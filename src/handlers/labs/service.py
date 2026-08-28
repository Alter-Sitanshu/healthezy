# database imports
from ...database.managers.manager import SessionMixin
from ...database.managers.labs import LabManager
from ...database.managers.users import UserManager
from ...database.models.tenants import Lab, LabTest, LabApplications
from ...database.models.response_models import LabResponse, LabTestResponse

# sqlalchemy imports
from sqlalchemy.orm import Session

# model imports
from .models import NewLab, NewLabTest

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


class LabService(SessionMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._lab_manager = LabManager(session)
        self.adapter = TypeAdapter(List[LabResponse])
        self.test_adapter = TypeAdapter(List[LabTestResponse])

    async def create_lab(self, appl: LabApplications) -> int:
        """Create a new lab"""
        generated_code = f"LAB-{uuid4().hex[:8].upper()}"
        lab = Lab(
            lab_code=generated_code,
            name=appl.name,
            type=appl.type,
            description=appl.description,
            address=appl.address,
            city=appl.city,
            state=appl.state,
            zip_code=appl.zip_code,
            country=appl.country,
            phone_number=appl.phone_number,
            email=appl.email,
            website=str(appl.website) if appl.website else None,
            is24x7=appl.is24x7,
            opening_time=appl.opening_time,
            closing_time=appl.closing_time,
            hospital_id=appl.hospital_id,
            license_number=appl.license_number,
            accreditation=appl.accreditation,
            established_year=appl.established_year,
            latitude=appl.latitude,
            longitude=appl.longitude,
            created_by=appl.created_by,
            updated_by=appl.created_by
        )
        return self._lab_manager.add_lab(lab)

    async def submit_lab_application(self, appl: NewLab, submitted_by: int) -> LabResponse:
        lab = LabApplications(
            name=appl.name,
            type=appl.type,
            description=appl.description,
            address=appl.address,
            city=appl.city,
            state=appl.state,
            zip_code=appl.zip_code,
            country=appl.country,
            phone_number=appl.phone_number,
            email=appl.email,
            website=str(appl.website) if appl.website else None,
            is24x7=appl.is24x7,
            opening_time=appl.opening_time,
            closing_time=appl.closing_time,
            hospital_id=appl.hospital_id,
            license_number=appl.license_number,
            accreditation=appl.accreditation,
            established_year=appl.established_year,
            latitude=appl.latitude,
            longitude=appl.longitude,
            created_by=submitted_by,
        )
        return self._lab_manager.add_lab_application(lab)

    def get_lab_by_id(self, lab_id: int) -> LabResponse | None:
        """Get lab by ID"""
        return self._lab_manager.get_lab_by_id(lab_id)
    
    def get_lab_by_code(self, lab_code: str) -> LabResponse | None:
        """Get lab by code"""
        return self._lab_manager.get_lab_by_code(lab_code)
    
    def get_all_labs(self) -> List[LabResponse]:
        """Get all active labs"""
        return self._lab_manager.get_all_labs()
    
    def get_labs_by_city(self, city: str) -> List[LabResponse]:
        """Get labs in a specific city"""
        return self._lab_manager.get_lab_by_city(city)
    
    def get_labs_nearby(self, lat: Decimal, long: Decimal, rad: int) -> List[LabResponse]:
        """Get labs nearby within a specific radius (Km)"""
        return self._lab_manager.get_labs_nearby(lat, long, rad)
    
    def update_lab(self, lab_id: int, payload: dict[str, Any], updator: dict[str, Any]) -> None:
        """Update lab details"""
        self._lab_manager.update_lab(lab_id, payload, updator)

    
    def mark_delete_lab(self, lab_id: int, admin_id: int) -> None:
        """Delete a lab"""
        self._lab_manager.mark_delete(lab_id, admin_id)

    def delete_lab(self, lab_id: int) -> None:
        self._lab_manager.delete_lab(lab_id)

    async def approve(self, application_id: int, verified_by: int) -> None:
        appl: LabApplications | None = self._lab_manager.get_application_by_id(application_id)
        if appl is None:
            raise ValueError("invalid credentials provided. appplication does not exist")
        
        self._lab_manager.set_application_status(
            application_id, ApplStatus.ACCEPT.value, verified_by
        )

        lab_id: int = await self.create_lab(appl)
        UserManager(self.session).link_admin(appl.created_by, lab_id)


    def reject(self, application_id: int, verified_by: int) -> None:
        self._lab_manager.set_application_status(
            application_id, ApplStatus.REJECT.value, verified_by
        )
    
    def withdraw(self, application_id: int, created_by: int) -> None:
        self._lab_manager.set_application_status(
            application_id, ApplStatus.WITHDRAW.value, created_by
        )

    async def create_lab_test(self, 
                             lab_id: int,
                             test_data: NewLabTest,
                             created_by: int
                             ) -> LabTestResponse:
        """Create a new lab test"""
        # Verify lab exists
        lab = self._lab_manager.get_lab_by_id(lab_id)
        if lab is None:
            raise ValueError(f"Lab with id {lab_id} not found")
        
        generated_code = f"TST-{uuid4().hex[:8].upper()}"
        test = LabTest(
            lab_id=lab_id,
            test_code=generated_code,
            name=test_data.name,
            description=test_data.description,
            category=test_data.category,
            turnaround_time_hours=test_data.turnaround_time_hours,
            sample_type=test_data.sample_type,
            test_price=test_data.test_price,
            normal_range=test_data.normal_range,
            unit_of_measurement=test_data.unit_of_measurement,
            created_by=created_by,
            updated_by=created_by,
        )
        return self._lab_manager.add_lab_test(test)

    def get_lab_tests(self, lab_id: int) -> List[LabTestResponse]:
        """Get all tests for a lab"""
        return self._lab_manager.get_lab_tests(lab_id)
    
    def get_lab_test_by_id(self, test_id: int) -> LabTestResponse | None:
        """Get a specific lab test"""
        return self._lab_manager.get_lab_test_by_id(test_id)
    
    def delete_lab_test(self, test_id: int) -> None:
        """Delete a lab test"""
        self._lab_manager.delete_lab_test(test_id)
