# authentication and hashing imports
from jose import jwt
from passlib.context import CryptContext

# utility imports
from typing import Any
from ..settings import get_settings
from fastapi import status
from fastapi.exceptions import HTTPException
from datetime import timezone, datetime, timedelta
import logging

# database models and base classes
from sqlalchemy.orm import Session
from .models import SignUpForm, TokenSchema, BasicSignUpForm, AdminForm
from ..database.managers.users import UserManager
from ..database.managers.doctors import DoctorManager
from ..database.models.response_models import UserResponse#, TenantResponse
from ..database.models.users import User, PotentialUsers
from ..database.models.tenants import Doctor
from ..database.managers.manager import SessionMixin


settings = get_settings() #load the env

TOKEN_SECRET: str = settings.secret_key
ADMIN_SECRET: str = settings.admin_secret
TOKEN_EXPIRY_MINUTES: int = settings.access_token_expire_minutes # By default 30mins
TOKEN_TYPE: str = "Bearer" #By default taking Bearer JWT tokens
TOKEN_ALGORITHM: str = settings.secret_algorithm
# USER_TENANT_ID: int = 0  # user will have tenant_id 0
OTP_EXPIRE_MINUTES: int = settings.otp_expire_minutes

# logger initiation
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)
file_handler = logging.FileHandler(filename=settings.logs_file)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

if not TOKEN_SECRET or not TOKEN_ALGORITHM:
    raise RuntimeError("JWT configuration missing")

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class HashingMixin:
    @staticmethod
    def encrypt(plain_password: str) -> str:
        return bcrypt_context.hash(plain_password)
    
    @staticmethod
    def verify(plain_password: str, hashed: str) -> bool:
        return bcrypt_context.verify(plain_password, hashed)
    
    @staticmethod
    def is_token_expired(exp: datetime) -> bool:
        return exp < datetime.now(timezone.utc)

    @classmethod
    def create_access_token(cls, email: str) -> str:
        """Encode user information and expiration time."""
        now = datetime.now(timezone.utc)
        jwt_claims: dict[str, Any] = {
            "sub": email,
            "exp": now + timedelta(minutes=int(TOKEN_EXPIRY_MINUTES)),
            "iat": now,
            "nbf": now,
            "iss": "fastapi-auth",
            "type": "access",
        }

        return jwt.encode(jwt_claims, TOKEN_SECRET, algorithm=TOKEN_ALGORITHM)

