from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Annotated, Literal

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
    role: Literal["user", "hospital-admin", "doctor", "lab-admin"]
    password: str
    
class AdminForm(SignUpForm):
    admin_secret: Annotated[str, StringConstraints(strip_whitespace=True, min_length=32, max_length=32)]