# authentication and hashing imports
from uuid import uuid4
from jose import jwt
from passlib.context import CryptContext

# utility imports
from typing import Any
from ..settings import get_settings
from fastapi import status
from fastapi.exceptions import HTTPException
from datetime import timezone, datetime, timedelta

# database models and base classes
from sqlalchemy.orm import Session
from .models import SignUpForm, TokenSchema
from ..database.users import UserManager, Users, UserResponse
from ..database.manager import SessionMixin


settings = get_settings() #load the env
TOKEN_SECRET: str = settings.secret_key
TOKEN_EXPIRY_MINUTES: int = settings.access_token_expire_minutes # By default 30mins
TOKEN_TYPE: str = "bearer" #By default taking Bearer JWT tokens
TOKEN_ALGORITHM: str = settings.secret_algorithm

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

class AuthService(SessionMixin, HashingMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self.user_manager = UserManager(session)

    def create_user(self, payload: SignUpForm) -> UserResponse:
        user_model = Users(
            id=uuid4(),
            email=payload.email,
            hashed_password=self.encrypt(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name if payload.last_name else None,
            phone_number=payload.phone_number,
        )
        return self.user_manager.add_user(user_model)
            
    def authenticate(self, email: str, password: str) -> TokenSchema | None:
        user: Users | None = self.user_manager.get_user(email)
        cred_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail="Could not authorise credentials",
                                    headers={"WWW-Authenticate": "Bearer"},
                                    )
        if user is None or not user.is_active:
            raise cred_exception
        
        if not self.verify(password, user.hashed_password):
            raise cred_exception
        else:
            access_token = self.create_access_token(user.full_name, user.email)
            return TokenSchema(
                access_token=access_token,
                token_type=TOKEN_TYPE
            )
    
    @classmethod
    def create_access_token(cls, name: str, email: str) -> str:
        """Encode user information and expiration time."""
        now = datetime.now(timezone.utc)
        jwt_claims: dict[str, Any] = {
            "sub": email,
            "name": name,
            "exp": now + timedelta(minutes=int(TOKEN_EXPIRY_MINUTES)),
            "iat": now,
            "nbf": now,
            "iss": "fastapi-auth",
            "type": "access",
        }

        return jwt.encode(jwt_claims, TOKEN_SECRET, algorithm=TOKEN_ALGORITHM)
    
    @staticmethod
    def is_token_expired(exp: datetime) -> bool:
        return exp < datetime.now(timezone.utc)
    
    def get_user_from_token(self, token: str) -> UserResponse | None:
        try:
            payload = jwt.decode(
                token, key=TOKEN_SECRET,
                algorithms=[TOKEN_ALGORITHM],
                options={"verify_exp": True}
            )
            user: Users | None = self.user_manager.get_user(payload["sub"])
            if not user:
                return None
            return user.dict(exclude_sensitive=True)
        except Exception as e:
            # TODO: add logging
            print(f"JWT decode error: str{e}")
            return None

    
    def verify_otp(self, identifier: str, is_email: bool, otp: str) -> tuple[str, str] | None:
        user: Users | None = self.user_manager.get_user(identifier, is_email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already verified",
            )

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

        if otp != "5678":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OTP",
            )

        # Verification success
        user.verify_email()
        self.session.commit()
        return (user.full_name, user.email)