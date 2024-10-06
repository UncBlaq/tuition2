from sqlalchemy import Column, DateTime, String, func, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID
from tuition.database import Base
import uuid


class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    full_name = Column(String(255), nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    role = Column(String, nullable=False, default='admin')
    is_super_admin = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())  # timezone-aware
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())  # timezone-aware

    last_login = Column(DateTime(timezone=True))
    failed_attempts = Column(Integer, default=0)
