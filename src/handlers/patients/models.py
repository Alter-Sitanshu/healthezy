from pydantic import (
    BaseModel, StringConstraints, EmailStr, NonNegativeInt,
    field_validator, ValidationError, ValidationInfo
)
from typing import Optional, Annotated, Literal
from datetime import date, datetime, time


class PatientForm(BaseModel):
    first_name: Annotated[str, StringConstraints(max_length=100)]
    middle_name: Optional[str]
    last_name: Annotated[str, StringConstraints(max_length=100)]
    email: EmailStr
    phone_number: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]
    date_of_birth: date
    age: NonNegativeInt
    gender: Literal["male", "female", "other"]
    blood_group: Annotated[str, StringConstraints(min_length=4)]

    address: str
    city: str
    state: str
    zip_code: str

    emergency_contact_name: str
    emergency_contact_phone: Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]
    emergency_contact_relation: str

    occupation: Optional[str]
    marital_status: Optional[Literal["married", "single"]]
    nationality: str = "INDIA"
    language_preference: Optional[str]
    photo_url: Optional[str]

    medical_history: Optional[str]
    allergies: Optional[str]
    chronic_conditions: Optional[str]
    current_medications: Optional[str]

    insurance_provider: Optional[str]
    insurance_policy_number: Optional[str]
    insurance_expiry_date: Optional[date]


    @field_validator("blood_group")
    @classmethod
    def validate_blood_goup(cls, blood_grp: str):
        type_: str = blood_grp[:len(blood_grp)-3].upper() # the last 3 chars will be polarity
        polarity: str = blood_grp[-3:].lower()
        allowed_types = ["AB", "A", "B", "O"]
        allowed_polarity = ["+ve", "-ve"]
        if type_ not in allowed_types:
            raise ValidationError("the blood group type must be in [AB, A, B, O]")
        
        if polarity not in allowed_polarity:
            raise ValidationError("malformed blood group polarity. must be +ve or -ve", polarity)
        
        # standardise the blood group formatting
        return type_+polarity
    
    @field_validator("insurance_expiry_date")
    @classmethod
    def validate_insurance(cls, d: date, info: ValidationInfo):
        if 'insurance_provider' in info.data:
            exp_datetime = datetime.combine(date=d, time=time(
                hour=0, minute=0, second=0
            ))
            now = datetime.now()
            if exp_datetime <= now:
                raise ValidationError("insurance expired")
            
            if 'insurance_policy_number' not in info.data:
                raise ValidationError("insurance policy number is missing", cls.insurance_provider)
    
class PatientUpdate(BaseModel):
    first_name: Optional[Annotated[str, StringConstraints(max_length=100)]]
    middle_name: Optional[str]
    last_name: Optional[Annotated[str, StringConstraints(max_length=100)]]
    email: Optional[EmailStr]
    phone_number: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]]
    date_of_birth: Optional[date]
    age: Optional[NonNegativeInt]
    gender: Optional[Literal["male", "female", "other"]]
    blood_group: Optional[Annotated[str, StringConstraints(min_length=4)]]

    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    zip_code: Optional[str]

    emergency_contact_name: Optional[str]
    emergency_contact_phone: Optional[Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=20, pattern=r"^\+?\d{10,15}$")]]
    emergency_contact_relation: Optional[str]

    occupation: Optional[str]
    marital_status: Optional[Literal["married", "single"]]
    nationality: Optional[str]
    language_preference: Optional[str]
    photo_url: Optional[str]

    medical_history: Optional[str]
    allergies: Optional[str]
    chronic_conditions: Optional[str]
    current_medications: Optional[str]

    insurance_provider: Optional[str]
    insurance_policy_number: Optional[str]
    insurance_expiry_date: Optional[date]

    @field_validator("blood_group")
    @classmethod
    def validate_blood_group(cls, blood_grp: str | None):
        if blood_grp is None:
            return blood_grp
        type_: str = blood_grp[:len(blood_grp)-3].upper()  # the last 3 chars will be polarity
        polarity: str = blood_grp[-3:].lower()
        allowed_types = ["AB", "A", "B", "O"]
        allowed_polarity = ["+ve", "-ve"]
        if type_ not in allowed_types:
            raise ValidationError("the blood group type must be in [AB, A, B, O]")
        
        if polarity not in allowed_polarity:
            raise ValidationError("malformed blood group polarity. must be +ve or -ve")
        
        # standardise the blood group formatting
        return type_ + polarity
    
    @field_validator("insurance_expiry_date")
    @classmethod
    def validate_insurance(cls, d: date | None, info: ValidationInfo):
        if d is None:
            return d
        if 'insurance_provider' in info.data and info.data['insurance_provider'] is not None:
            exp_datetime = datetime.combine(date=d, time=time(hour=0, minute=0, second=0))
            now = datetime.now()
            if exp_datetime <= now:
                raise ValidationError("insurance expired")
            
            if 'insurance_policy_number' not in info.data or info.data['insurance_policy_number'] is None:
                raise ValidationError("insurance policy number is missing")