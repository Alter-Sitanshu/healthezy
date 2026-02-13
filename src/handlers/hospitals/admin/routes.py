# fastapi imports
from fastapi import Request, Depends, APIRouter, status, HTTPException

# database imports
from sqlalchemy.orm import Session
from ....database.sessions import create_session

# security imports
from ....auth.dependencies import (
    enforce_hospital_privilege,
    user_auth_guard, enforce_admin_privilege #, get_tenant_id, verify_tenant
) 

# utility imports
from ....auth.service import AuthService
from ..service import HospitalService
from ....auth.models import SignUpForm
from ....database.models.response_models import UserResponse, HospitalResponse

router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED,
        dependencies=[Depends(enforce_admin_privilege)]         
    )
async def create_hospital_admin(
    form: SignUpForm,
    # tenant_id: int = Depends(get_tenant_id),
    session: Session = Depends(create_session)
) -> UserResponse:
    service = AuthService(session)

    # if not await verify_tenant(tenant_id, session):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="invalid tenant, access denied"
    #     )
    
    return await service.create_user(form)

@router.get("/{admin_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_hospital_admin(
    request: Request,
    admin_id: int,
    session: Session = Depends(create_session),
    # tenant_id: int = Depends(get_tenant_id)
) -> UserResponse:
    try:
        current_user: UserResponse =  request.state.user
        if current_user.id != admin_id and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="unauthorised request. access denied"
            )
        return AuthService(session).get_hospital_admin(
            admin_id#, tenant_id
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="malformed request. access denied"
        )

@router.get("/my_hospital", response_model=HospitalResponse,
        dependencies=[Depends(enforce_hospital_privilege)]        
    )
async def get_my_hospital(
    request: Request,
    session: Session = Depends(create_session)
) -> HospitalResponse | None:
    try:
        current_user: UserResponse = request.state.user
        if current_user.is_superuser:
            raise HTTPException(
                detail="invalid request. no hospital found",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        
        output = HospitalService(session).get_hospital_by_id(current_user.hospital_id)
        if output is None:
            raise HTTPException(
                detail="invalid request. no hospital found",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return output
        
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="could not fetch admin hospital"
        )
