from pydantic import BaseModel, EmailStr, StringConstraints, Field, NonNegativeInt
from typing import Annotated, Optional, Literal
from decimal import Decimal
from datetime import date

class AppointmentFilter(BaseModel):
    status: Literal["cancelled", "upcoming", "completed"] | None = None
    doctor_id: Optional[int] = None
    patient_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None

class HospitalForm(BaseModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]
    type: Optional[str]
    description: Optional[str]

    # address
    address: str
    city: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
    state: Annotated[str, StringConstraints(strip_whitespace=True, max_length=100)]
    zip_code: Annotated[str, StringConstraints(strip_whitespace=True, max_length=20)]
    country: Optional[str] = "INDIA"

    # contact details
    phone_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]
    email: EmailStr
    website: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^https?:\/\/(?:www\.)?")]
    emergency_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]
    total_beds: int
    available_beds: int
    is24x7: bool = False

    latitude: Annotated[Decimal, Field(ge=-90, le=90, max_digits=10, decimal_places=8)]
    longitude: Annotated[Decimal, Field(ge=-180, le=180, max_digits=11, decimal_places=8)]

    logo_url: Optional[str]
    license_number: str
    accreditation: str
    established_year: int

    
class HospitalUpdateForm(BaseModel):
    name: Optional[Annotated[str, StringConstraints(strip_whitespace=True, max_length=255)]]
    type: Optional[str]
    description: Optional[str]

    # contact details
    phone_number: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]]
    email: Optional[EmailStr]
    website: Optional[Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^https?:\/\/(?:www\.)?")]]
    emergency_number: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]]
    
    total_beds: Optional[int]
    available_beds: Optional[int]

    logo_url: Optional[str]

class Location(BaseModel):
    latitude: Annotated[Decimal, Field(ge=-90, le=90, max_digits=10, decimal_places=8)]
    longitude: Annotated[Decimal, Field(ge=-180, le=180, max_digits=11, decimal_places=8)]
    radius_km: NonNegativeInt


