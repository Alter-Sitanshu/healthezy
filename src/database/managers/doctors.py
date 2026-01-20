from sqlalchemy.orm import Session
from sqlalchemy import select
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import Doctor
from ..models.response_models import (
    DoctorResponse
)
from typing import List, Any
from pydantic import TypeAdapter

class DoctorManager(BaseDatabase):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.adapter = TypeAdapter(List[DoctorResponse])
    
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
            raise ManagerException("Doctor", str(e))
    
    def get_doctor_by_id(self, id: int) -> Doctor | None:
        model: Doctor | None = self.get_one(select(Doctor).where(Doctor.id == id))
        if model is None:
            print(f"doctor with id{id} does not exist")
            return
        
        return model
    
    def get_doctor_by_code(self, code: str) -> Doctor | None:
        model: Doctor | None = self.get_one(select(Doctor).where(Doctor.doctor_code == code))
        if model is None:
            print(f"doctor with code<{code}> does not exist")
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
    
    def delete(self, id: int) -> None:
        target: Doctor | None = self.get_one(select(Doctor).where(Doctor.id == id))
        if target is None:
            raise ManagerException("Doctor", f"could not delete doctor. not found <Id:{id}>")
        
        self.delete_one(target)

    def update(self, id: int, payload: dict[str, Any]) -> DoctorResponse:
        target: Doctor | None = self.get_one(select(Doctor).where(Doctor.id == id))
        if target is None:
            raise ManagerException("Doctor", f"could not find doctor <Id:{id}>")
        for key, value in payload.items():
            setattr(target, key, value)
        self.session.commit()
        return target.to_response()



