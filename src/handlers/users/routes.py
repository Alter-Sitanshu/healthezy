from fastapi import APIRouter, Request, Depends, status
from fastapi.exceptions import HTTPException
from ...auth.dependencies import user_auth_guard

from .models import *

from sqlalchemy.orm import Session
from ...database.models.response_models import UserResponse
from ...database.sessions import create_session
from ...database.managers.users import UserManager


def get_current_user(request: Request) -> UserResponse:
    return request.state.user


def authorize_user(
    request: Request,
    target_user_id: int,
    current_user: UserResponse = Depends(get_current_user)
) -> None:
    if not current_user.is_superuser and (current_user.id != target_user_id):
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

@router.delete("/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    request: Request,
    target_user_id: int,
    session: Session = Depends(create_session),
    _: None = Depends(authorize_user) #enforce authority of the user
):
    success: bool = UserManager(session).mark_delete(target_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="user deletion failed",
        )
    
@router.patch("/{target_user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(
    request: Request,
    target_user_id: int,
    payload: UserUpdateForm,
    session: Session = Depends(create_session),
    _: None = Depends(authorize_user) # enforce authority of user
):
    payload_empty: bool = len(payload.model_dump(exclude_unset=True, exclude_none=True)) == 0
    if payload_empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="payload cannot be empty"
        )
    UserManager(session).update_user(target_user_id, payload)