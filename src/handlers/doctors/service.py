# database imports
from ...database.managers.manager import SessionMixin
from ...database.managers.doctors import DoctorManager
from ...database.managers.schedules import ScheduleManager
from ...database.models.response_models import DoctorResponse, DoctorScheduleResp, DoctorScheduleExpResp
from ...database.models.tenants import Doctor, DoctorSchedule, DoctorScheduleExceptions

# sqlalchemy imports
from sqlalchemy.orm import Session

# model imports
from .models import NewDoctorForm, SchedulePayload, Slot, ScheduleExcPayload, UpdateException
from ...settings import get_settings

# util imports
from ...auth.service import HashingMixin
from uuid import uuid4
from typing import List, Any, Final
from datetime import time, timedelta, datetime, timezone
import secrets
import jwt

WEEK_DAY: Final[dict[str, int]] = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
}
settings = get_settings() #load the env

TOKEN_SECRET: str = settings.secret_key
TOKEN_EXPIRY_MINUTES: int = settings.access_token_expire_minutes
TOKEN_ALGORITHM: str = settings.secret_algorithm

def add_time_delta(t: time, delta: timedelta) -> time:
    """
    The function creates a dummy datetime object with dummy date and base date
    adds the timedelta and converts the resultant wrapped datetime object to time
    and returns. *wrapped here means after addition it wraps around 24H
    
    :param t: Base time object to add delta to
    :type t: time
    :param delta: delta time difference to add to base time
    :type delta: timedelta
    :return: Resultant time object (timezone-naive)
    :rtype: time
    """
    if t.tzinfo is not None:
        t = t.replace(tzinfo=None)
    base_date: datetime = datetime.combine(datetime.today(), t)
    return (base_date + delta).time()

