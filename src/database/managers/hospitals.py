from sqlalchemy.orm import Session
from sqlalchemy import select, text
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import Hospital #Doctor
from ..models.response_models import (
    HospitalResponse, DoctorResponse
)
from typing import Any, List, Literal
from decimal import Decimal

from pydantic import TypeAdapter
from ...settings import get_settings
import logging


settings = get_settings()

# logger initiation
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename=settings.logs_file)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

class HospitalManager(BaseDatabase):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.adapter = TypeAdapter(List[HospitalResponse])
    
    def add_hospital(self, hospital: Hospital) -> HospitalResponse:
        """
        Adds the hospital instance to the database
        
        :param hospital: Hospital instance
        :type hospital: Hospital
        :return: HospitalResponse object
        :rtype: HospitalResponse
        """
        try:
            self.add_one(hospital)
            return hospital.to_response()

        except Exception as e:
            logger.error("{}".format(str(e)))
            raise ManagerException("Hospital", "could not add hospital")
    
    def get_hospital_by_id(self, id: int) -> HospitalResponse | None:
        """
        fetches the hospital for the given id. if not found returns None

        :param id: hospital id
        :type id: int 
        :return: HospitalResponse object or None
        :rtype: HospitalResponse | None
        """
        hospital: Hospital | None = self.get_one(select(Hospital).where(Hospital.id == id))
        if hospital is None:
            return hospital
        
        return hospital.to_response()
    
    def get_hospital_by_code(self, hospital_code: str) -> HospitalResponse | None:
        """
        fetches the hospital for the given code. if not found returns None

        :param hospital_code: hospital code
        :type hospital_code: str 
        :return: HospitalResponse object or None
        :rtype: HospitalResponse | None
        """
        hospital: Hospital | None = self.get_one(
            select(Hospital).where(Hospital.hospital_code == hospital_code)
        )
        if hospital is None:
            return hospital
        
        return hospital.to_response()
    
    def get_all_hospitals(self) -> List[Hospital]:
        return self.get_all(
            select(Hospital)
        )

    def update(self, payload: dict[str, Any], hospital_code: str) -> None:
        """
        Updates the target hospital's details. If not found raise exception
        
        :param payload: dict of key and values to be updated
        :type payload: dict[str, Any]
        :param hospital_code: target hospital code to update
        :type hospital_code: str
        """

        target: Hospital | None = self.get_one(
            select(Hospital).where(Hospital.hospital_code == hospital_code)
        )
        if target is None:
            raise ManagerException("Hospital", "invalid hospital code")

        for key, value in payload.items():
            setattr(target, key, value)
        
        self.session.commit()

    def delete(self, hospital_code: str) -> None:
        target: Hospital | None = self.get_one(
            select(Hospital).where(Hospital.hospital_code == hospital_code)
        )
        if target is None:
            raise ManagerException("Hospital", "invalid hospital code")

        self.delete_one(target)

    def find_hospitals_around(self, latitude: Decimal, longitude: Decimal, radius_km: int) -> List[HospitalResponse]:
        """
        Scans for hospitals around a specific latitude and longitude around radius(radius_km)
        
        :param latitude: Latitude of coordinates
        :type latitude: Decimal
        :param longitude: Longitude of coordinates
        :type longitude: Decimal
        :param radius_km: radius of search in KM
        :type radius_km: int
        :return: All near by hospitals
        :rtype: List[HospitalResponse]
        """

        # Define the raw SQL
        raw_sql = text("""
            SELECT h.* FROM hospitals h
            WHERE h.is_active = true 
            AND h.latitude IS NOT NULL 
            AND h.longitude IS NOT NULL
            AND (6371 * acos(
                    cos(radians(:lat)) * cos(radians(h.latitude)) * cos(radians(h.longitude) - radians(:lon)) + 
                    sin(radians(:lat)) * sin(radians(h.latitude))
                )) <= :rad
            ORDER BY (
                    6371 * acos(
                       cos(radians(:lat)) * cos(radians(h.latitude)) * 
                       cos(radians(h.longitude) - radians(:long)) + sin(radians(:lat)) *
                       sin(radians(h.latitude))
                    )
                )
        """)

        # 2. Bind the SQL to the ORM Model
        # This creates a statement that returns 'Hospital' objects
        stmt = select(Hospital).from_statement(raw_sql)

        # 3. Bind the parameters securely
        stmt = stmt.params(lat=latitude, lon=longitude, rad=radius_km)

        # 4. Execute
        hospitals = self.get_all(stmt)

        return self.adapter.validate_python(hospitals)
    
    def find_by(self, param: str, param_type: Literal["type", "city"]) -> List[HospitalResponse]:
        column = None
        if param_type == "type":
            column = Hospital.type
        elif param_type == "city":
            column = Hospital.city
        else:
            # 2. Handle invalid types immediately
            raise ManagerException("Hospital", "invalid query param {}".format(param_type))

        stmt = select(Hospital).where(column == param)

        # 4. Execute
        hospitals = self.get_all(stmt)
        return self.adapter.validate_python(hospitals)

    def get_doctors(self, hospital_id: int) -> List[DoctorResponse]:
        hospital: Hospital | None = self.get_one(
            select(Hospital).where(
                Hospital.id == hospital_id
            )
        )
        if hospital is None:
            raise ManagerException("Hospital", "hospital does not exist")
        
        doctors = hospital.doctors
        adapter = TypeAdapter(List[DoctorResponse])

        return adapter.validate_python(doctors)