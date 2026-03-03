from fastapi import APIRouter, Request, Depends, status
from fastapi.exceptions import HTTPException
from ...auth.dependencies import user_auth_guard

from .models import *
from .service import UserService

from sqlalchemy.orm import Session
from ...database.models.response_models import UserResponse, PatientResponse
from ...database.sessions import create_session

from typing import List

def get_current_user(request: Request) -> UserResponse:
    return request.state.user


def authorize_user(
    request: Request,
    target_user_id: int,
    current_user: UserResponse = Depends(get_current_user)
) -> None:
    if (not current_user.is_superuser) and (current_user.id != target_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="privileges required",
        )

router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

@router.get("/me", status_code=status.HTTP_200_OK, 
            response_model=UserResponse, response_model_exclude_none=True)
async def get_me(request: Request) -> UserResponse:
    return request.state.user

@router.get("/patients", response_model=List[PatientResponse], status_code=status.HTTP_200_OK,
            description="""
    This method returns the logged in user's registered patient profiles
""")
async def get_my_patient_profiles(
    request: Request,
    session: Session = Depends(create_session),
) -> List[PatientResponse]:
    current_user: UserResponse = request.state.user
    if current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid request. no patients"
        )
    return UserService(session).get_my_patients(
        current_user.id    
    )

@router.delete("/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[Depends(authorize_user)]  #enforce authority of the user        
    )
async def delete_user(
    request: Request,
    target_user_id: int,
    session: Session = Depends(create_session) 
):
    success: bool = UserService(session).delete_user(target_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="user deletion failed",
        )
    
@router.patch("/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT,
        dependencies=[ Depends(authorize_user)] # enforce authority of user    
    )
async def update_user(
    request: Request,
    target_user_id: int,
    payload: UserUpdateForm,
    session: Session = Depends(create_session)
) -> None:
    payload_empty: bool = len(payload.model_dump(exclude_unset=True, exclude_none=True)) == 0
    if payload_empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="payload cannot be empty"
        )
    UserService(session).update_details(
        target_user_id, 
        payload, 
        updated_by=request.state.user.id
    )