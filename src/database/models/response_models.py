from pydantic import BaseModel, EmailStr, ConfigDict, Field
from typing import Optional, Annotated
from datetime import datetime, time, date
from decimal import Decimal

class BaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra='ignore')


class TempUser(BaseResponse):
    email: str
    phone_number: str
    is_verified: bool = False
    otp: str
    otp_exp: datetime

class UserResponse(BaseResponse):
    id: int
    # tenant_id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str
    role: str
    is_superuser: bool = False
    # Password is included but Optional so it can be hidden
    password: Optional[str] = None
    
    # Linked Entity IDs (Nullable)
    hospital_id: Optional[int] = None

    # Status Flags
    is_active: bool
    email_verified: bool
    phone_verified: bool

    # Activity & Timestamps
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class TenantResponse(BaseResponse):
    id: int
    tenant_code: str

    # tenant details
    name: str
    description: Optional[str]
    subdomain: str
    contact_email: str
    contact_phone: Optional[str]

    # location details
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    
    # subscription
    subscription_plan: str
    status: str
    subscription_start_date: Optional[datetime]
    subscription_end_date: Optional[datetime]

    # database details
    database_name: str
    max_users: int
    max_patients: int
    max_doctors: int

    # tenant status
    is_active: bool
    created_at: str
    updated_at: str
    created_by: str


class PatientResponse(BaseResponse):
    id: int
    patient_code: str

    # patient details
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    full_name: str

    email: Optional[EmailStr] = None
    phone_number: str
    date_of_birth: date
    age: Optional[int] = None
    gender: str
    blood_group: Optional[str] = None

    # location
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

    # emergency contact
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    emergency_contact_relation: Optional[str] = None

    # miscellaneous
    occupation: Optional[str] = None
    marital_status: Optional[str] = None
    nationality: Optional[str] = None
    language_preference: Optional[str] = None
    photo_url: Optional[str] = None

    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    chronic_conditions: Optional[str] = None
    current_medications: Optional[str] = None

    # insurance
    insurance_provider: Optional[str] = None
    insurance_policy_number: Optional[str] = None
    insurance_expiry_date: Optional[date] = None

    # tenant_id: int

    # audit
    created_at: datetime
    created_by: int
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

# -------------------------------------------------------------------
# Department Response
# -------------------------------------------------------------------
class DepartmentResponse(BaseResponse):
    id: int
    department_code: str
    name: str
    description: Optional[str] = None
    head_of_department: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    floor_number: Optional[int] = None
    building: Optional[str] = None
    is_active: bool
    # tenant_id: int

# -------------------------------------------------------------------
# Doctor Responses (including nested schedule models)
# -------------------------------------------------------------------
class DoctorScheduleResp(BaseResponse):
    id: int
    doctor_id: int
    day_of_week: str
    start_time: time
    end_time: time
    slot_duration: int
    max_patients_per_slot: int
    buffer_time_minutes: int
    hospital_id: Optional[int] = None
    is_available: bool

class DoctorScheduleExpResp(BaseResponse):
    id: int
    doctor_id: int
    exception_date: date
    is_available: bool
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: Optional[str] = None

class DoctorResponse(BaseResponse):
    id: int
    doctor_code: str
    password: Optional[str] = None
    first_login: bool = False
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    full_name: str  # Generated from @property
    email: EmailStr
    phone_number: str
    gender: str
    specialization: str
    qualification: str
    registration_number: str
    experience_years: int
    consultation_fee: Annotated[
        Decimal, 
        Field(max_digits=10, decimal_places=2, ge=0)
    ]
    bio: Optional[str] = None
    address: Optional[str] = None
    photo_url: Optional[str] = None
    department_id: Optional[int] = None
    hospital_id: Optional[int] = None
    status: str
    # tenant_id: int

# -------------------------------------------------------------------
# Hospital Response
# -------------------------------------------------------------------
class HospitalResponse(BaseResponse):
    id: int
    hospital_code: str
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    address: str
    city: str
    state: str
    zip_code: str
    country: str
    phone_number: str
    email: EmailStr
    website: Optional[str] = None
    emergency_number: str
    total_beds: int
    available_beds: int
    latitude: Annotated[Decimal, Field(ge=-90, le=90, max_digits=10, decimal_places=8)]
    longitude: Annotated[Decimal, Field(ge=-180, le=180, max_digits=11, decimal_places=8)]
    logo_url: Optional[str] = None
    license_number: Optional[str] = None
    accreditation: Optional[str] = None
    established_year: int
    is_active: bool
    is24x7: bool
    # tenant_id: int

# -------------------------------------------------------------------
# Appointment Response
# -------------------------------------------------------------------
class AppointmentResponse(BaseResponse):
    id: int
    appointment_number: str
    patient_id: int
    doctor_id: Optional[int] = None
    hospital_id: Optional[int] = None
    department_id: Optional[int] = None
    appointment_date: date
    appointment_time: time
    duration_minutes: int
    visit_type: str
    booking_type: str
    status: str
    appointment_mode: str
    reason_for_visit: Optional[str] = None
    notes: Optional[str] = None
    token_number: int
    
    # Timestamps for tracking flow
    checked_in_at: Optional[datetime] = None
    checked_out_at: Optional[datetime] = None
    consultation_started_at: Optional[datetime] = None
    consultation_ended_at: Optional[datetime] = None
    
    created_at: datetime
    # tenant_id: int