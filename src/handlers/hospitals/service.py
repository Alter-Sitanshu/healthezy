# database imports
from ...database.managers.manager import SessionMixin
from ...database.managers.hospitals import HospitalManager
from ...database.managers.appointments import AppointmentManager
from ...database.managers.doctors import DoctorManager
from ...database.managers.users import UserManager
from ...database.models import Hospital, Doctor, HospitalApplications
from ...database.models.response_models import HospitalResponse, DoctorResponse, AppointmentResponse

# sqlalchemy imports
from sqlalchemy.orm import Session

# model imports
from .models import HospitalForm

# util imports
from uuid import uuid4
from pydantic import TypeAdapter
from typing import List, Any
from decimal import Decimal
from enum import Enum

class ApplStatus(Enum):
    ACCEPT="ACCEPTED"
    REJECT="REJECTED"
    REVIEW="REVIEW"
    WITHDRAW="WITHDRAWN"

class HospitalService(SessionMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._hospital_manager = HospitalManager(session)
        self._appointment_manager = AppointmentManager(session)
        self.adapter = TypeAdapter(List[HospitalResponse])

    async def create_hospital(self, hospital: HospitalApplications) -> int:
        generated_code = f"HOS-{uuid4().hex[:8].upper()}"
        hosp = Hospital(
            hospital_code=generated_code,
            name=hospital.name,
            type=hospital.name,
            description=hospital.description,
            address=hospital.address,
            city=hospital.city,
            state=hospital.state,
            zip_code=hospital.zip_code,
            country=hospital.country,
            phone_number=hospital.phone_number,
            email=hospital.email,
            website=hospital.website,
            emergency_number=hospital.emergency_number,
            total_beds=hospital.total_beds,
            available_beds=hospital.available_beds,
            is24x7=hospital.is24x7,
            latitude=hospital.latitude,
            longitude=hospital.longitude,
            logo_url=hospital.logo_url,
            license_number=hospital.license_number,
            accreditation=hospital.accreditation,
            established_year=hospital.established_year,
            created_by=hospital.created_by,
            updated_by=hospital.created_by,
        )
        return self._hospital_manager.add_hospital(hosp)

    async def submit_hospital_application(
            self, form: HospitalForm, submitted_by: int
        ) -> HospitalResponse:
        hosp = HospitalApplications(
            name=form.name,
            type=form.name,
            description=form.description,
            address=form.address,
            city=form.city,
            state=form.state,
            zip_code=form.zip_code,
            country=form.country,
            phone_number=form.phone_number,
            email=form.email,
            website=form.website,
            emergency_number=form.emergency_number,
            total_beds=form.total_beds,
            available_beds=form.available_beds,
            is24x7=form.is24x7,
            latitude=form.latitude,
            longitude=form.longitude,
            logo_url=form.logo_url,
            license_number=form.license_number,
            accreditation=form.accreditation,
            established_year=form.established_year,
            created_by=submitted_by
        )
        self._hospital_manager.add_hospital_application(hosp)
        return hosp.to_response()

    def get_hospital_by_id(self, id: int | None) -> HospitalResponse | None:
        if id is None:
            return None
        return self._hospital_manager.get_hospital_by_id(id)
    
    def get_hospitals(self) -> List[HospitalResponse]:
        res: List[Hospital] = self._hospital_manager.get_all_hospitals()
        return self.adapter.validate_python(res)

    def get_hospital_by_code(self, hospital_code: str) -> HospitalResponse | None:
        return self._hospital_manager.get_hospital_by_code(hospital_code)
    
    def update_details(self, payload: dict[str, Any], hospital_code: str, admin_id: int) -> None:
        self._hospital_manager.update(payload, hospital_code, admin_id)
    
    def delete(self, hospital_code: str, admin_id: int) -> None:
        self._hospital_manager.delete(hospital_code, admin_id)

    def find_hospitals_around(self, lat: Decimal, long: Decimal, rad: int) -> List[HospitalResponse]:
        return self._hospital_manager.find_hospitals_around(
            lat, long, rad
        )
    
    def find_by_type(self, type_: str) -> List[HospitalResponse]:
        return self._hospital_manager.find_by(
            type_,
            "type"
        )
    
    def find_by_city(self, city: str) -> List[HospitalResponse]:
        return self._hospital_manager.find_by(
            city,
            "city"
        )
    
    def get_doctors(self, hospital_id: int) -> List[DoctorResponse]:
        return self._hospital_manager.get_doctors(hospital_id)
    
    def get_hospital_appointments(self, hospital_id: int, filters: dict[str, Any]) -> List[AppointmentResponse]:
        return self._appointment_manager.get_hospital_appointments(hospital_id, filters)
        
    def add_doctor(self, hospital_id: int, doctor_id: int) -> None:
        doc: Doctor | None = DoctorManager(self.session).get_doctor_by_id(doctor_id)
        if doc is None:
            raise NameError("doctor not found")
        
        if doc.hospital_id is None:
            doc.hospital_id = hospital_id
            self.session.commit()
        else:
            raise ValueError("method not allowed")
        
    async def approve(self, application_id: int, verified_by: int) -> None:
        appl: HospitalApplications | None = self._hospital_manager.get_application_by_id(application_id)
        if appl is None:
            raise ValueError("invalid credentials provided. appplication does not exist")
        
        self._hospital_manager.set_application_status(
            application_id, ApplStatus.ACCEPT.value, verified_by
        )

        hospital_id: int = await self.create_hospital(appl)
        UserManager(self.session).link_admin(appl.created_by, hospital_id)


    def reject(self, application_id: int, verified_by: int) -> None:
        self._hospital_manager.set_application_status(
            application_id, ApplStatus.REJECT.value, verified_by
        )
    
    def withdraw(self, application_id: int, created_by: int) -> None:
        self._hospital_manager.set_application_status(
            application_id, ApplStatus.WITHDRAW.value, created_by
        )