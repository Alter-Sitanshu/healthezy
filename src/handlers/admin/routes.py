from fastapi import APIRouter, status, Depends
from ...auth.service import AuthService
from .service import AdminService

# dependencies
from ...auth.dependencies import enforce_admin_privilege

# model imports
from ...auth.models import TokenSchema, AdminForm
from ...database.models.response_models import UserResponse, PatientResponse

# database imports
from ...database.sessions import create_session
from sqlalchemy.orm import Session

# utility imports
from typing import List, Literal, Any


router = APIRouter()
secure_router = APIRouter(
    dependencies=[Depends(enforce_admin_privilege)]
)
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TokenSchema)
async def create_superadmin(
    form: AdminForm,
    session: Session = Depends(create_session)
) -> TokenSchema:
    service =  AuthService(session)
    await service.create_admin(form)
    access_token: str = service.create_access_token(form.email)

    return TokenSchema(
        access_token=access_token,
        token_type="Bearer"
    )

@secure_router.get(
    "/applications/{for_}", 
    status_code=status.HTTP_200_OK,
    response_model=List[Any]
)
async def get_applications(
    for_: Literal["hospital", "lab"],
    session: Session = Depends(create_session)
) -> List[Any]:
    return AdminService(session).get_applications(for_)

@secure_router.get(
    "/users", 
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_all_users(
    active: bool = False,
    session: Session = Depends(create_session)
) -> List[UserResponse]:
    return AdminService(session).get_users(active)

@secure_router.get(
    "/patients",
    response_model=List[PatientResponse], 
    status_code=status.HTTP_200_OK
)
async def get_all_patients(
    session: Session = Depends(create_session)
) -> List[PatientResponse]:
    return AdminService(session).get_patients()


@secure_router.patch(
    "/{entity}/approve/{id_}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def approve_entity(
    entity: Literal["hospitals", "labs"],
    id_: int,
    session: Session = Depends(create_session)
) -> None:
   AdminService(session).approve(entity, id_) 

@secure_router.patch(
    "/{entity}/reject/{id_}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def reject_entity(
    entity: Literal["hospitals", "labs"],
    id_: int,
    session: Session = Depends(create_session)
) -> None:
   AdminService(session).reject(entity, id_) 

@secure_router.get(
    "/provider_admin",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK
)
async def get_provider_admins(
    provider: Literal["hospital", "lab"] = Depends(),
    isactive: bool | None = None,
    session: Session = Depends(create_session)
) -> List[UserResponse]:
    return AdminService(session).get_provider_admins(
        provider = provider, isactive = isactive,
    )


router.include_router(secure_router)