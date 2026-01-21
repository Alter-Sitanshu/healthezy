from fastapi import APIRouter, Depends, status, HTTPException, Request
from ...auth.dependencies import user_auth_guard, enforce_admin_privilege
from .service import PatientService
from typing import List

# database imports
from ...database.models.response_models import PatientResponse, UserResponse
from ...database.sessions import create_session
from sqlalchemy.orm import Session

# model imports
from .models import PatientForm, PatientUpdate

router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_patient(
    request: Request,
    form: PatientForm,
    session: Session = Depends(create_session)
) -> None:
    current_user: UserResponse = request.state.user

    try:
        PatientService(session).add_patient(
            current_user.id, form
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/{patient_id}", status_code=status.HTTP_200_OK,
        response_model=PatientResponse    
)
async def get_patient_details(
    request: Request,
    patient_id: int,
    session: Session = Depends(create_session)
) -> PatientResponse:
    current_user: UserResponse = request.state.user
    try:
        response = PatientService(session).get_by_id(
            current_user.id, patient_id
        )
        return response
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="could not fetch patient details"
        )
    
@router.delete("/{patient_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_patient(
    request: Request,
    patient_id: int,
    session: Session = Depends(create_session)
) -> None:
    current_user: UserResponse = request.state.user
    try:
        service = PatientService(session)
        service.delete(current_user.id, patient_id)
    except Exception as e:
        raise e

@router.put("/{patient_id}", status_code=status.HTTP_200_OK)
async def update_patient_details(
    request: Request,
    patient_id: int,
    payload: PatientUpdate,
    session: Session = Depends(create_session)
) -> None:
    current_user: UserResponse = request.state.user
    try:
        service = PatientService(session)
        service.update_details(current_user.id, patient_id, payload)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[PatientResponse])
async def get_all_patients(
    request: Request,
    _: None = Depends(enforce_admin_privilege),
    session: Session = Depends(create_session)
) -> List[PatientResponse]:
    
    return PatientService(session).get_all()