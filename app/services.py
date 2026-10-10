import hashlib
import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    FileRecord,
    FileHash,
    DuplicateGroup,
    AuditLog,
)


def sha256_file(path: str | Path) -> str:
    """Calculate the SHA-256 hash of a file."""
    digest = hashlib.sha256()

    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def finalize_file(
    db: Session,
    record: FileRecord,
    digest: str,
    user_id: int,
) -> FileRecord:
    """Finalize file processing and update duplicate information."""
    try:
        record.sha256 = digest
        record.status = "ready"

        existing = db.scalar(
            select(FileRecord).where(
                FileRecord.user_id == user_id,
                FileRecord.sha256 == digest,
                FileRecord.id != record.id,
                FileRecord.status == "ready",
            ).limit(1)
        )

        record.is_duplicate = existing is not None

        hash_record = db.scalar(
            select(FileHash).where(
                FileHash.file_id == record.id
            )
        )

        if hash_record is None:
            db.add(
                FileHash(
                    file_id=record.id,
                    sha256=digest,
                )
            )
        else:
            hash_record.sha256 = digest

        matching_files = db.scalars(
            select(FileRecord).where(
                FileRecord.user_id == user_id,
                FileRecord.sha256 == digest,
                FileRecord.status == "ready",
            )
        ).all()

        if len(matching_files) > 1:
            group = db.scalar(
                select(DuplicateGroup).where(
                    DuplicateGroup.user_id == user_id,
                    DuplicateGroup.sha256 == digest,
                )
            )

            total_size = sum(
                item.size_bytes for item in matching_files
            )
            largest_size = max(
                item.size_bytes for item in matching_files
            )
            savings = total_size - largest_size

            if group is None:
                db.add(
                    DuplicateGroup(
                        user_id=user_id,
                        sha256=digest,
                        file_count=len(matching_files),
                        total_size_bytes=total_size,
                        potential_savings_bytes=savings,
                    )
                )
            else:
                group.file_count = len(matching_files)
                group.total_size_bytes = total_size
                group.potential_savings_bytes = savings

        db.add(
            AuditLog(
                user_id=user_id,
                action="file_processed",
                entity_type="file",
                entity_id=record.id,
                details=json.dumps({
                    "message": "SHA-256 calculated",
                    "sha256": digest,
                }),
            )
        )

        db.commit()
        db.refresh(record)
        return record

    except Exception:
        db.rollback()
        raise