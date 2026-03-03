from sqlalchemy.orm import Session
from sqlalchemy import select, text, and_
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import Lab, LabTest, LabApplications
from ..models.response_models import LabResponse, LabTestResponse
from typing import Any, List
from pydantic import TypeAdapter
from ...settings import get_settings
import logging
from decimal import Decimal

settings = get_settings()

# logger initiation
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)
file_handler = logging.FileHandler(filename=settings.logs_file)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

class LabManager(BaseDatabase):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.lab_adapter = TypeAdapter(List[LabResponse])
        self.test_adapter = TypeAdapter(List[LabTestResponse])
    
    def add_lab(self, lab: Lab) -> int:
        """Add a new lab to the database"""
        try:
            self.add_one(lab)
            return lab.id
        except Exception as e:
            logger.error(f"Error adding lab: {str(e)}")
            raise ManagerException("Lab", "could not add lab")
    
    def add_lab_application(self, application: LabApplications) -> LabResponse:
        """Add a lab application to the database"""
        try:
            self.add_one(application)
            return application.to_response()
        
        except Exception as e:
            logger.error(f"Error adding lab: {str(e)}")
            raise ManagerException("Lab", "could not add lab application")

    def get_application_by_id(self, application_id: int) -> LabApplications | None:
        return self.get_one(
            select(LabApplications).where(LabApplications.id == application_id)
        )

    def get_lab_by_id(self, lab_id: int) -> LabResponse | None:
        """Fetch lab by ID"""
        lab: Lab | None = self.get_one(select(Lab).where(Lab.id == lab_id))
        if lab is None:
            return None
        return lab.to_response()
    
    def get_lab_by_code(self, lab_code: str) -> LabResponse | None:
        """Fetch lab by code"""
        lab: Lab | None = self.get_one(select(Lab).where(Lab.lab_code == lab_code))
        if lab is None:
            return None
        return lab.to_response()
    
    def get_all_labs(self) -> List[LabResponse]:
        """Fetch all active labs"""
        labs: List[Lab] = self.get_all(select(Lab).where(Lab.is_active == True))
        return self.lab_adapter.validate_python(labs)
    
    def get_lab_by_city(self, city: str) -> List[LabResponse]:
        """Fetch labs by city"""
        labs: List[Lab] = self.get_all(
            select(Lab).where((Lab.city == city) & (Lab.is_active == True))
        )
        return self.lab_adapter.validate_python(labs)
    
    def get_labs_nearby(self, latitude: Decimal, longitude: Decimal, radius_km: int) -> List[LabResponse]:
        """
        Scans for labs around a specific latitude and longitude around radius(radius_km)
        
        :param latitude: Latitude of coordinates
        :type latitude: Decimal
        :param longitude: Longitude of coordinates
        :type longitude: Decimal
        :param radius_km: radius of search in KM
        :type radius_km: int
        :return: All near by labs
        :rtype: List[LabResponse]
        """

        # Define the raw SQL
        raw_sql = text("""
            SELECT l.* FROM labs l
            WHERE l.is_active = true 
            AND l.latitude IS NOT NULL 
            AND l.longitude IS NOT NULL
            AND (6371 * acos(
                    cos(radians(:lat)) * cos(radians(l.latitude)) * cos(radians(l.longitude) - radians(:lon)) + 
                    sin(radians(:lat)) * sin(radians(l.latitude))
                )) <= :rad
            ORDER BY (
                    6371 * acos(
                       cos(radians(:lat)) * cos(radians(l.latitude)) * 
                       cos(radians(l.longitude) - radians(:long)) + sin(radians(:lat)) *
                       sin(radians(l.latitude))
                    )
                )
        """)

        # 2. Bind the SQL to the ORM Model
        # This creates a statement that returns 'Lab' objects
        stmt = select(Lab).from_statement(raw_sql)

        # 3. Bind the parameters securely
        stmt = stmt.params(lat=latitude, lon=longitude, rad=radius_km)

        # 4. Execute
        hospitals = self.get_all(stmt)

        return self.lab_adapter.validate_python(hospitals)

    def update_lab(self, lab_id: int, payload: dict[str, Any], updated_by: int,  admin_id: int | None = None,) -> None:
        """Update lab details"""
        try:
            if admin_id:
                lab: Lab | None = self.get_one(
                    select(Lab)
                    .where(
                        and_(
                            Lab.id == lab_id,
                            Lab.created_by == admin_id,
                        )
                ))
            else:
                lab: Lab | None = self.get_one(
                    select(Lab)
                    .where(
                            Lab.id == lab_id
                    ))
            if lab is None:
                raise ManagerException("Lab", f"Lab with ID {lab_id} not found")
            
            for key, value in payload.items():
                if hasattr(lab, key) and key not in ["id", "lab_code", "created_at", "created_by"]:
                    setattr(lab, key, value)
            
            lab.updated_by = updated_by
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error updating lab: {str(e)}")
            raise ManagerException("Lab", "could not update lab")
    
    def delete_lab(self, lab_id: int, admin_id: int | None = None) -> None:
        """Delete lab"""
        try:
            if admin_id:
                lab: Lab | None = self.get_one(
                    select(Lab)
                    .where(
                        and_(
                            Lab.id == lab_id,
                            Lab.created_by == admin_id,
                        )
                    ))
            else:
                lab: Lab | None = self.get_one(
                    select(Lab)
                    .where(
                        Lab.id == lab_id
                    ))
            if lab is None:
                raise ManagerException("Lab", f"Lab with ID {lab_id} not found")
            lab.is_active = False
            self.session.commit()
        except Exception as e:
            logger.error(f"Error deleting lab: {str(e)}")
            raise ManagerException("Lab", "could not delete lab")
    
    def add_lab_test(self, test: LabTest) -> LabTestResponse:
        """Add a new lab test"""
        try:
            self.add_one(test)
            return test.to_response()
        except Exception as e:
            logger.error(f"Error adding lab test: {str(e)}")
            raise ManagerException("LabTest", "could not add lab test")
    
    def get_lab_tests(self, lab_id: int) -> List[LabTestResponse]:
        """Fetch all tests for a lab"""
        tests: List[LabTest] = self.get_all(
            select(LabTest).where((LabTest.lab_id == lab_id) & (LabTest.is_active == True))
        )
        return self.test_adapter.validate_python(tests)
    
    def get_lab_test_by_id(self, test_id: int) -> LabTestResponse | None:
        """Fetch lab test by ID"""
        test: LabTest | None = self.get_one(select(LabTest).where(LabTest.id == test_id))
        if test is None:
            return None
        return test.to_response()
    
    def delete_lab_test(self, test_id: int) -> None:
        """Delete lab test"""
        try:
            test: LabTest | None = self.get_one(select(LabTest).where(LabTest.id == test_id))
            if test is None:
                raise ManagerException("LabTest", f"Lab test with id {test_id} not found")
            
            self.delete_one(test)
        except Exception as e:
            logger.error(f"Error deleting lab test: {str(e)}")
            raise ManagerException("LabTest", "could not delete lab test")

    def get_pending_applications(self) -> List[Lab]:
        return self.get_all(
            select(LabApplications).where(
                and_(
                    LabApplications.status == "PENDING",
                )
            )
        )

    def get_under_review_applications(self) -> List[Lab]:
        return self.get_all(
            select(LabApplications).where(
                and_(
                    LabApplications.status == "REVIEW",
                )
            )
        )


    def set_application_status(self, id_: int, status: str, verified_by: int) -> LabResponse | None:
        target_obj: LabApplications | None = self.get_one(
            select(LabApplications).where(
                LabApplications.id == id_
            )
        )
        if target_obj is not None:
            target_obj.status = status
            target_obj.verified_by = verified_by
            self.session.commit()