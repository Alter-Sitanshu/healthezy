from sqlalchemy.orm import Session
from .models import UserUpdateForm

from ...database.managers.manager import SessionMixin
from ...database.managers.users import UserManager
from ...database.models.users import User
from ...database.models.response_models import PatientResponse


from typing import List
from pydantic import TypeAdapter

class UserService(SessionMixin):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._user_manager = UserManager(session)
        self.patient_adapter = TypeAdapter(List[PatientResponse])

    def update_details(self, target_user_id: int, payload: UserUpdateForm, updated_by: int) -> None:
        self._user_manager.update_user(target_user_id, payload, updated_by)

    def delete_user(self, target_user_id: int) -> bool:
        return self._user_manager.mark_delete(target_user_id)
    
    def get_my_patients(self, user_id: int) -> List[PatientResponse]:
        me: User = self._user_manager.get_user_by_id(user_id)
        return self.patient_adapter.validate_python(me.registered_patients)