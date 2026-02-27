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
                

    def get_applications(self, for_: str) -> List[Any]:
        match for_:
            case "hospital":
                return self._get_hospital_applications()
            case "lab":
                return self._get_lab_applications()
            case _:
                return []
            
    def approve(self, entity: str, id_: int) -> None:
        match entity:
            case "hospitals":
                self._hos_manager.approve(id_)
            case "labs":
                self._lab_manager.approve(id_)
            case _:
                return
            
    def reject(self, entity: str, id_: int) -> None:
        match entity:
            case "hospitals":
                self._hos_manager.reject(id_)
            case "labs":
                self._lab_manager.reject(id_)
            case _:
                return

    def _get_lab_applications(self) -> List[LabResponse]:
        labs = LabManager(self.session).get_applications()
        return self.lab_adapter.validate_python(labs)

    def _get_hospital_applications(self) -> List[HospitalResponse]:
        hospitals = HospitalManager(self.session).get_applications()
        return self.hospital_adapter.validate_python(hospitals)
    
    def get_users(self, active: bool = False) -> List[UserResponse]:
        users = UserManager(self.session).get_all_users(active)
        return self.user_adapter.validate_python(users)
    
    def get_patients(self) -> List[PatientResponse]:
        patients = PatientManager(self.session).get_all_patients()
        return self.patient_adapter.validate_python(patients)