class DoctorService(SessionMixin, HashingMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._doctor_manager = DoctorManager(session)
        self._schedule_manager = ScheduleManager(session)

    def reset_password(self, id: int, old: str, new: str) -> None:
        doc: Doctor | None = self._doctor_manager.get_doctor_by_id(id)
        if doc is None:
            raise ValueError("incorrect password or id")
        
        if not self.verify(old, doc.password):
            raise ValueError("incorrect password or id")

        doc.password = self.encrypt(new)
        self.session.commit()
        
    def get_all(self) -> List[DoctorResponse]:

        return self._doctor_manager.get_all_doctors()

    def get_doctor_from_token(self, token: str) -> DoctorResponse | None:
        try:
            payload = jwt.decode(
                token, key=TOKEN_SECRET,
                algorithms=[TOKEN_ALGORITHM],
                options={"verify_exp": True}
            )
            user: Doctor | None = self._doctor_manager.get_doctor(payload["sub"])
            if not user:
                return None
            return user.to_response(exclude_sensitive=True)
        except Exception as e:
            # TODO: add logging
            print(f"JWT decode error: str{e}")
            return None

    async def create_doctor(self, doc: NewDoctorForm, created_by: int) -> dict[str, str]:
        generated_code = f"DOC-{uuid4().hex[:8].upper()}"
        token = secrets.token_urlsafe(12)
        doctor = Doctor(
            doctor_code=generated_code,
            password=token,
            # Basic Info
            first_name=doc.first_name,
            middle_name=doc.middle_name or "", 
            last_name=doc.last_name,
            email=doc.email,
            phone_number=doc.phone_number,
            gender=doc.gender,

            # Professional Info
            specialization=doc.specialization,
            qualification=doc.qualification,
            registration_number=doc.registration_number,
            experience_years=doc.experience_years,
            consultation_fee=doc.consultation_fee,
            bio=doc.bio,
            
            # Location & Relations
            address=doc.address,
            photo_url=doc.photo_url,
            
            department_id=doc.department_id,
            hospital_id=doc.hospital_id,

            # Audit Fields
            created_by=created_by,
            updated_by=created_by,
        )
        self._doctor_manager.add_doctor(doctor)
        return {
            "token": token,
            "doc_code": generated_code
        }
    
    def get_doctor_by_spec(self, filter: str) -> List[DoctorResponse]:
        return self._doctor_manager.get_doctors_by_specialization(filter)
    
    def get_doctor_by_id(self, id: int) -> DoctorResponse | None:
        doc = self._doctor_manager.get_doctor_by_id(id)
        if doc is None:
            return
        
        doc.to_response()
    
    def get_doctor_by_experience(self, exp: int) ->List[DoctorResponse]:
        return self._doctor_manager.get_doctors_by_experience(exp)
    
    def delete_doctor(self, admin_id: int, doctor_id: int) -> None:
        try:
            self._doctor_manager.delete(admin_id, doctor_id)
        except Exception as e:
            raise ValueError(str(e))
    
    async def update_doctor(self, doctor_id: int, payload: dict[str, Any]) -> DoctorResponse:
        try:
            return self._doctor_manager.update(doctor_id, payload)
        except Exception as e:
            raise ValueError(str(e))
        
    def add_schedule(self, payload: SchedulePayload) -> bool:
        try:
            schedule = DoctorSchedule(
                doctor_id = payload.doctor_id,

                # schedule metadata
                day_of_week = payload.day_of_week,
                start_time = payload.start_time,
                end_time = payload.end_time,
                slot_duration = payload.slot_duration,
                max_patients_per_slot = payload.max_patients_per_slot,
                buffer_time_minutes = payload.buffer_time_minutes,

                # doctor metadata
                hospital_id = payload.hospital_id,
            )
            self._schedule_manager.add_schedule(schedule)
            return True
        
        except:
            return False
        
    def edit_schedule(self, schedule_id: int, payload: dict[str, Any]):
        target: DoctorSchedule | None = self._schedule_manager.get_schedule_by_id(schedule_id)
        if target is None:
            raise ValueError("Schedule", f"schedule{id} does not exist")
        self._schedule_manager.update(target, payload)

    def delete_schedule(self, id: int) -> None:
        self._schedule_manager.drop_schedule(id)

        
    @classmethod
    def retrieve_slots(cls, schedule: DoctorScheduleResp) -> List[Slot]:
        start: time = schedule.start_time
        end: time = schedule.end_time
         # Convert to naive if timezone-aware
        if start.tzinfo is not None:
            start = start.replace(tzinfo=None)
        if end.tzinfo is not None:
            end = end.replace(tzinfo=None)
            
        IST = timezone(timedelta(hours=5, minutes=30))

        delta: timedelta = timedelta(minutes=(schedule.slot_duration + schedule.buffer_time_minutes))
        now_dt = datetime.now(IST)
        now_: time = now_dt.time()

        now_ = now_.replace(tzinfo=None)
        slot_list: List[Slot] = []
        next_: time

        day_of_week: str = schedule.day_of_week.lower()
        day_: int = WEEK_DAY[day_of_week[:3]]
        today_: int = now_dt.weekday()


        while start < end:
            next_ = add_time_delta(start, delta)
            if next_ > end:
                break
            slot_list.append(
                Slot(
                    day=day_of_week,
                    start_time=start,
                    slot_duration=schedule.slot_duration,
                    max_patients=schedule.max_patients_per_slot,
                    buffer_time_minutes=schedule.buffer_time_minutes,
                    is_available = start >= now_ if day_ >= today_ else False
                )
            )
            start = next_

        return slot_list

    def get_schedule(self, schedule_id: int) -> List[Slot]:
        schedule = self._schedule_manager.get_schedule_by_id(schedule_id)
        if schedule is None:
            return []
        return self.retrieve_slots(schedule.to_response())
    
    def get_doctor_schedules(self, doctor_id: int) -> List[Slot]:
        doctor_schedules: List[DoctorScheduleResp] = self._schedule_manager.get_doctor_schedules(doctor_id)
        slots_: List[Slot] = []
        for schedule in doctor_schedules:
            slots_per_schedule: List[Slot] = self.retrieve_slots(schedule)
            slots_.extend(slots_per_schedule)

        return slots_
    
    async def add_exception(self, doctor_id: int, payload: ScheduleExcPayload) -> DoctorScheduleExpResp:
        # model validates the start and end times if required
        # it also verifies the exception date at runtime. safe to execute

        model = DoctorScheduleExceptions(
            doctor_id=doctor_id,
            exception_date=payload.exception_date,
            is_available=payload.is_available,
            start_time=payload.start_time,
            end_time=payload.end_time,
            reason=payload.reason,
        )
        self._schedule_manager.add_exception(model)

        return model.to_response()
    
    def get_exceptions(self, doctor_id: int) -> List[DoctorScheduleExpResp]:
        doctor: Doctor | None = self._doctor_manager.get_doctor_by_id(
            doctor_id
        )
        if doctor is None:
            raise ValueError("Doctor not found")
        
        return self._schedule_manager.exception_adapter.validate_python(doctor.schedule_exceptions)

    def delete_exception(self, doctor_id: int, exception_id: int) -> None:
        exception: DoctorScheduleExceptions = self._schedule_manager.get_exception_by_id(exception_id)
        if exception.doctor_id != doctor_id:
            raise ValueError("unauthorised access")
        
        self._schedule_manager.delete_one(exception)

    def update_exception(self, doc_id:int, exception_id: int, payload: UpdateException) -> None:
        exception = self._schedule_manager.get_exception_by_id(exception_id)
        if exception.doctor_id != doc_id:
            raise ValueError("unauthorised access")
        
        self._schedule_manager.update(
            exception, payload.model_dump(exclude_none=True)
        )