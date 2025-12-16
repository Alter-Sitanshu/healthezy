from pydantic import BaseModel
from typing import Optional

class UserUpdateForm(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[str]

class PassResetForm(BaseModel):
    curr_password: str
    new_password: str
    confirm_password: str