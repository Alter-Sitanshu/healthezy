# fastapi imports
from fastapi import Depends, APIRouter, status, HTTPException

# database imports
from sqlalchemy.orm import Session
from ....database.sessions import create_session

# security imports
from ....auth.dependencies import user_auth_guard, enforce_admin_privilege #, get_tenant_id, verify_tenant

# utility imports
from ....auth.service import AuthService
from ....auth.models import AdminForm
from ....database.models.response_models import UserResponse

router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_hospital_admin(
    form: AdminForm,
    # tenant_id: int = Depends(get_tenant_id),
    session: Session = Depends(create_session),
    _: None = Depends(enforce_admin_privilege)
) -> UserResponse:
    service = AuthService(session)

    # if not await verify_tenant(tenant_id, session):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="invalid tenant, access denied"
    #     )
    
    return await service.create_hospital_admin(form)

router.get("/{id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_hospital_admin(
    id: int,
    session: Session = Depends(create_session),
    # tenant_id: int = Depends(get_tenant_id)
) -> UserResponse:
    try:
        return AuthService(session).get_hospital_admin(
            id#, tenant_id
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="malformed request. access denied"
        )