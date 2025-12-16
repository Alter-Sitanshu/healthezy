from pydantic import BaseModel, EmailStr, StringConstraints
from typing import Optional, Annotated

class SignUpForm(BaseModel):
    email: EmailStr
    phone_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]
    first_name: str
    last_name: Optional[str]
    password: Annotated[str, StringConstraints(min_length=8)]

class TokenSchema(BaseModel):
    access_token: str
    token_type: str

class OTPVerifyRequest(BaseModel):
    identifier: str
    is_email: bool = True # By default it is set to assume OTP over email
    otp: str

class OTPResponse(BaseModel):
    message: str
    token: TokenSchema | None