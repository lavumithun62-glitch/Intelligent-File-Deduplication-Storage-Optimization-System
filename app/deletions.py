
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DeletionHistory, User
from app.security import get_current_user

router = APIRouter(prefix="/api/deletions", tags=["Deletion History"])


@router.get("")
def get_deletion_history(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.scalars(
        select(DeletionHistory)
        .where(DeletionHistory.user_id == user.id)
        .order_by(desc(DeletionHistory.deleted_at))
        .limit(100)
    ).all()

    return [
        {
            "id": record.id,
            "file_id": record.file_id,
            "original_name": record.original_name,
            "size_bytes": record.size_bytes,
            "sha256": record.sha256,
            "deleted_at": record.deleted_at,
        }
        for record in records
    ]
