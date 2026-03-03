from .base import Base
from sqlalchemy import (
    String, DateTime, Boolean, BigInteger, 
    Index, Text, Integer, ForeignKey,
    Date, Time, DECIMAL
)
from sqlalchemy.sql import func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .response_models import (
    PatientResponse, DepartmentResponse,
    DoctorResponse, AppointmentResponse,
    DoctorScheduleResp, DoctorScheduleExpResp,
    HospitalResponse, LabResponse, LabTestResponse
)
from datetime import datetime, date, time
from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal

if TYPE_CHECKING:
    from .users import User


class Patient(Base):

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    patient_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    # patient details
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    blood_group: Mapped[str] = mapped_column(String(10))
    
    # patient location details
    address: Mapped[str] = mapped_column(Text)
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    zip_code: Mapped[str] = mapped_column(String(20))

    # emergency contact details
    emergency_contact_name: Mapped[str] = mapped_column(String(100))
    emergency_contact_phone: Mapped[str] = mapped_column(String(20))
    emergency_contact_relation: Mapped[str] = mapped_column(String(50))

    # miscellanous details
    occupation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    marital_status: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    nationality: Mapped[str] = mapped_column(String(50), default="INDIA")
    language_preference: Mapped[str] = mapped_column(String(50))
    photo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    medical_history: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chronic_conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_medications: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # insurance details
    insurance_provider: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    insurance_policy_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    insurance_expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # patient activity records
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_patient_creator"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_patient_updator"), nullable=False)

    creator: Mapped["User"] = relationship(
        "User", 
        back_populates="registered_patients",
        foreign_keys=[created_by]
    )

    __table_args__ = (
        Index("idx_patient_code", "patient_code"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_patients_email", "email"),
        Index("idx_phone", "phone_number"),
        Index("idx_patients_created_at", "created_at"),
    )

    @property
    def full_name(self) -> str:
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def update_photo(self, url: str) -> None:
        self.photo_url = url
    
    def to_response(self) -> PatientResponse:
        return PatientResponse.model_validate(self)
    
class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    department_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    head_of_department: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    phone_number: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(255))
    floor_number: Mapped[int] = mapped_column(Integer)
    building: Mapped[str] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # audit records
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by: Mapped[str] = mapped_column(String(100))
    
    # Relationships
    doctors: Mapped[List["Doctor"]] = relationship("Doctor", back_populates="department")

    def to_response(self) -> DepartmentResponse:
        """Converts SQLAlchemy model to Pydantic DepartmentResponse"""
        return DepartmentResponse.model_validate(self)

