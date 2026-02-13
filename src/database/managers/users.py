from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from .manager import BaseDatabase
from ..models.users import User, PotentialUsers, Tenant
from ..models.response_models import UserResponse, TempUser, TenantResponse
from ...exceptions import ManagerException
from typing import Any

from ...handlers.users.models import UserUpdateForm
import logging
from ...settings import get_settings

settings = get_settings()

# logger initiation
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)
file_handler = logging.FileHandler(filename=settings.logs_file)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

class UserManager(BaseDatabase):
    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def add_user(self, user: User) -> UserResponse:
        """
        Docstring for add_user
        
        :param user: User object of the database
        :type user: User
        :rtype: UserResponse
        """

        try:
            self.add_one(user)
            return user.to_response(exclude_sensitive=True)
        except Exception as e:
            logger.error("{}".format(str(e)))
            raise ManagerException("Auth", str(e))
        
    def add_temp_user(self, user: PotentialUsers) -> None:
        """
        Docstring for add_temp_user
        
        :param user: TempUser object of the database
        :type user: TempUser
        :rtype: None
        """

        try:
            self.add_one(user)
        except Exception as e:
            logger.error("{}".format(str(e)))
            raise ManagerException("Auth", str(e))
        
    def get_user(self, identifier: str, is_mail: bool = True) -> User | None:
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
            model = self.get_one(select(User).where(
                User.email == identifier
            ))
        else:
            model = self.get_one(select(User).where(
                User.phone_number == identifier
            ))

        if not model:
            return None

        return model

    def get_user_by_id(self, id: int) -> User:
        model = self.get_one(
            select(User).where(
                User.id == id
            )
        )
        if model is None:
            raise ManagerException("User", "user with does not exist")
        return model

    def get_tenant(self, tenant_id: int) -> TenantResponse | None:
        """
        Docstring for get_tenant
        
        :param tenant_id: id of the tenant
        :type tenant_id: int
        :return: Tenant response object if not found returns None
        :rtype: TenantResponse | None
        """
        model = self.get_one(
            select(Tenant).where(Tenant.id == tenant_id)
        )

        if model is None:
            return model
        return model.to_response()

    def potential_user(self, identifier: str, is_mail: bool = True) -> TempUser | None:
        """
        Docstring for potential_user
        
        :param identifier: User's phone_number or email
        :type identifier: str
        :param is_mail: By default consider identifier is mail
        :type is_mail: bool
        :rtype: TempUser or None
        """
        model: Any
        if is_mail:
            model = self.get_one(select(PotentialUsers).where(
                PotentialUsers.email == identifier
            ))
        else:
            model = self.get_one(select(PotentialUsers).where(
                PotentialUsers.phone_number == identifier
            ))

        if not model:
            return None

        return model
    
    def mark_delete(self, user_id: int) -> bool:
        """
        Soft deletes a user entity by marking the user inactive
        
        :param email: email of the user
        :type email: str
        :return: Delete success/failed
        :rtype: bool
        """
        model: User | None = self.get_one(select(User).where(User.id == user_id))
        if not isinstance(model, User):
            logger.info("user<{}>: invalid access detected".format(user_id))
            return False
        model.soft_delete()
        self.session.commit()
        return True
    
    def update_user(self, user_id: int, payload: UserUpdateForm) -> None:
        """
        Updates a user details which are permissible
        
        :param user_id: target user id
        :type user_id: UUID
        :param payload: update payload form
        :type payload: UserUpdateForm
        :rtype: None
        """
        model: User | None = self.get_one(select(User).where(User.id == user_id))
        if not isinstance(model, User):
            logger.info("user<{}>: invalid access detected".format(user_id))
            raise ValueError("user not found")
        
        # if the user changes the poc mark them as not verified to force re verification
        update_data = payload.model_dump(exclude_unset=True)

        # side-effect rules
        if "email" in update_data:
            model.email_verified = False
        if "phone_number" in update_data:
            model.phone_verified = False
        
        for key, value in update_data.items():
            setattr(model, key, value)
        
        self.session.commit()
        
    def get_hospital_admin(self, id: int) -> UserResponse:
        hospital_admin: User | None = self.get_one(
            select(User).where(
               and_(
                   User.id == id,
                   User.role == "hospital_admin"
               )
            )
        )
        if hospital_admin is None:
            raise ManagerException("User", "hospital admin does not exist")
        return hospital_admin.to_response(exclude_sensitive=True)