
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FileRecord, User
from app.security import get_current_user

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("")
def get_analytics(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    files = db.scalars(
        select(FileRecord).where(FileRecord.user_id == user.id)
    ).all()

    groups = {}
    for file in files:
        if file.sha256 and file.status == "ready":
            groups.setdefault(file.sha256, []).append(file)

    duplicate_files = [
        file for file in files
        if file.is_duplicate and file.status == "ready"
    ]

    potential_savings = sum(
        sum(file.size_bytes for file in group[1:])
        for group in groups.values()
        if len(group) > 1
    )

    largest_files = sorted(
        files,
        key=lambda file: file.size_bytes,
        reverse=True,
    )[:5]

    recent_uploads = sorted(
        files,
        key=lambda file: file.created_at,
        reverse=True,
    )[:5]

    return {
        "total_files": len(files),
        "total_storage_bytes": sum(file.size_bytes for file in files),
        "duplicate_files": len(duplicate_files),
        "duplicate_storage_bytes": sum(
            file.size_bytes for file in duplicate_files
        ),
        "potential_storage_savings_bytes": potential_savings,
        "largest_files": [
            {
                "id": file.id,
                "name": file.original_name,
                "size_bytes": file.size_bytes,
            }
            for file in largest_files
        ],
        "recent_uploads": [
            {
                "id": file.id,
                "name": file.original_name,
                "size_bytes": file.size_bytes,
                "created_at": file.created_at,
                "status": file.status,
            }
            for file in recent_uploads
        ],
    }
