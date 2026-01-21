from sqlalchemy.orm import Session
from sqlalchemy import select
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.tenants import Patient

from typing import Any, List

class PatientManager(BaseDatabase):
    
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add_patient(self, model: Patient) -> None:
        self.add_one(model)

    def get_patient_by_id(self, id: int) -> Patient:
        model = self.get_one(
            select(Patient).where(
                Patient.id == id
            )
        )
        if model is None:
            raise ManagerException("Patient", f"patient with id<{id}> does not exist")
        
        return model
    
    def delete(self, patient_id: int) -> None:
        target: Patient = self.get_patient_by_id(patient_id)
        self.delete_one(target)
    
    def update_patient(self, patient_id: int, updates: dict[str, Any]) -> None:
        patient: Patient = self.get_patient_by_id(patient_id)
        for key, value in updates.items():
            setattr(patient, key, value)
        self.session.commit()

    def all_patients(self) -> List[Patient]:
        return self.get_all(select(Patient))