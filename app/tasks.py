```python
from pathlib import Path

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import FileRecord
from app.services import sha256_file, finalize_file


@celery_app.task(
    name="app.tasks.process_file",
    bind=True,
    max_retries=3,
    default_retry_delay=5,
)
def process_file(self, file_id: int, user_id: int, file_path: str):
    """
    Process an uploaded file:
    1. Verify that the stored file exists.
    2. Calculate its SHA-256 hash.
    3. Finalize its metadata and duplicate status.
    """

    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(
            f"Uploaded file does not exist: {path}"
        )

    db = SessionLocal()

    try:
        record = db.get(FileRecord, file_id)

        if record is None:
            raise ValueError(
                f"File record {file_id} does not exist"
            )

        if record.user_id != user_id:
            raise ValueError(
                "The file does not belong to the specified user"
            )

        digest = sha256_file(path)

        finalize_file(
            db=db,
            record=record,
            digest=digest,
            user_id=user_id,
        )

        return {
            "file_id": file_id,
            "status": "ready",
            "sha256": digest,
        }

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc)

    finally:
        db.close()
