from sqlalchemy.orm import Session
from .models import PatientForm, PatientUpdate
from fastapi import HTTPException, status

from ...database.managers.manager import SessionMixin
from ...database.managers.users import UserManager
from ...database.managers.patients import PatientManager
from ...database.models.users import User
from ...database.models.tenants import Patient
from ...database.models.response_models import PatientResponse


from uuid import uuid4
from typing import List
from pydantic import TypeAdapter

class PatientService(SessionMixin):

    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._user_manager = UserManager(session)
        self._patient_manager = PatientManager(session)
        self.adapter = TypeAdapter(List[PatientResponse])

    def add_patient(self, user_id: int, form: PatientForm) -> None:

        user: User = self._user_manager.get_user_by_id(user_id)
        if len(user.registered_patients) == 5:
            raise ValueError("maximum patient limit reached for user")
        
        patient_code: str = f"PAT-{uuid4().hex[:8].upper()}"
        model = Patient(
            patient_code=patient_code,
            first_name=form.first_name,
            middle_name=form.middle_name,
            last_name=form.last_name,
            email=form.email,
            phone_number=form.phone_number,
            date_of_birth=form.date_of_birth,
            age=form.age,
            gender=form.gender,
            blood_group=form.blood_group,
            address=form.address,
            city=form.city,
            state=form.state,
            zip_code=form.zip_code,
            emergency_contact_name=form.emergency_contact_name,
            emergency_contact_phone=form.emergency_contact_phone,
            emergency_contact_relation=form.emergency_contact_relation,
            occupation=form.occupation,
            marital_status=form.marital_status,
            nationality=form.nationality,
            language_preference=form.language_preference,
            photo_url=form.photo_url,
            medical_history=form.medical_history,
            allergies=form.allergies,
            chronic_conditions=form.chronic_conditions,
            current_medications=form.current_medications,
            insurance_provider=form.insurance_provider,
            insurance_policy_number=form.insurance_policy_number,
            insurance_expiry_date=form.insurance_expiry_date,

            creator=user,
            updated_by=user_id
        )

        self._patient_manager.add_patient(model)

    def get_by_id(self, user_id: int, patient_id: int) -> PatientResponse:
        try:
            user: User = self._user_manager.get_user_by_id(user_id)
            # Superusers can access any patient
            if user.is_superuser:
                patient = self._patient_manager.get_patient_by_id(patient_id)
                return patient.to_response()
            
            for p in user.registered_patients:
                if p.id == patient_id:
                    return p.to_response()
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="unauthorised access"
                )
        except Exception as e:
            raise e
    
    def delete(self, user_id: int, patient_id: int) -> None:
        user: User = self._user_manager.get_user_by_id(user_id)
        if user.is_superuser:
            try:
                self._patient_manager.delete(patient_id)
            except Exception as e:
                raise HTTPException(
                    detail=str(e),
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            for p in user.registered_patients:
               if p.id == patient_id: 
                    self._patient_manager.delete(patient_id)
                    return
            else:
                # the loop was complete that means the user does not own the patient
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="unauthorised access"
                )
                
    def update_details(self, user_id: int, patient_id: int, updates: PatientUpdate) -> None:
        user: User = self._user_manager.get_user_by_id(user_id)
        if user.is_superuser:
            try:
                # Convert Pydantic model to dict, excluding None values
                update_dict = updates.model_dump(exclude_unset=True, exclude_none=True)
                if 'updated_by' not in update_dict:
                    update_dict['updated_by'] = user_id
                self._patient_manager.update_patient(patient_id, update_dict)
            except:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="unauthorised access"
                )
        else:
            for p in user.registered_patients:
                if p.id == patient_id:
                    # Convert Pydantic model to dict, excluding None values
                    update_dict = updates.model_dump(exclude_unset=True, exclude_none=True)
                    if 'updated_by' not in update_dict:
                        update_dict['updated_by'] = user_id
                    self._patient_manager.update_patient(patient_id, update_dict)
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="unauthorised access"
                )

    def get_all(self) -> List[PatientResponse]:
        models = self._patient_manager.all_patients()
        return self.adapter.validate_python(models)