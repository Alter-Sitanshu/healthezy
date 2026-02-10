from pydantic import BaseModel, EmailStr, Field, field_validator, ValidationInfo
from datetime import datetime
from typing import Optional

class TenantCreate(BaseModel):
    """
    Pydantic model for validating input when creating a new Tenant.
    """

    # --- Identity Details ---
    name: str = Field(..., max_length=255, description="Full name of the tenant/hospital")
    # tenant_code: str = Field(..., max_length=50, description="Unique code identifier")
    subdomain: str = Field(..., max_length=100, description="Unique subdomain for the tenant")
    description: Optional[str] = None

    # --- Contact Details ---
    # Using EmailStr for validation and explicit max lengths
    contact_email: EmailStr = Field(..., max_length=255)
    contact_phone: str = Field(..., max_length=20)

    # --- Location Details ---
    address: str
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    zip_code: str = Field(..., max_length=20)
    country: str = Field(default="INDIA", max_length=100)

    # --- Subscription Details ---
    subscription_plan: str = Field(..., max_length=50)
    subscription_start_date: datetime
    subscription_end_date: datetime
    
    status: str = Field(default="ACTIVE", max_length=50)
    is_active: bool = True

    # --- Database & Config ---
    # Database name is required in DB
    database_name: str = Field(..., max_length=100)
    
    max_users: int = Field(default=100, ge=1)
    max_patients: int = Field(default=10000, ge=1)
    max_doctors: int = Field(default=50, ge=1)

    # --- Validators ---
    @field_validator('subscription_end_date')
    @classmethod
    def validate_dates(cls, v: datetime, info: ValidationInfo):
        # Ensure end date is after start date
        if 'subscription_start_date' in info.data:
            start_date = info.data['subscription_start_date']
            if v <= start_date:
                raise ValueError('subscription_end_date must be after subscription_start_date')
        return v