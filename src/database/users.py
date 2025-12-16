from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from .manager import BaseDatabase
from .models import Users, UserResponse
from ..exceptions import ManagerException
from typing import Any
from uuid import UUID

from ..handlers.users.models import UserUpdateForm

class UserManager(BaseDatabase):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add_user(self, user: Users) -> UserResponse:
        """
        Docstring for add_user
        
        :param user: User object of the database
        :type user: User
        :rtype: UserResponse
        """

        try:
            self.add_one(user)
            return user.dict(exclude_sensitive=True)
        except Exception as e:
            raise ManagerException("Auth", str(e))
        
    def get_user(self, identifier: str, is_mail: bool = True) -> Users | None:
        """
        Docstring for get_user
        
        :param identifier: User's phone_number or email
        :type identifier: str
        :param is_mail: By default consider identifier is mail
        :type is_mail: bool
        :rtype: UserResponse
        """
        model: Any
        if is_mail:
            model = self.get_one(select(Users).where(or_(
                Users.email == identifier
            )))
        else:
            model = self.get_one(select(Users).where(or_(
                Users.phone_number == identifier
            )))

        if not isinstance(model, Users):
            print(f"User with details: {identifier} not found.")
            return None

        return model
    
    def mark_delete(self, user_id: UUID) -> bool:
        """
        Soft deletes a user entity by marking the user inactive
        
        :param email: email of the user
        :type email: str
        :return: Delete success/failed
        :rtype: bool
        """
        model: Users | None = self.get_one(select(Users).where(Users.id == user_id))
        if not isinstance(model, Users):
            # TODO: implement the logging
            print(f"user<{user_id}>: entity does not exist")
            return False
        model.soft_delete()
        self.session.commit()
        return True
    def update_user(self, user_id: UUID, payload: UserUpdateForm) -> None:
        """
        Updates a user details which are permissible
        
        :param user_id: target user id
        :type user_id: UUID
        :param payload: update payload form
        :type payload: UserUpdateForm
        :rtype: None
        """
        model: Users | None = self.get_one(select(Users).where(Users.id == user_id))
        if not isinstance(model, Users):
            # TODO: implement the logging
            print(f"user<{user_id}>: entity does not exist")
            raise ValueError("user not found")
        
        # if the user changes the poc mark them as not verified to force re verification
        update_data = payload.model_dump(exclude_unset=True)

        # side-effect rules
        if "email" in update_data or "phone_number" in update_data:
            model.is_verified = False
        
        for key, value in update_data.items():
            setattr(model, key, value)
        
        self.session.commit()
        
