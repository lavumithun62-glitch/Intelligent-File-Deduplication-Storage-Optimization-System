
from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    User,
    FileRecord,
    FileHash,
    DuplicateGroup,
    FileMetadata,
    DeletionHistory,
    AuditLog,
)
from app.security import get_current_user
from app.auth import router as auth_router
from app.files import router as files_router


# Main router
router = APIRouter()

# Authentication routes
router.include_router(auth_router)

# File upload, listing, download, and deletion routes
router.include_router(files_router)


# --------------------------------------------------
# USERS
# --------------------------------------------------

@router.get("/api/users", tags=["Users"])
def list_users(
    user: User = Depends(get_current_user),
):
    return [
        {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at,
        }
    ]


# --------------------------------------------------
# FILE HASHES
# --------------------------------------------------

@router.get("/api/file-hashes", tags=["File Hashes"])
def list_file_hashes(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(FileHash)
        .join(FileRecord, FileHash.file_id == FileRecord.id)
        .where(FileRecord.user_id == user.id)
        .order_by(desc(FileHash.created_at))
    ).all()

    return [
        {
            "id": item.id,
            "file_id": item.file_id,
            "sha256": item.sha256,
            "created_at": item.created_at,
        }
        for item in records
    ]


# --------------------------------------------------
# DUPLICATES
# --------------------------------------------------

@router.get("/api/duplicates", tags=["Duplicates"])
def list_duplicates(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(FileRecord).where(
            FileRecord.user_id == user.id,
            FileRecord.status == "ready",
            FileRecord.sha256.is_not(None),
        )
    ).all()

    groups = defaultdict(list)

    for item in records:
        groups[item.sha256].append(item)

    result = []

    for sha256, items in groups.items():
        if len(items) < 2:
            continue

        total_size = sum(item.size_bytes for item in items)
        original_size = min(item.size_bytes for item in items)

        result.append(
            {
                "sha256": sha256,
                "file_count": len(items),
                "total_size_bytes": total_size,
                "potential_savings_bytes": total_size - original_size,
                "files": [
                    {
                        "id": item.id,
                        "original_name": item.original_name,
                        "size_bytes": item.size_bytes,
                        "sha256": item.sha256,
                        "status": item.status,
                    }
                    for item in items
                ],
            }
        )

    return result


# --------------------------------------------------
# DUPLICATE GROUPS
# --------------------------------------------------

@router.get("/api/duplicate-groups", tags=["Duplicate Groups"])
def list_duplicate_groups(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(DuplicateGroup)
        .where(DuplicateGroup.user_id == user.id)
        .order_by(desc(DuplicateGroup.updated_at))
    ).all()

    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "sha256": item.sha256,
            "file_count": item.file_count,
            "total_size_bytes": item.total_size_bytes,
            "potential_savings_bytes": item.potential_savings_bytes,
            "updated_at": item.updated_at,
        }
        for item in records
    ]


# --------------------------------------------------
# FILE METADATA
# --------------------------------------------------

@router.get("/api/file-metadata", tags=["File Metadata"])
def list_file_metadata(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(FileMetadata)
        .join(FileRecord, FileMetadata.file_id == FileRecord.id)
        .where(FileRecord.user_id == user.id)
        .order_by(desc(FileMetadata.id))
    ).all()

    return [
        {
            "id": item.id,
            "file_id": item.file_id,
            "extension": item.extension,
            "mime_type": item.mime_type,
            "file_size_bytes": item.file_size_bytes,
        }
        for item in records
    ]


# --------------------------------------------------
# DELETION HISTORY
# --------------------------------------------------

@router.get("/api/deletions", tags=["Deletion History"])
def list_deletions(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(DeletionHistory)
        .where(DeletionHistory.user_id == user.id)
        .order_by(desc(DeletionHistory.deleted_at))
    ).all()

    return [
        {
            "id": item.id,
            "file_id": item.file_id,
            "original_name": item.original_name,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
            "deleted_at": item.deleted_at,
        }
        for item in records
    ]


# --------------------------------------------------
# AUDIT LOGS
# --------------------------------------------------

@router.get("/api/audit-logs", tags=["Audit Logs"])
def list_audit_logs(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(AuditLog)
        .where(AuditLog.user_id == user.id)
        .order_by(desc(AuditLog.id))
        .limit(200)
    ).all()

    return [
        {
            "id": item.id,
            "user_id": item.user_id,
            "action": item.action,
            "entity_type": item.entity_type,
            "entity_id": item.entity_id,
            "details": item.details,
        }
        for item in records
    ]


# --------------------------------------------------
# STORAGE ANALYTICS
# --------------------------------------------------

@router.get("/api/analytics", tags=["Analytics"])
def analytics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(FileRecord).where(FileRecord.user_id == user.id)
    ).all()

    groups = defaultdict(list)

    for item in records:
        if item.status == "ready" and item.sha256:
            groups[item.sha256].append(item)

    duplicate_groups = [
        items for items in groups.values()
        if len(items) > 1
    ]

    duplicate_files = sum(
        len(items) for items in duplicate_groups
    )

    duplicate_storage = sum(
        sum(item.size_bytes for item in items)
        for items in duplicate_groups
    )

    potential_savings = sum(
        sum(item.size_bytes for item in items)
        - min(item.size_bytes for item in items)
        for items in duplicate_groups
    )

    largest_files = sorted(
        records,
        key=lambda item: item.size_bytes,
        reverse=True,
    )[:5]

    recent_uploads = sorted(
        records,
        key=lambda item: item.created_at,
        reverse=True,
    )[:5]

    def serialize_file(item: FileRecord) -> dict:
        return {
            "id": item.id,
            "original_name": item.original_name,
            "size_bytes": item.size_bytes,
            "sha256": item.sha256,
            "is_duplicate": item.is_duplicate,
            "status": item.status,
            "created_at": item.created_at,
        }

    return {
        "total_files": len(records),
        "storage_used": sum(item.size_bytes for item in records),
        "duplicate_files": duplicate_files,
        "duplicate_storage": duplicate_storage,
        "potential_savings": potential_savings,
        "largest_files": [
            serialize_file(item) for item in largest_files
        ],
        "recent_uploads": [
            serialize_file(item) for item in recent_uploads
        ],
    }
