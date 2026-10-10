
import json
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
    Query,
)
from fastapi.responses import FileResponse
from sqlalchemy import select, desc, func
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import (
    FileRecord,
    FileMetadata,
    User,
    DeletionHistory,
    AuditLog,
)
from app.security import get_current_user
from app.services import sha256_file, finalize_file


router = APIRouter(prefix="/api/files", tags=["Files"])

ALLOWED_EXTENSIONS = {
    ".txt", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".csv", ".json", ".doc", ".docx", ".xls", ".xlsx",
    ".zip", ".mp3", ".mp4", ".py", ".md",
}

CHUNK_SIZE = 1024 * 1024


def serialize_file(record: FileRecord) -> dict:
    return {
        "id": record.id,
        "user_id": record.user_id,
        "original_name": record.original_name,
        "content_type": record.content_type,
        "size_bytes": record.size_bytes,
        "sha256": record.sha256,
        "is_duplicate": record.is_duplicate,
        "protected": record.protected,
        "status": record.status,
        "created_at": record.created_at,
    }


def get_user_file(
    file_id: int,
    user: User,
    db: Session,
) -> FileRecord:
    record = db.scalar(
        select(FileRecord).where(
            FileRecord.id == file_id,
            FileRecord.user_id == user.id,
        )
    )

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    return record


# --------------------------------------------------
# UPLOAD
# --------------------------------------------------

@router.post("/upload", status_code=201)
async def upload_file(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    original_name = Path(file.filename or "upload.bin").name
    extension = Path(original_name).suffix.lower()

    if not original_name or extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="File extension is not allowed",
        )

    storage = Path(settings.storage_dir)
    storage.mkdir(parents=True, exist_ok=True)

    stored_name = uuid.uuid4().hex
    path = storage / stored_name
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    size = 0
    record = None

    try:
        with path.open("wb") as destination:
            while True:
                chunk = await file.read(CHUNK_SIZE)

                if not chunk:
                    break

                size += len(chunk)

                if size > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail="Upload exceeds configured size limit",
                    )

                destination.write(chunk)

        record = FileRecord(
            user_id=user.id,
            original_name=original_name[:255],
            stored_name=stored_name,
            content_type=(
                file.content_type or "application/octet-stream"
            ),
            size_bytes=size,
            status="processing",
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        # Save file metadata.
        metadata = FileMetadata(
            file_id=record.id,
            extension=extension,
            mime_type=record.content_type,
            file_size_bytes=size,
        )
        db.add(metadata)
        db.commit()

        # Calculate the hash and finalize processing.
        record = db.get(FileRecord, record.id)

        if record is None:
            raise RuntimeError(
                "Uploaded file record was not found"
            )

        digest = sha256_file(path)

        record = finalize_file(
            db=db,
            record=record,
            digest=digest,
            user_id=user.id,
        )

        db.refresh(record)
        return serialize_file(record)

    except HTTPException:
        db.rollback()
        path.unlink(missing_ok=True)
        raise

    except Exception:
        db.rollback()

        # Remove the database record created by this failed upload.
        if record is not None:
            try:
                failed_record = db.get(FileRecord, record.id)

                if failed_record is not None:
                    db.delete(failed_record)
                    db.commit()

            except Exception:
                db.rollback()

        path.unlink(missing_ok=True)
        raise

    finally:
        await file.close()


# --------------------------------------------------
# LIST, SEARCH, FILTER, SORT, PAGINATE
# --------------------------------------------------

@router.get("")
def list_files(
    q: str | None = None,
    file_type: str | None = None,
    min_size: int | None = Query(None, ge=0),
    max_size: int | None = Query(None, ge=0),
    duplicates_only: bool = False,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort_by: str = "created_at",
    order: str = "desc",
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if min_size is not None and max_size is not None:
        if min_size > max_size:
            raise HTTPException(
                status_code=400,
                detail="min_size cannot exceed max_size",
            )

    if order.lower() not in {"asc", "desc"}:
        raise HTTPException(
            status_code=400,
            detail="order must be asc or desc",
        )

    statement = select(FileRecord).where(
        FileRecord.user_id == user.id
    )

    if q:
        statement = statement.where(
            FileRecord.original_name.ilike(f"%{q[:200]}%")
        )

    if file_type:
        extension = file_type.lstrip(".").lower()
        statement = statement.where(
            func.lower(FileRecord.original_name).like(
                f"%.{extension}"
            )
        )

    if min_size is not None:
        statement = statement.where(
            FileRecord.size_bytes >= min_size
        )

    if max_size is not None:
        statement = statement.where(
            FileRecord.size_bytes <= max_size
        )

    if duplicates_only:
        statement = statement.where(
            FileRecord.is_duplicate.is_(True)
        )

    if date_from:
        statement = statement.where(
            FileRecord.created_at >= date_from
        )

    if date_to:
        statement = statement.where(
            FileRecord.created_at <= date_to
        )

    columns = {
        "created_at": FileRecord.created_at,
        "size_bytes": FileRecord.size_bytes,
        "original_name": FileRecord.original_name,
    }

    if sort_by not in columns:
        raise HTTPException(
            status_code=400,
            detail=(
                "sort_by must be created_at, size_bytes, "
                "or original_name"
            ),
        )

    column = columns[sort_by]
    statement = statement.order_by(
        column.asc()
        if order.lower() == "asc"
        else desc(column)
    )

    records = db.scalars(
        statement.offset((page - 1) * page_size).limit(page_size)
    ).all()

    return [serialize_file(record) for record in records]


# --------------------------------------------------
# DOWNLOAD
# --------------------------------------------------

@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = get_user_file(file_id, user, db)
    path = Path(settings.storage_dir) / record.stored_name

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Stored file missing; upload the file again",
        )

    return FileResponse(
        path=str(path),
        filename=record.original_name,
        media_type=record.content_type,
    )


# --------------------------------------------------
# SAFE DELETE PREVIEW
# --------------------------------------------------

@router.get("/{file_id}/delete-preview")
def preview_delete(
    file_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = get_user_file(file_id, user, db)

    protected = (
        record.protected
        or file_id in settings.protected_ids
    )

    return {
        "file_id": record.id,
        "file_name": record.original_name,
        "size_bytes": record.size_bytes,
        "potential_storage_impact_bytes": record.size_bytes,
        "protected": protected,
        "can_delete": not protected,
    }


# --------------------------------------------------
# DELETE WITH HISTORY
# --------------------------------------------------

@router.delete("/{file_id}")
def delete_file(
    file_id: int,
    confirm: bool = Query(False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = get_user_file(file_id, user, db)

    if not confirm:
        raise HTTPException(
            status_code=400,
            detail="Review delete-preview then pass confirm=true",
        )

    if record.protected or file_id in settings.protected_ids:
        raise HTTPException(
            status_code=403,
            detail="File is protected",
        )

    path = Path(settings.storage_dir) / record.stored_name
    size = record.size_bytes

    try:
        db.add(
            DeletionHistory(
                user_id=user.id,
                file_id=record.id,
                original_name=record.original_name,
                size_bytes=size,
                sha256=record.sha256,
            )
        )

        # AuditLog.details is Text, so store JSON as a string.
        db.add(
            AuditLog(
                user_id=user.id,
                action="delete",
                entity_type="file",
                entity_id=record.id,
                details=json.dumps({"size_bytes": size}),
            )
        )

        db.delete(record)
        db.commit()

    except Exception:
        db.rollback()
        raise

    # Remove the physical file only after the database transaction succeeds.
    path.unlink(missing_ok=True)

    return {
        "message": "File deleted",
        "storage_released_bytes": size,
    }
