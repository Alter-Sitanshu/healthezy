# database imports
from ...database.managers.manager import SessionMixin
from ...database.managers.labs import LabManager
from ...database.models.tenants import Lab, LabTest
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


class LabService(SessionMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._lab_manager = LabManager(session)
        self.adapter = TypeAdapter(List[LabResponse])
        self.test_adapter = TypeAdapter(List[LabTestResponse])

    async def create_lab(self, 
                        lab_data: NewLab,
                        created_by: int
                        ) -> LabResponse:
        """Create a new lab"""
        generated_code = f"LAB-{uuid4().hex[:8].upper()}"
        lab = Lab(
            lab_code=generated_code,
            name=lab_data.name,
            type=lab_data.type,
            description=lab_data.description,
            address=lab_data.address,
            city=lab_data.city,
            state=lab_data.state,
            zip_code=lab_data.zip_code,
            country=lab_data.country,
            phone_number=lab_data.phone_number,
            email=lab_data.email,
            website=str(lab_data.website) if lab_data.website else None,
            is24x7=lab_data.is24x7,
            opening_time=lab_data.opening_time,
            closing_time=lab_data.closing_time,
            hospital_id=lab_data.hospital_id,
            license_number=lab_data.license_number,
            accreditation=lab_data.accreditation,
            established_year=lab_data.established_year,
            latitude=lab_data.latitude,
            longitude=lab_data.longitude,
            created_by=created_by,
            updated_by=created_by,
            is_active=False
        )
        return self._lab_manager.add_lab(lab)

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
    
    def update_lab(self, lab_id: int, payload: dict[str, Any], updated_by: int) -> None:
        """Update lab details"""
        self._lab_manager.update_lab(lab_id, payload, updated_by)
    
    def delete_lab(self, lab_id: int) -> None:
        """Delete a lab"""
        self._lab_manager.delete_lab(lab_id)

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