class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    doctor_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    gender: Mapped[str] = mapped_column(String(20), nullable=False)

    specialization: Mapped[str] = mapped_column(String(200), nullable=False)
    qualification: Mapped[str] = mapped_column(String(500), nullable=False)
    registration_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    consultation_fee: Mapped[Decimal] = mapped_column(DECIMAL(10, 2, asdecimal=True), nullable=False)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    address: Mapped[str] = mapped_column(Text)
    photo_url: Mapped[str] = mapped_column(String(500))
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.id"), nullable=True)
    hospital_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hospitals.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="doctor_created_by"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id", name="doctor_updated_by"), nullable=True)
    
    # Relationships
    department: Mapped[Optional["Department"]] = relationship("Department", back_populates="doctors")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", passive_deletes=True,back_populates="doctor")
    hospital: Mapped[Optional["Hospital"]] = relationship("Hospital", back_populates="doctors")
    schedules: Mapped[List["DoctorSchedule"]] = relationship("DoctorSchedule", passive_deletes=True, back_populates="doctor")
    schedule_exceptions: Mapped[List["DoctorScheduleExceptions"]] = relationship(
        "DoctorScheduleExceptions", back_populates="doctor",
        passive_deletes=True)

    __table_args__ = (
        Index("idx_doctor_code", "doctor_code"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_doctors_email", "email"),
        Index("idx_specialization", "specialization"),
        Index("idx_doctors_status", "status"),
        Index("idx_department_id", "department_id")
    )

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Doctor(id={self.id}, email={self.email}, name={self.full_name})>"

    def to_response(self, exclude_sensitive: bool = True) -> DoctorResponse:
        if exclude_sensitive:
            resp = DoctorResponse.model_validate(self)
            resp.password = None
        
        return DoctorResponse.model_validate(self)
        

class DoctorSchedule(Base):

    __tablename__ = "doctor_schedules"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"))
    
    day_of_week: Mapped[str] = mapped_column(String(20), nullable=False)
    start_time: Mapped[time] = mapped_column(Time(timezone=True), nullable=False)
    end_time: Mapped[time] = mapped_column(Time(timezone=True), nullable=False)
    slot_duration: Mapped[int] = mapped_column(Integer, comment="Slot duration in minutes")
    max_patients_per_slot: Mapped[int] = mapped_column(Integer, default=1, comment="For concurrent appointments")
    buffer_time_minutes: Mapped[int] = mapped_column(Integer, default=0, comment="Gap between appointments")
    hospital_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="Null = primary hospital, specific ID = location-based schedule")
    
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedules")
   
    __table_args__ = (
        Index("idx_ds_doctor_id", "doctor_id"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_day", "day_of_week")
    )

    def to_response(self) -> DoctorScheduleResp:
        return DoctorScheduleResp.model_validate(self)

class DoctorScheduleExceptions(Base):

    __tablename__ = "doctor_schedule_exceptions"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id", ondelete="CASCADE"), nullable=False)
    
    exception_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=False, comment="False is leave/holiday, true is for special working hours")
    start_time: Mapped[time] = mapped_column(Time(timezone=True), comment="For special working hours")
    end_time: Mapped[time] = mapped_column(Time(timezone=True), comment="For special working hours")

    reason: Mapped[str] = mapped_column(Text)
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    
    # Relationships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="schedule_exceptions")
    
    __table_args__ = (
        Index("idx_dse_doctor_id", "doctor_id"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_leave_date", "exception_date"),
        # UniqueConstraint("doctor_id", "exception_date", "tenant_id", name="unique_doctor_date")
    )

    def to_response(self) -> DoctorScheduleExpResp:
        return DoctorScheduleExpResp.model_validate(self)

class Hospital(Base):

    __tablename__ = "hospitals"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    hospital_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="INDIA")

    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_number: Mapped[str] = mapped_column(String(20), nullable=False)
    is24x7: Mapped[bool] = mapped_column(Boolean, default=False)

    total_beds: Mapped[int] = mapped_column(Integer, default=0)
    available_beds: Mapped[int] = mapped_column(Integer, default=0)
    
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(10, 8, asdecimal=True))
    longitude: Mapped[Decimal] = mapped_column(DECIMAL(11, 8, asdecimal=True))

    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    license_number: Mapped[str] = mapped_column(String(100))
    accreditation: Mapped[str] = mapped_column(String(200))
    established_year: Mapped[int] = mapped_column(Integer, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # is_rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="hospitals_created_by"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="hospitals_updated_by"), nullable=True)

    # Relationships
    doctors: Mapped[List["Doctor"]] = relationship("Doctor", back_populates="hospital")

    __table_args__ = (
        Index("idx_hospital_code", "hospital_code"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_city", "city")
    )

    def to_response(self) -> HospitalResponse:
        return HospitalResponse.model_validate(self)

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    appointment_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    
    doctor_id: Mapped[Optional[int]] = mapped_column(ForeignKey("doctors.id"), 
                                                     index=True,
                                                     nullable=True, 
                                                     comment="Nullable for walk in/ department based appointments")
    hospital_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hospitals.id"))
    department_id: Mapped[Optional[int]] = mapped_column(BigInteger, comment="For department based appointments without specific doctor")

    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    appointment_time: Mapped[time] = mapped_column(Time(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=15)
    visit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    booking_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="SCHEDULED")
    # appointment_mode: Mapped[str] = mapped_column(String(20), default="SCHEDULED", comment='SCHEDULED, QUEUE, BLOCK, CONCURRENT')
    reason_for_visit: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    token_number: Mapped[int] = mapped_column(Integer, nullable=False)

    checked_in_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    checked_out_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    consultation_ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_appointmnent_creator"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="fk_appointment_updator"), nullable=False)

    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Realtionships
    doctor: Mapped["Doctor"] = relationship("Doctor", back_populates="appointments")

    __table_args__ = (
        Index("idx_appointment_number", "appointment_number"),
        Index("idx_patient_id", "patient_id"),
        Index("idx_appointments_doctor_id", "doctor_id"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_appointment_date", "appointment_date"),
        Index("idx_appointments_status", "status")
    )

    def to_response(self) -> AppointmentResponse:
        return AppointmentResponse.model_validate(self)

class Lab(Base):
    __tablename__ = "labs"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    lab_code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(100), comment="Pathology, Diagnostic, Imaging, etc.")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location details
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="INDIA")

    # Contact information
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Operating hours
    is24x7: Mapped[bool] = mapped_column(Boolean, default=False)
    opening_time: Mapped[Optional[time]] = mapped_column(Time(timezone=True), nullable=True)
    closing_time: Mapped[Optional[time]] = mapped_column(Time(timezone=True), nullable=True)

    # Hospital association
    hospital_id: Mapped[Optional[int]] = mapped_column(ForeignKey("hospitals.id"), nullable=True, comment="Associated hospital if any")

    # License & credentials
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    accreditation: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="e.g., NABL, ISO certified")
    established_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Geographic coordinates
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(10, 8, asdecimal=True), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(DECIMAL(11, 8, asdecimal=True), nullable=False)

    # Media
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # is_rejected: Mapped[bool] = mapped_column(Boolean, default=False)
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="labs_created_by"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="labs_updated_by"), nullable=True)

    # Relationships
    hospital: Mapped[Optional["Hospital"]] = relationship("Hospital")
    tests: Mapped[List["LabTest"]] = relationship("LabTest", back_populates="lab", passive_deletes=True)

    __table_args__ = (
        Index("idx_lab_code", "lab_code"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_lab_city", "city"),
        Index("idx_lab_is_active", "is_active")
    )

    def to_response(self) -> LabResponse:
        return LabResponse.model_validate(self)

class LabTest(Base):
    __tablename__ = "lab_tests"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    lab_id: Mapped[int] = mapped_column(ForeignKey("labs.id", ondelete="CASCADE"), nullable=False)
    
    test_code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Test categorization
    category: Mapped[str] = mapped_column(String(100), nullable=False, comment="Blood, Urine, Imaging, etc.")
    
    # Test specifications
    turnaround_time_hours: Mapped[int] = mapped_column(Integer, nullable=False, comment="Hours required to get results")
    sample_type: Mapped[str] = mapped_column(String(100), nullable=False, comment="Blood, Urine, Saliva, etc.")
    
    # Pricing
    test_price: Mapped[Decimal] = mapped_column(DECIMAL(10, 2, asdecimal=True), nullable=False)
    
    # Reference values
    normal_range: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment="e.g., 4.5-11.0")
    unit_of_measurement: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="e.g., 10^3/uL")
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="lab_test_created_by"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="lab_test_updated_by"), nullable=True)

    # Relationships
    lab: Mapped["Lab"] = relationship("Lab", back_populates="tests")

    __table_args__ = (
        Index("idx_lab_test_lab_id", "lab_id"),
        Index("idx_lab_test_code", "test_code"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_lab_test_category", "category"),
        Index("idx_lab_test_is_active", "is_active")
    )

    def to_response(self) -> LabTestResponse:
        return LabTestResponse.model_validate(self)
    
class LabApplications(Base):
    __tablename__ = "labs_applications"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(100), comment="Pathology, Diagnostic, Imaging, etc.")
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Location details
    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="INDIA")

    # Contact information
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Operating hours
    is24x7: Mapped[bool] = mapped_column(Boolean, default=False)
    opening_time: Mapped[Optional[time]] = mapped_column(Time(timezone=True), nullable=True)
    closing_time: Mapped[Optional[time]] = mapped_column(Time(timezone=True), nullable=True)

    # Hospital association
    # Don't need to make a relation as this will be verified by the Admin
    hospital_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True, comment="Associated hospital if any")

    # License & credentials
    license_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    accreditation: Mapped[Optional[str]] = mapped_column(String(200), nullable=True, comment="e.g., NABL, ISO certified")
    established_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Geographic coordinates
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(10, 8, asdecimal=True), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(DECIMAL(11, 8, asdecimal=True), nullable=False)

    # Media
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(20), default="PENDING",
                            comment="PENDING, REVIEW, ACCEPTED, REJECTED, WITHDRAWN")
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="labs_appllied_by"), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None, onupdate=func.now())
    verified_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="labs_verified_by"), nullable=True)
    __table_args__ = (
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_appl_lab_city", "city"),
        Index("idx_appl_lab_status", "status")
    )

    def to_response(self) -> LabResponse:
        return LabResponse.model_validate(self)

