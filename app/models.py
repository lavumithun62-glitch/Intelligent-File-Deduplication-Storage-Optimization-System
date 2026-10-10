from datetime import datetime, timezone
from sqlalchemy import String, Integer, BigInteger, DateTime, ForeignKey, Boolean, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
def now_utc(): return datetime.now(timezone.utc).replace(tzinfo=None)
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    email: Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now_utc)
class FileRecord(Base):
    __tablename__="files"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    original_name: Mapped[str]=mapped_column(String(255))
    stored_name: Mapped[str]=mapped_column(String(255),unique=True)
    content_type: Mapped[str]=mapped_column(String(255),default="application/octet-stream")
    size_bytes: Mapped[int]=mapped_column(BigInteger,default=0)
    sha256: Mapped[str|None]=mapped_column(String(64),index=True,nullable=True)
    is_duplicate: Mapped[bool]=mapped_column(Boolean,default=False)
    protected: Mapped[bool]=mapped_column(Boolean,default=False)
    status: Mapped[str]=mapped_column(String(30),default="processing")
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now_utc)
class FileHash(Base):
    __tablename__="file_hashes"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    file_id: Mapped[int]=mapped_column(ForeignKey("files.id",ondelete="CASCADE"),unique=True)
    sha256: Mapped[str]=mapped_column(String(64),index=True)
    created_at: Mapped[datetime]=mapped_column(DateTime,default=now_utc)
class DuplicateGroup(Base):
    __tablename__="duplicate_groups"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id: Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    sha256: Mapped[str]=mapped_column(String(64),index=True)
    file_count: Mapped[int]=mapped_column(Integer,default=2)
    total_size_bytes: Mapped[int]=mapped_column(BigInteger,default=0)
    potential_savings_bytes: Mapped[int]=mapped_column(BigInteger,default=0)
    updated_at: Mapped[datetime]=mapped_column(DateTime,default=now_utc)
    __table_args__=(UniqueConstraint("user_id","sha256",name="uq_duplicate_group_user_hash"),)
class FileMetadata(Base):
    __tablename__="file_metadata"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    file_id: Mapped[int]=mapped_column(ForeignKey("files.id",ondelete="CASCADE"),unique=True)
    extension: Mapped[str]=mapped_column(String(30),default="")
    mime_type: Mapped[str]=mapped_column(String(255),default="application/octet-stream")
    file_size_bytes: Mapped[int]=mapped_column(BigInteger,default=0)
class DeletionHistory(Base):
    __tablename__="deletion_history"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id: Mapped[int]=mapped_column(Integer,index=True)
    file_id: Mapped[int]=mapped_column(Integer)
    original_name: Mapped[str]=mapped_column(String(255))
    size_bytes: Mapped[int]=mapped_column(BigInteger)
    sha256: Mapped[str|None]=mapped_column(String(64),nullable=True)
    deleted_at: Mapped[datetime]=mapped_column(DateTime,default=now_utc)
class AuditLog(Base):
    __tablename__="audit_logs"
    id: Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id: Mapped[int]=mapped_column(Integer,index=True)
    action: Mapped[str]=mapped_column(String(100))
    entity_type: Mapped[str]=mapped_column(String(100))
    entity_id: Mapped[int|None]=mapped_column(Integer,nullable=True)
    details: Mapped[str]=mapped_column(Text,default="")
