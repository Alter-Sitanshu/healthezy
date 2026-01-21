from pydantic import BaseModel
from typing import Optional
from datetime import date, time


class AppointmentRequest(BaseModel):
    patient_id: int
    doctor_id: int
    hospital_id: int
    department_id: Optional[int]

    appointment_date: date
    appointment_time: time
    duration_minutes: int
    visit_type: str # Online or Offline

    booking_type: str = "CHECKUP" # Follow-Up or Check-up
    reason_for_visit: str
    notes: Optional[str]

class UpdateAppointment(BaseModel):
    booking_type: Optional[str]
    appointment_date: Optional[date]
    appointment_time: Optional[time]
    reason_for_visit: Optional[str]
    notes: Optional[str]