class HospitalApplications(Base):
    
    __tablename__ = "hospitals_applications"

    id: Mapped[int] = mapped_column(BigInteger, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    address: Mapped[str] = mapped_column(Text, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(100), nullable=False)
    zip_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(100), default="INDIA")

    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    emergency_number: Mapped[str] = mapped_column(String(20), nullable=False)
    is24x7: Mapped[bool] = mapped_column(Boolean, default=False)

    total_beds: Mapped[int] = mapped_column(Integer, default=0)
    available_beds: Mapped[int] = mapped_column(Integer, default=0)
    
    latitude: Mapped[Decimal] = mapped_column(DECIMAL(10, 8, asdecimal=True))
    longitude: Mapped[Decimal] = mapped_column(DECIMAL(11, 8, asdecimal=True))

    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    license_number: Mapped[str] = mapped_column(String(100))
    accreditation: Mapped[str] = mapped_column(String(200))
    established_year: Mapped[int] = mapped_column(Integer, nullable=False)

    status: Mapped[str] = mapped_column(String(20), default="PENDING",
                            comment="PENDING, REVIEW, ACCEPTED, REJECTED, WITHDRAWN")
    # tenant_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="hospitals_applied_by"), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None, onupdate=func.now())
    verified_by: Mapped[int] = mapped_column(ForeignKey("users.id", name="hospitals_verified_by"), nullable=True)
   
    __table_args__ = (
        Index("idx_appl_hospital_status", "status"),
        # Index("idx_tenant_id", "tenant_id"),
        Index("idx_appl_hospital_city", "city")
    )

    def to_response(self) -> HospitalResponse:
        return HospitalResponse.model_validate(self)
    
