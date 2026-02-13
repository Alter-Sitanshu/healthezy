# database imports
from ...database.managers.manager import SessionMixin
from ...database.managers.hospitals import HospitalManager
from ...database.managers.appointments import AppointmentManager
from ...database.models import Hospital
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

class HospitalService(SessionMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._hospital_manager = HospitalManager(session)
        self._appointment_manager = AppointmentManager(session)
        self.adapter = TypeAdapter(List[HospitalResponse])

    async def create_hospital(self, 
                              hospital: HospitalForm,
                              created_by: int
                            ) -> HospitalResponse:
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
            created_by=created_by,
            updated_by=created_by,
        )
        return self._hospital_manager.add_hospital(hosp)

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
        
