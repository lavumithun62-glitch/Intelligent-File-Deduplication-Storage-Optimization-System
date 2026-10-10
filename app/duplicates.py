
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FileRecord, User
from app.security import get_current_user

router = APIRouter(prefix="/api/duplicates", tags=["Duplicates"])


@router.get("")
def get_duplicates(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    files = db.scalars(
        select(FileRecord)
        .where(
            FileRecord.user_id == user.id,
            FileRecord.status == "ready",
            FileRecord.sha256.is_not(None),
        )
        .order_by(FileRecord.created_at, FileRecord.id)
    ).all()

    groups = {}

    for file in files:
        groups.setdefault(file.sha256, []).append(file)

    results = []

    for digest, group in groups.items():
        if len(group) < 2:
            continue

        original = group[0]
        duplicate_files = group[1:]

        total_size = sum(file.size_bytes for file in group)
        potential_savings = sum(file.size_bytes for file in duplicate_files)

        results.append(
            {
                "sha256": digest,
                "file_count": len(group),
                "total_size_bytes": total_size,
                "potential_savings_bytes": potential_savings,
                "original_file": {
                    "id": original.id,
                    "name": original.original_name,
                    "size_bytes": original.size_bytes,
                    "created_at": original.created_at,
                },
                "duplicate_files": [
                    {
                        "id": file.id,
                        "name": file.original_name,
                        "size_bytes": file.size_bytes,
                        "created_at": file.created_at,
                    }
                    for file in duplicate_files
                ],
            }
        )

    return results