class AuthService(SessionMixin, HashingMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._user_manager = UserManager(session)
        self._doctor_manager = DoctorManager(session)

    async def create_user(self, payload: SignUpForm) -> UserResponse:
        # temp_user = self._user_manager.potential_user(payload.email)
        # if temp_user is None or not temp_user.is_verified:
        #     raise ValueError("user credentials not verified")
        user_model = User(
            # tenant_id=USER_TENANT_ID,
            email=payload.email,
            password=self.encrypt(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number,
            role=payload.role,
            phone_verified=True,
        )
        return self._user_manager.add_user(user_model)
    
    async def create_hos_admin(self, payload: SignUpForm) -> UserResponse:
        # temp_user = self._user_manager.potential_user(payload.email)
        # if temp_user is None or not temp_user.is_verified:
        #     raise ValueError("user credentials not verified")
        user_model = User(
            # tenant_id=USER_TENANT_ID,
            email=payload.email,
            password=self.encrypt(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number,
            role=payload.role,
            phone_verified=True,
            is_active=False,
        )
        return self._user_manager.add_user(user_model)
    
    async def create_lab_admin(self, payload: SignUpForm) -> UserResponse:
        # temp_user = self._user_manager.potential_user(payload.email)
        # if temp_user is None or not temp_user.is_verified:
        #     raise ValueError("user credentials not verified")
        user_model = User(
            # tenant_id=USER_TENANT_ID,
            email=payload.email,
            password=self.encrypt(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number,
            role=payload.role,
            phone_verified=True,
            is_active=False,
        )
        return self._user_manager.add_user(user_model)
    
    async def create_admin(self, payload: AdminForm) -> None:
        if payload.admin_secret != ADMIN_SECRET:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="access denied. unauthorised"
            )
        user_model = User(
            # tenant_id=USER_TENANT_ID,
            email=payload.email,
            password=self.encrypt(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
            phone_number=payload.phone_number,
            role=payload.role,
            phone_verified=True,
            is_superuser=True,
        )
        self._user_manager.add_user(user_model)

    # def get_tenant(self, tenant_id: int) -> TenantResponse | None:
    #     return self._user_manager.get_tenant(tenant_id)

    def create_temp_user(self, payload: BasicSignUpForm, otp: str) -> None:
        exp: datetime = datetime.now(timezone.utc) + timedelta(minutes=int(OTP_EXPIRE_MINUTES))
        model = PotentialUsers(
            email=payload.email,
            phone_number=payload.phone_number,
            otp=otp,
            otp_exp=exp
        )
        self._user_manager.add_temp_user(model)
    
    def cross_validate_otp(self, phone_number: str, otp: str) -> bool:
        temp_user = self._user_manager.potential_user(phone_number, is_mail=False)
        
        if temp_user is None:
            return False
        
        now = datetime.now(timezone.utc)
        exp = temp_user.otp_exp
        exp = exp.replace(tzinfo=timezone.utc) if exp.tzinfo == None else exp

        if (temp_user.otp != otp) or (not temp_user.is_verified)\
            or exp < now:
            return False

        return True
        
    def user_exists(self, email: str) -> bool:
        user: User | None = self._user_manager.get_user(email)
        return not (user is None)
    
    def authenticate(self, role: str, email: str, password: str) -> TokenSchema | None:
        cred_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="username or password incorrect",
                                    headers={"WWW-Authenticate": "Bearer"},
                                    )
        if role != "doctor":
            user: User | None = self._user_manager.get_user(email)
            if user is None or not user.is_active or (not user.email_verified and not user.phone_verified):
                # either user not found, or not active or (nothing is verified)
                raise cred_exception
        
            if not self.verify(password, user.password):
                raise cred_exception
            else:
                access_token = self.create_access_token(user.email)
                return TokenSchema(
                    access_token=access_token,
                    token_type=TOKEN_TYPE
                )
        else:
            doctor: Doctor | None = self._doctor_manager.get_doctor(email)
        
            if doctor is None or doctor.status.lower() != "active":
                # either user not found, or not active or (nothing is verified)
                raise cred_exception
            
            if not self.verify(password, doctor.password):
                raise cred_exception
            else:
                access_token = self.create_access_token(doctor.email)
                return TokenSchema(
                    access_token=access_token,
                    token_type="Bearer"
                )

    
    async def change_password(self, user_id: int, old_password: str, new_password: str) -> None:
        user: User = self._user_manager.get_user_by_id(id=user_id)
        if self.verify(old_password, user.password):
            user.password = self.encrypt(new_password)
        self.session.commit()


    def get_user_from_token(self, token: str) -> UserResponse | None:
        try:
            payload = jwt.decode(
                token, key=TOKEN_SECRET,
                algorithms=[TOKEN_ALGORITHM],
                options={"verify_exp": True}
            )
            user: User | None = self._user_manager.get_user(payload["sub"])
            if not user:
                return None
            return user.to_response(exclude_sensitive=True)
        except Exception as e:
            logger.info("JWT decode error: {}".format(e))
            return None

    async def regenerate_otp(self, identifier: str, is_email: bool = False) -> bool:
        temp_user = self._user_manager.potential_user(identifier, is_email)
        if temp_user is None:
            return False
        
        new_otp: str = "5678"
        new_exp: datetime = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)
        
        temp_user.otp = new_otp
        temp_user.otp_exp = new_exp

        self.session.commit()

        return True
    
    def verify_otp(self, identifier: str, is_email: bool, otp: str) -> str | None:
        user: User | None = self._user_manager.get_user(identifier, is_email)

        if not user:
            temp_user = self._user_manager.potential_user(identifier, is_email)
            # if the user is not in users it is still in the signup phase
            if not temp_user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            if temp_user.is_verified:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User already verified",
                )
            
            if otp != "5678":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid OTP",
                )
            
            temp_user.is_verified = True
            self.session.commit()
            return temp_user.email


        # user is in users that means the final user object is already created

        # TODO: implement this in the OTP table
        # if not user.otp_hash or not user.otp_expires_at:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="OTP not generated",
        #     )

        # if datetime.now(timezone.utc) > user.otp_expires_at:
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail="OTP expired",
        #     )

        

        # Verification success
        if otp != "5678":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP",
            )
        if is_email:
            user.email_verified = True
        else:
            user.phone_verified = True
        self.session.commit()
        return user.email
    
    # def get_hospital_admin(self, id: int, tenant_id: int) -> UserResponse:
    #     return self._user_manager.get_hospital_admin(id, tenant_id)

    def get_user_by_id(self, id: int) -> UserResponse:
        return self._user_manager.get_user_by_id(id).to_response(exclude_sensitive=True)
        