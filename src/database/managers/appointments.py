from sqlalchemy.orm import Session
from sqlalchemy import select, update
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import Appointment, Patient, Doctor
from ..models.response_models import AppointmentResponse
from typing import Any, List
from datetime import datetime

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
    
    def invalidate(self, appointment: Appointment) -> None:
        appointment.status = "INVALID"
        self.session.commit()

    def validate(self, appointment: Appointment, timestamp: dict[str, datetime]) -> None:
        appointment.status = "COMPLETE"
        appointment.checked_in_at = timestamp["in"]
        appointment.checked_out_at = timestamp["out"]
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
    
    def update_appointment(self, appointment_id: int, update_data: dict[str, Any], updated_by: int) -> None:
        stmt = (
            update(Appointment)
            .where(Appointment.id == appointment_id)
            .values(update_data, updated_by = updated_by)
        )

        self.session.execute(stmt)
        self.session.commit()
    
    def get_appointments_by_user(self, user_id: int) -> List[Appointment]:
        stmt = select(Appointment).join(
            Patient, Appointment.patient_id == Patient.id
        ).where(
                Patient.created_by == user_id
            )
        return self.get_all(stmt)
    
    def get_appointment_for_update(self, appointment_id: int, user_id: int) -> int | None:
        target = self.get_one(
            select(Appointment.id)
            .join(Patient, Appointment.patient_id == Patient.id)
            .where(
                Patient.created_by == user_id
            )
        )

        return target
    
    def get_hospital_appointments(self, hospital_id: int, filters: dict[str, Any]) -> List[AppointmentResponse]:
        query = (
            select(
                Appointment,
                Patient.first_name.label("patient_first_name"),
                Patient.last_name.label("patient_last_name"),
                Doctor.first_name.label("doctor_first_name"),
                Doctor.last_name.label("doctor_last_name"),
                Doctor.doctor_code
            )
            .join(Patient, Appointment.patient_id == Patient.id)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .where(Appointment.hospital_id == hospital_id)
        )
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
    
    def get_appointments_by_doctor(self, doctor_id: int) -> List[Any]:
        stmt = (
            select(
                Appointment,
                Patient.first_name.label("patient_first_name"),
                Patient.last_name.label("patient_last_name"),
                Doctor.first_name.label("doctor_first_name"),
                Doctor.last_name.label("doctor_last_name")
            )
            .join(Patient, Appointment.patient_id == Patient.id)
            .join(Doctor, Appointment.doctor_id == Doctor.id)
            .where(Appointment.doctor_id == doctor_id)
        )
        return self.get_all(stmt)
