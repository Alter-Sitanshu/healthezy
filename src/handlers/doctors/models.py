from pydantic import (
    BaseModel, StringConstraints, EmailStr, NonNegativeInt,
    Field, field_validator, ValidationInfo, ValidationError
)
from typing import Annotated, Literal, Optional
from decimal import Decimal
from datetime import time, date, datetime, timezone

class NewDoctorForm(BaseModel):
    first_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]
    middle_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)] | None
    last_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)]

    email: EmailStr
    phone_number: Annotated[str, StringConstraints(max_length=20, strip_whitespace=True, pattern=r"^\+?\d{10,15}$")]
    gender: Annotated[Literal["male", "female", "other"], StringConstraints(to_lower=True, max_length=20)]

    specialization: Annotated[str, StringConstraints(max_length=200, strip_whitespace=True)]
    qualification: Annotated[str, StringConstraints(max_length=500)]
    registration_number: Annotated[str, StringConstraints(max_length=100)]
    experience_years: NonNegativeInt = 0
    consultation_fee: Annotated[
        Decimal, 
        Field(max_digits=10, decimal_places=2, ge=0)
    ]
    bio: str | None
    address: str
    photo_url: str
    department_id: int | None
    hospital_id: int | None

class ResetPasswordForm(BaseModel):
    old_password: str
    new_password: Annotated[str, StringConstraints(min_length=8)]

class DoctorUpdateForm(BaseModel):
    first_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)] | None
    middle_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)] | None
    last_name: Annotated[str, StringConstraints(strip_whitespace=True, max_length=50)] | None

    email: EmailStr | None
    phone_number: Annotated[str, StringConstraints(max_length=20, strip_whitespace=True, pattern=r"^\+?\d{10,15}$")] | None
    gender: Annotated[Literal["male", "female", "other"], StringConstraints(to_lower=True, max_length=20)] | None

    specialization: Annotated[str, StringConstraints(max_length=200, strip_whitespace=True)]
    qualification: Annotated[str, StringConstraints(max_length=500)]
    experience_years: NonNegativeInt | None
    consultation_fee: Annotated[
        Decimal, 
        Field(max_digits=10, decimal_places=2, ge=0)
    ] | None
    bio: str | None
    address: str | None
    photo_url: str | None

class SchedulePayload(BaseModel):
    doctor_id: int

    day_of_week: Annotated[
            Literal["monday", "tuesday", "wednesday", "thursday",
                "friday", "saturday", "sunday"
            ], StringConstraints(strip_whitespace=True, to_lower=True)
        ]
    start_time: time
    end_time: time
    slot_duration: NonNegativeInt = 5
    max_patients_per_slot: Optional[NonNegativeInt]
    buffer_time_minutes: Optional[NonNegativeInt]

    hospital_id: Optional[int]

class ScheduleExcPayload(BaseModel):
    doctor_id: int

    exception_date: date
    is_available: bool
    start_time: Optional[time]
    end_time: Optional[time]

    reason: str

    @field_validator('end_time')
    @classmethod
    def validate_time(cls, v: time, info: ValidationInfo):
        # Ensure end time is after start time
        if info.data['is_available']:
            if 'start_time' in info.data:
                start_time = info.data['start_time']
                if v <= start_time:
                    raise ValidationError('end_time must be after start_time')
            return v
    
    @field_validator('exception_date')
    @classmethod
    def validate_exception_date(cls, v: date, info: ValidationInfo):
        # Ensure exception date is a future date
        today = datetime.now(tz=timezone.utc)
        target_date = datetime.combine(v, time=time(
            hour=23, minute=59, second=59
        ))

        if today > target_date:
            raise ValidationError('exception_date cannot be before current date')
        

class UpdateException(BaseModel):
    exception_date: Optional[date]
    is_available: Optional[bool]
    start_time: Optional[time]
    end_time: Optional[time]

    reason: Optional[str]

    @field_validator('end_time')
    @classmethod
    def validate_time(cls, v: time, info: ValidationInfo):
        # Ensure end time is after start time
        if info.data['is_available']:
            if 'start_time' in info.data:
                start_time = info.data['start_time']
                if v <= start_time:
                    raise ValidationError('end_time must be after start_time')
            return v
    
    @field_validator('exception_date')
    @classmethod
    def validate_exception_date(cls, v: date, info: ValidationInfo):
        # Ensure exception date is a future date
        today = datetime.now(tz=timezone.utc)
        target_date = datetime.combine(v, time=time(
            hour=23, minute=59, second=59
        ))

        if today > target_date:
            raise ValidationError('exception_date cannot be before current date')


class Slot(BaseModel):
    day: str
    start_time: time
    slot_duration: NonNegativeInt
    max_patients: NonNegativeInt = 1
    buffer_time_minutes: NonNegativeInt = 0
    is_available: bool = False
    booking_count: NonNegativeInt = 0

class ScheduleUpdatePayload(BaseModel):
    start_time: Optional[time]
    end_time: Optional[time]
    slot_duration: Optional[NonNegativeInt]
    max_patients_per_slot: Optional[NonNegativeInt]
    buffer_time_minutes: Optional[NonNegativeInt]