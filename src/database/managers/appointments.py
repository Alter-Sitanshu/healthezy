from sqlalchemy.orm import Session
from sqlalchemy import select
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import Appointment, Patient
from ..models.response_models import AppointmentResponse
from typing import Any, List

from pydantic import TypeAdapter

class AppointmentManager(BaseDatabase):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.adapter = TypeAdapter(List[AppointmentResponse])

    def create_appointment(self, appointment: Appointment) -> None:
        self.add_one(appointment)

    def cancel(self, appointment: Appointment) -> None:
        appointment.status = "CANCELLED"
        self.session.commit()

    def get_appointment_by_id(self, appointment_id: int) -> Appointment:
        model: Appointment | None = self.get_one(
            select(Appointment).where(
                Appointment.id == appointment_id
            )
        )  
        if model is None:
            raise ManagerException("Appointment", "invalid id")
        
        return model
    
    def get_patient(self, patient_id: int) -> Patient:
        model = self.get_one(
            select(Patient).where(
                Patient.id == patient_id
            )
        )
        if model is None:
            raise ManagerException("Appointment", "patient does not exist")
        
        return model
    
    def update_appointment(self, appointment_id: int, update_data: dict[str, Any]) -> Appointment:
        appointment = self.get_appointment_by_id(appointment_id)
        for key, value in update_data.items():
            if hasattr(appointment, key) and value is not None:
                setattr(appointment, key, value)
        self.session.commit()
        return appointment
    
    def get_appointments_by_user(self, user_id: int) -> List[Appointment]:
        stmt = select(Appointment).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
                Patient.created_by == user_id
            )
        return self.get_all(stmt)
    
    def get_hospital_appointments(self, hospital_id: int, filters: dict[str, Any]) -> List[AppointmentResponse]:
        query = select(Appointment).where(Appointment.hospital_id == hospital_id)
        if filters.get("status"):
            query = query.where(Appointment.status == filters["status"])

        if filters.get("doctor_id"):
            query = query.where(Appointment.doctor_id == filters["doctor_id"])

        if filters.get("date_from"):
            query = query.where(Appointment.appointment_date >= filters["date_from"])

        if filters.get("date_to"):
            query = query.where(Appointment.appointment_date <= filters["date_to"])

        result = self.get_all(select_stmt=query)
        return self.adapter.validate_python(result)