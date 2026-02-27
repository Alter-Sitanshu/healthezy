from ...database.managers.manager import SessionMixin
from ...database.models.tenants import Appointment, Patient
from ...database.models.response_models import AppointmentResponse
from ...database.managers.appointments import AppointmentManager
from ...database.managers.schedules import ScheduleManager

from sqlalchemy.orm import Session

from fastapi import HTTPException, status

from .models import *
from uuid import uuid4
from pydantic import TypeAdapter
from typing import List

class AppointmentService(SessionMixin):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._appointment_manager = AppointmentManager(session)
        self._schedule_manager = ScheduleManager(session)
        self.adapter = TypeAdapter(List[AppointmentResponse])

    def create_appointment(self, payload: AppointmentRequest) -> AppointmentResponse:
        appointment_num: str = f"{uuid4().hex[:10].upper()}"
        booking_count: int = self._schedule_manager.get_slot_bookings(
            payload.doctor_id, payload.appointment_date, payload.appointment_time
        )
        model = Appointment(
            appointentment_number=appointment_num,
            patient_id=payload.patient_id,
            doctor_id=payload.doctor_id,
            hospital_id=payload.hospital_id,
            department_id=payload.department_id,
            appointment_date=payload.appointment_date,
            appointment_time=payload.appointment_time,
            duration_minutes=payload.duration_minutes,
            visit_type=payload.visit_type,
            booking_type=payload.booking_type,
            reason_for_visit=payload.reason_for_visit,
            notes=payload.notes,
            token_number=booking_count+1
        )
        self._appointment_manager.create_appointment(model)

        return model.to_response()
    
    def cancel_appointment(self, user_id: int, appointment_id: int) -> None:
        appointment = self._appointment_manager.get_appointment_by_id(appointment_id)

        # for sure the patient exists
        patient: Patient = self._appointment_manager.get_patient(appointment.patient_id)
        if patient.creator.id != user_id:
            raise ValueError("unauthorised access")
        
        
        self._appointment_manager.cancel(appointment)
    
    def update_appointment(self, user_id: int, appointment_id: int, update_data: UpdateAppointment) -> AppointmentResponse:
        appointment = self._appointment_manager.get_appointment_by_id(appointment_id)
        patient = self._appointment_manager.get_patient(appointment.patient_id)
        if patient.creator.id != user_id:
            raise ValueError("unauthorised access")
        
        updated = self._appointment_manager.update_appointment(appointment_id, update_data.model_dump(exclude_unset=True))
        return updated.to_response()
    
    def get_my_appointments(self, user_id: int) -> List[AppointmentResponse]:
        appointments = self._appointment_manager.get_appointments_by_user(user_id)
        return self.adapter.validate_python(appointments)
    
    def invalidate(self, appointment_id: int, doctor_id: int) -> None:
        appointment = self._appointment_manager.get_appointment_by_id(appointment_id)
        if appointment.doctor_id != doctor_id:
            raise HTTPException(
                detail="unauthorised request",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        self._appointment_manager.invalidate(appointment)

    def mark_completed(self, appointment_id: int, doctor_id: int) -> None:
        appointment = self._appointment_manager.get_appointment_by_id(appointment_id)
        if appointment.doctor_id != doctor_id:
            raise HTTPException(
                detail="unauthorised request",
                status_code=status.HTTP_401_UNAUTHORIZED
            )
        self._appointment_manager.validate(appointment)