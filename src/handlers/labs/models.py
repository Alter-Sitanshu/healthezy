from pydantic import (
    BaseModel, StringConstraints, EmailStr, 
    HttpUrl, Field, NonNegativeInt
)
from typing import Annotated, Optional, Literal
from datetime import time
from decimal import Decimal


class Location(BaseModel):
    latitude: Annotated[Decimal, Field(ge=-90, le=90, max_digits=10, decimal_places=8)]
    longitude: Annotated[Decimal, Field(ge=-180, le=180, max_digits=11, decimal_places=8)]
    radius_km: NonNegativeInt

class NewLab(BaseModel):
    name: str
    type: Annotated[str, StringConstraints(max_length=100, strip_whitespace=True)]
    description: Optional[str]

    # Address
    address: str
    city: str
    state: Annotated[str, StringConstraints(max_length=50, min_length=3)]
    zip_code: Annotated[str, StringConstraints(max_length=20, pattern=r"^\d{6,20}$")]
    country: str = "INDIA"

    # Contact information
    phone_number: Annotated[str, StringConstraints(pattern=r"^\+?\d{10,15}$")]
    email: EmailStr
    website: Optional[HttpUrl]

    # Operating hours
    is24x7: bool
    opening_time: Optional[time]
    closing_time: Optional[time]

    # Hospital association
    hospital_id: Optional[int]

    # License & credentials
    license_number: Optional[str]
    accreditation: Optional[str]
    established_year: int

    # Geographic coordinates
    latitude: Annotated[Decimal, Field(ge=-90, le=90, max_digits=10, decimal_places=8)]
    longitude: Annotated[Decimal, Field(ge=-180, le=180, max_digits=11, decimal_places=8)]

class LabUpdates(BaseModel):
    """Model for updating lab details - fields optional"""
    name: Optional[str] = None
    type: Optional[Annotated[str, StringConstraints(max_length=100, strip_whitespace=True)]] = None
    description: Optional[str] = None

    # Address
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[Annotated[str, StringConstraints(max_length=50, min_length=3)]] = None
    zip_code: Optional[Annotated[str, StringConstraints(max_length=20, pattern=r"^\d{6,20}$")]] = None
    country: Optional[str] = None

    # Contact information
    phone_number: Optional[Annotated[str, StringConstraints(pattern=r"^\+?\d{10,15}$")]] = None
    email: Optional[EmailStr] = None
    website: Optional[HttpUrl] = None

    # Operating hours
    is24x7: Optional[bool] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None

    # Hospital association
    hospital_id: Optional[int] = None
    
class NewLabTest(BaseModel):
    name: str
    description: Optional[str]
    
    # Test categorization
    category: Annotated[Literal["Blood", "Urine", "Imaging"], StringConstraints(max_length=100, strip_whitespace=True)]
    
    # Test specifications
    turnaround_time_hours: Annotated[int, Field(ge=0)]
    sample_type: Literal["blood", "urine", "saliva", "stool"] | None
    
    # Pricing
    test_price: Annotated[Decimal, Field(ge=0.0)]
    
    # Reference values
    normal_range: Optional[str] # example 11.5-13.5
    unit_of_measurement: Optional[str] # e.g. 10^3/uL
