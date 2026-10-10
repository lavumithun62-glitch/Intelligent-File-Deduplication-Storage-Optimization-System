
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DuplicateGroup, User
from app.security import get_current_user

router = APIRouter(
    prefix="/api/duplicate-groups",
    tags=["Duplicate Groups"],
)


@router.get("")
def list_duplicate_groups(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    groups = db.scalars(
        select(DuplicateGroup)
        .where(DuplicateGroup.user_id == user.id)
        .order_by(DuplicateGroup.updated_at.desc())
    ).all()

    return [
        {
            "id": group.id,
            "user_id": group.user_id,
            "sha256": group.sha256,
            "file_count": group.file_count,
            "total_size_bytes": group.total_size_bytes,
            "potential_savings_bytes": group.potential_savings_bytes,
            "updated_at": group.updated_at,
        }
        for group in groups
    ]
