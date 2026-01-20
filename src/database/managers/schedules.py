from sqlalchemy.orm import Session
from sqlalchemy import select
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import (
    Doctor,
    DoctorSchedule, DoctorScheduleExceptions
)
from ..models.response_models import (
    DoctorScheduleResp, DoctorScheduleExpResp
)

from typing import Any, List
from pydantic import TypeAdapter

class ScheduleManager(BaseDatabase):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.adapter = TypeAdapter(List[DoctorScheduleResp])
        self.exception_adapter = TypeAdapter(List[DoctorScheduleExpResp])

    def add_schedule(self, schedule: DoctorSchedule) -> None:
        """
        Creates a doctor schedule instance in the database
        :param schedule: DoctorSchedule object

        """
        try:
            self.add_one(schedule)
        except Exception as e:
            raise ManagerException("Schedule", str(e))
    
    
    def get_schedule_by_id(self, id: int) -> DoctorSchedule | None:
        model: DoctorSchedule | None = self.get_one(select(DoctorSchedule).where(DoctorSchedule.id == id))
        if model is None: 
            return
        return model
    
    def get_doctor_schedules(self, doctor_id: int) -> List[DoctorScheduleResp]:
        doctor: Doctor | None = self.get_one(select(Doctor).where(Doctor.id == doctor_id))
        if doctor is None:
            return []
        
        schedules: List[DoctorSchedule] = doctor.schedules
        return self.adapter.validate_python(schedules)
    
    def drop_schedule(self, id: int) -> None:
        target: DoctorSchedule | None  = self.get_one(
            select(DoctorSchedule).where(DoctorSchedule.id == id)
        )

        if target is None:
            raise ManagerException("Schedule", f"target schedule<{id}> does not exist")

        self.delete_one(target)

    def add_exception(self, exception: DoctorScheduleExceptions) -> None:
        self.add_one(exception)

    def get_exception_by_id(self, id: int) -> DoctorScheduleExceptions:
        model = self.get_one(
            select(DoctorScheduleExceptions).where(
                DoctorScheduleExceptions.id == id
            )
        )
        if model is None:
            raise ManagerException("Exception", "invalid id")
        
        return model

    def update(self, model: Any, payload: dict[str, Any]) -> None:
        for key, value in payload.items():
            setattr(model, key, value)

        self.session.commit()