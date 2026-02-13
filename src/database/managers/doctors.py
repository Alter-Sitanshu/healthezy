from sqlalchemy.orm import Session
from sqlalchemy import select, and_
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import Doctor
from ..models.response_models import (
    DoctorResponse
)
from typing import List, Any
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

class DoctorManager(BaseDatabase):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.adapter = TypeAdapter(List[DoctorResponse])

    def get_all_doctors(self) -> List[DoctorResponse]:
        model_list = self.get_all(
            select(Doctor)
        )

        return self.adapter.validate_python(model_list)
    
    def get_doctor(self, email: str) -> Doctor | None:
        """
        Docstring for get_doctor
        
        :param email: Doctor's email address
        :type email: str
        :return: Doctor object if found or else None
        :rtype: Doctor | None
        """

        return self.get_one(
            select(Doctor).where(
                Doctor.email == email
            )
        )

    def add_doctor(self, doctor: Doctor) -> DoctorResponse:
        """
        add_doctor inserts a new doctor entry in the doctors table
        
        :param doctor: doctor object
        :type doctor: Doctor
        :return: Doctor response object
        :rtype: DoctorResponse
        """
        try:
            self.add_one(doctor)
            return doctor.to_response()
        except Exception as e:
            logger.error("{}".format(str(e)))
            raise ManagerException("Doctor", str(e))
    
    def get_doctor_by_id(self, id: int) -> Doctor | None:
        model: Doctor | None = self.get_one(select(Doctor).where(Doctor.id == id))
        if model is None:
            return
        
        return model
    
    def get_doctor_by_code(self, code: str) -> Doctor | None:
        model: Doctor | None = self.get_one(select(Doctor).where(Doctor.doctor_code == code))
        if model is None:
            return
        
        return model
    
    def get_doctors_by_specialization(self, spec: str) -> List[DoctorResponse]:
        """
        Docstring for get_doctors_by_specialization
        
        :param spec: Specialization of a doctor
        :type spec: str
        :return: list of matching doctors
        :rtype: List[DoctorResponse]
        """
        doctors: List[Doctor] = self.get_all(select(Doctor).where(Doctor.specialization == spec))

        return self.adapter.validate_python(doctors)

    def get_doctors_by_experience(self, exp: int) -> List[DoctorResponse]:
        """
        Docstring for get_doctors_by_experience
        
        :param exp: minimum experience of the desired doctors
        :type exp: int
        :return: list of matching doctors
        :rtype: List[DoctorResponse]
        """
        doctors: List[Doctor] = self.get_all(select(Doctor).where(Doctor.experience_years >= exp))
        return self.adapter.validate_python(doctors)
    
    def delete(self, admin_id: int, id: int) -> None:
        target: Doctor | None = self.get_one(
            select_stmt=select(Doctor).where(
                and_(
                    Doctor.id == id,
                    Doctor.hospital.has(created_by=admin_id)
                )
            )
        )
        if target is None:
            raise ManagerException("Doctor", "could not delete doctor")
        
        self.delete_one(target)

    def update(self, id: int, payload: dict[str, Any]) -> DoctorResponse:
        target: Doctor | None = self.get_one(select(Doctor).where(Doctor.id == id))
        if target is None:
            raise ManagerException("Doctor", "doctor not found")
        for key, value in payload.items():
            setattr(target, key, value)
        self.session.commit()
        return target.to_response()



