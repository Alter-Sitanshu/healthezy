from sqlalchemy.orm import Session
from sqlalchemy import select, and_, func, update
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import (
    Appointment,
    DoctorSchedule, DoctorScheduleExceptions
)
from ..models.response_models import (
    DoctorScheduleResp, DoctorScheduleExpResp
)

from typing import Any, List
from pydantic import TypeAdapter
from datetime import date, time

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
        schedules = self.get_all(select(DoctorSchedule).where(DoctorSchedule.doctor_id == doctor_id))
        return self.adapter.validate_python(schedules)
    
    def drop_schedule(self, id: int) -> None:
        target: DoctorSchedule | None  = self.get_one(
            select(DoctorSchedule).where(DoctorSchedule.id == id)
        )

        if target is None:
            raise ManagerException("Schedule", "target schedule<{}> does not exist".format(id))

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

    def update_schedule(self, schedule_id: int, doctor_id: int, payload: dict[str, Any]) -> None:
        try:
            self.session.execute(
                update(DoctorSchedule).where(
                    and_(
                        DoctorSchedule.id == schedule_id,
                        DoctorSchedule.doctor_id == doctor_id
                    )
                ).values(payload)
            )
            self.session.commit()
        except:
            raise ManagerException(
                "Schedule", "cannot update doctor schedule <{}>".format(schedule_id)
            )

    def update_schedule_exception(self, exception_id: int, doctor_id: int, payload: dict[str, Any]) -> None:
        try:
            self.session.execute(
                update(DoctorScheduleExceptions).where(
                    and_(
                        DoctorScheduleExceptions.id == exception_id,
                        DoctorScheduleExceptions.doctor_id == doctor_id
                    )
                ).values(payload)
            )
            self.session.commit()
        except:
            raise ManagerException(
                "ScheduleException", "cannot update doctor schedule <{}>".format(exception_id)
            )


    def get_bookings(self, doctor_id: int, target_date: date) -> List[Any]:
        stmt = (
            select(Appointment.appointment_time, func.count(Appointment.id))
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date == target_date,
                    Appointment.status != 'CANCELLED'
                )
            )
            .group_by(Appointment.appointment_time)
        )
        return self.get_all(stmt)
    
    def get_slot_bookings(self, doctor_id: int, target_date: date, target_time: time) -> int:
        stmt = (
            select(func.count(Appointment.id))
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date == target_date,
                    Appointment.appointment_time == target_time,
                    Appointment.status != 'CANCELLED',
                )
            )
        )
        return self.get_one(stmt)
    
    def invalidate_appointments(self, doctor_id: int, _date: date) -> None:
        stmt = (
            update(Appointment).where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.appointment_date == _date
                )

            ).values(
                status = "CANCELLED"
            )
        )
        self.session.execute(stmt)
        self.session.commit()