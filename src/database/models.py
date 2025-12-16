from sqlalchemy import String, Boolean, DateTime, Integer, UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
import uuid

class Base(DeclarativeBase):
    """
    Base class for all the Database models
    """
    pass


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    first_name: str
    last_name: str
    hashed_password: Optional[tuple[str]]
    phone_number: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    last_login_at: str
    created_at: str
    updated_at: str


class Users(Base):
    """User model for authentication and user management"""
    
    __tablename__ = "users"
    
    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Authentication fields
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False, deferred=True)
    # The deferred argument prevents the password from being loaded into memory unless
    # specified explicitly (for added security)
   
    # Profile fields
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Account status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Login tracking
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    login_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    deleted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)  # Soft delete
    
    # Relationships
    # appointments = relationship("Appointments", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.first_name})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def verify_email(self):
        """Mark email as verified"""
        self.is_verified = True
    
    def record_login(self):
        """Record successful login"""
        self.last_login_at = datetime.now(timezone.utc)
        self.login_count += 1
    
    def soft_delete(self):
        """Soft delete the user"""
        self.deleted_at = datetime.now(timezone.utc)
        self.is_active = False
    
    def dict(self, exclude_sensitive: bool = True) -> UserResponse:
        """Convert model to dictionary"""
        data: UserResponse = UserResponse(
            id=self.id,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name or "",
            hashed_password=None,
            phone_number=self.phone_number,
            is_active=self.is_active,
            is_verified=self.is_verified,
            is_superuser=self.is_superuser,
            last_login_at=self.last_login_at.strftime("%Y-%m-%d %H:%M:%S") if self.last_login_at else "",
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_at=self.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
        
        if not exclude_sensitive:
            data.hashed_password = self.hashed_password,
        
        return data

