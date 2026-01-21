from .base import Base
from sqlalchemy import String, Boolean, DateTime, BigInteger, Index, Text, Integer, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from .response_models import (
    UserResponse, TempUser, TenantResponse
)

from typing import List, TYPE_CHECKING
if TYPE_CHECKING:
    from .tenants import Patient


# ------- DATABASE MODELS -------

class User(Base):
    """User model for authentication and user management"""

    __tablename__ = "users"

    # Primary key for user id
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # user credentials
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    hospital_id: Mapped[int | None] = mapped_column(BigInteger)
    doctor_id: Mapped[int | None] = mapped_column(BigInteger)
    patient_id: Mapped[int | None] = mapped_column(BigInteger)

    # user status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    phone_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    # user activity records
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )

    # realtionships
    registered_patients: Mapped[List["Patient"]] = relationship(
        "Patient", 
        back_populates="creator"
    )

    __table_args__ = (
        Index("idx_email", "email"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_role", "role"),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.first_name})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    
    def record_login(self):
        """Record successful login"""
        self.last_login = datetime.now(timezone.utc)
    
    def soft_delete(self):
        """Soft delete the user"""
        self.is_active = False
    
    def to_response(self, exclude_sensitive: bool = True) -> UserResponse:
        """Convert model to dictionary and parse the datetimes into human readable"""
        data: UserResponse = UserResponse.model_validate(self)
        
        if exclude_sensitive:
            data.password = None
        
        return data

class PotentialUsers(Base):
    """ Potential User table that are not yet verified """
    __tablename__ = "potential_users"

    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, primary_key=True)
    phone_number: Mapped[str | None] = mapped_column(String(20), nullable=False)
    otp: Mapped[str] = mapped_column(String(4), nullable=False)
    otp_exp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    
    # Account status
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    __table_args__ = (
        Index("ix_potential_email", "email"),
        UniqueConstraint("otp", "otp_exp", "phone_number", name="unique_otp_per_user")
    )

    def mark_verified(self) -> None:
        self.is_verified = True

    def to_response(self) -> TempUser:
        return TempUser.model_validate(self)
    
class Tenant(Base):
    """
        Tenants are the customers that will use the services of the application
        Each tenant has its own database. This table has all the tenants registered on the
        Healtheze application
    """

    __tablename__ = "tenants"

    # primary key id
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    tenant_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # tenant details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    subdomain: Mapped[str] = mapped_column(String(100), unique=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str] = mapped_column(String(20))

    # location details
    address: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    zip_code: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(100), default="INDIA")
    
    # subscription
    subscription_plan: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")
    subscription_start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    subscription_end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    # database details
    database_name: Mapped[str] = mapped_column(String(100), nullable=False)
    max_users: Mapped[int] = mapped_column(Integer, default=100)
    max_patients: Mapped[int] = mapped_column(Integer, default=10000)
    max_doctors: Mapped[int] = mapped_column(Integer, default=50)

    # tenant status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    created_by: Mapped[str] = mapped_column(String(100))

    __table_args__ = (
        Index("idx_tenant_code", "tenant_code"),
        Index("idx_subdomain", "subdomain"),
        Index("idx_status", "status")
    )

    def to_response(self) -> TenantResponse: 
        return TenantResponse.model_validate(self)
    
    def change_subscription(self, subscription: str) -> None:
        self.subscription_plan = subscription
    
    def deactivate(self) -> None:
        self.is_active = False
    