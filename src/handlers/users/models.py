from pydantic import BaseModel, StringConstraints
from typing import Optional, Annotated

class UserUpdateForm(BaseModel):
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")] | None
