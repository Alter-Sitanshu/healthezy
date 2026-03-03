from sqlalchemy.orm import Session
from ...database.managers.manager import SessionMixin
from ...database.managers.hospitals import HospitalManager
from ...database.managers.users import UserManager
from ...database.managers.patients import PatientManager
from ...database.managers.labs import LabManager



from ...database.models.response_models import (
    HospitalResponse, PatientResponse, UserResponse,
    LabResponse
)

# dependencies
from ..hospitals.service import HospitalService
from ..labs.service import LabService


from typing import List, Any
from pydantic import TypeAdapter

class AdminService(SessionMixin):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._hos_manager = HospitalManager(session)
        self._usr_manager = UserManager(session)
        # self._patient_manager = PatientManager(session)
        self._lab_manager = LabManager(session)
        self.hospital_adapter = TypeAdapter(List[HospitalResponse])
        self.user_adapter = TypeAdapter(List[UserResponse])
        self.patient_adapter = TypeAdapter(List[PatientResponse])
        self.lab_adapter = TypeAdapter(List[LabResponse])
        
    
    def get_provider_admins(self, provider: str, isactive: bool | None) -> List[UserResponse]:
        """Gets the new provider admin applications"""
        admins = self._usr_manager.get_admins(provider=provider, isactive=isactive)
        return self.user_adapter.validate_python(admins)
                

    def get_applications(self, for_: str, status: str) -> List[Any]:
        match for_:
            case "hospital":
                return self._get_hospital_applications(status)
            case "lab":
                return self._get_lab_applications(status)
            case _:
                return []
            
    async def approve(self, entity: str, id_: int, verified_by: int) -> None:
        match entity:
            case "hospitals":
                await HospitalService(self.session).approve(id_, verified_by)
            case "labs":
                await LabService(self.session).approve(id_, verified_by)
            case _:
                return
            
    def reject(self, entity: str, id_: int, verified_by: int) -> None:
        match entity:
            case "hospitals":
                HospitalService(self.session).reject(id_, verified_by=verified_by)
            case "labs":
                LabService(self.session).reject(id_, verified_by)
            case _:
                return

    def _get_lab_applications(self, status: str) -> List[LabResponse]:
        match status:
            case "pending":
                labs = self._lab_manager.get_pending_applications()
            case "under_review":
                labs = self._lab_manager.get_under_review_applications()
            case _:
                return []

        return self.lab_adapter.validate_python(labs)

    def _get_hospital_applications(self, status: str) -> List[HospitalResponse]:
        match status:
            case "pending":
                hospitals = self._hos_manager.get_pending_applications()
            case "under_review":
                hospitals = self._hos_manager.get_under_review_applications()
            case _:
                return []

        return self.hospital_adapter.validate_python(hospitals)
    
    def get_users(self, active: bool = False) -> List[UserResponse]:
        users = UserManager(self.session).get_all_users(active)
        return self.user_adapter.validate_python(users)
    
    def get_patients(self) -> List[PatientResponse]:
        patients = PatientManager(self.session).get_all_patients()
        return self.patient_adapter.validate_python(patients)