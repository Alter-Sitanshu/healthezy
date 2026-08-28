from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Literal
from enum import Enum


class UserRoles(Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    MOD = "moderator"
    SUPPORT = "support"
    HOS = "hospital-admin"
    LAB = "lab-admin"
    NORMAL = "user"


class SignUpForm(BaseModel):
    email: EmailStr
    phone_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]
    first_name: str
    last_name: str
    role: Literal["user", "hospital-admin", "lab-admin"]
    password: Annotated[str, StringConstraints(min_length=8)]
    # otp: Annotated[str, StringConstraints(max_length=4, min_length=4)]

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class OTPVerifyRequest(BaseModel):
    identifier: str
    is_email: bool = False # By default it is set to assume OTP over phone_number
    otp: str

class OTPResponse(BaseModel):
    message: str
    token: TokenSchema | None

class BasicSignUpForm(BaseModel):
    email: EmailStr
    phone_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]

class LoginRequest(BaseModel):
    email: EmailStr
    role: Literal[
        "user", "hospital-admin", "doctor", "lab-admin",
        "superadmin", "admin", "moderator", "support"
    ]
    password: str

class AdminForm(BaseModel):
    email: EmailStr
    phone_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]
    first_name: str
    last_name: str
    role: Literal["superadmin", "admin", "moderator", "support"]
    password: Annotated[str, StringConstraints(min_length=8)]
    admin_secret: Annotated[str, StringConstraints(strip_whitespace=True, min_length=32, max_length=32)]
   
class PassResetForm(BaseModel):
    curr_password: str
    new_password: str