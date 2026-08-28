# fastapi imports
from fastapi import Request, Depends, APIRouter, status, HTTPException

# database imports
from sqlalchemy.orm import Session
from ...database.sessions import create_session

# security imports
from ...auth.dependencies import (
    require_role,
    user_auth_guard #, get_tenant_id, verify_tenant
)
from .models import AppointmentFilter

# utility imports
from ...auth.service import AuthService
from .service import HospitalService
from ...auth.models import SignUpForm, UserRoles
from ...database.models.response_models import UserResponse, HospitalResponse, AppointmentResponse
from typing import List

secure_router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

router = APIRouter()

@router.post(
    "/", 
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
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
    
    return await service.create_hos_admin(form)

@secure_router.get("/{admin_id}", response_model=UserResponse, status_code=status.HTTP_200_OK)
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
        return AuthService(session).get_user_by_id(
            admin_id#, tenant_id
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="malformed request. access denied"
        )

@secure_router.get("/my_hospital", response_model=HospitalResponse)
async def get_my_hospital(
    admin: UserResponse = Depends(require_role(UserRoles.HOS)),
    session: Session = Depends(create_session)
) -> HospitalResponse | None:
    try:
        output = HospitalService(session).get_hospital_by_id(admin.hospital_id)
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

@secure_router.get(
    "/my_hospital/appointments", 
    response_model=List[AppointmentResponse], 
    status_code=status.HTTP_200_OK)
async def get_my_hospital_appointments(
    admin: UserResponse = Depends(require_role(UserRoles.HOS)),
    filters: AppointmentFilter = Depends(),
    session: Session = Depends(create_session)
) -> List[AppointmentResponse]:
    try:
        if admin.hospital_id is None:
            raise HTTPException(
                detail="invalid request. no hospital found",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        return HospitalService(session).get_hospital_appointments(
            hospital_id = admin.hospital_id,
            filters = filters.model_dump(exclude_none=True)
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error fetching hospital appointments"
        )
    
@secure_router.put(
    "/add/{doctor_id}", 
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="ONLY FOR HOS-ADMIN"    
)
async def add_doctor(
    doctor_id: int,
    admin: UserResponse = Depends(require_role(UserRoles.HOS)),
    session: Session = Depends(create_session)
) -> None:
    """
        this method adds an existing doctor to a new organistaion(hos/clinic)
        if the doctor already belongs to some hos/clinic, this throws error 400
        if the doctor id is not valid this throws a error 404 -> redirect the user to 
        create a new doctor page
    """
    try:
        if admin.hospital_id is None:
            raise HTTPException(
                detail="invalid request. no hospital found",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        HospitalService(session).add_doctor(
            admin.hospital_id, doctor_id
        )
    except NameError:
        raise HTTPException(
            detail="invalid credentials entered",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        raise HTTPException(
            detail="method not allowed",
            status_code=status.HTTP_400_BAD_REQUEST
        )


@secure_router.put(
    "/{hospital_id}/add/{doctor_id}", 
    response_model=None,
    status_code=status.HTTP_200_OK,
    description="ONLY FOR ADMINS. Addition of doctor to any hospital"
)
async def add_doctor_to_hos(
    hospital_id: int,
    doctor_id: int,
    admin: UserResponse = Depends(require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN)),
    session: Session = Depends(create_session)
) -> None:
    """
        this method is only for admins !!
        adds an existing doctor to a new organistaion(hos/clinic)
        if the doctor already belongs to some hos/clinic, this throws error 400
        if the doctor id is not valid this throws a error 404 -> redirect the user to 
        create a new doctor page
    """
    try:
        HospitalService(session).add_doctor(
            hospital_id, doctor_id
        )
    except NameError:
        raise HTTPException(
            detail="invalid credentials entered",
            status_code=status.HTTP_404_NOT_FOUND
        )
    except ValueError:
        raise HTTPException(
            detail="method not allowed",
            status_code=status.HTTP_400_BAD_REQUEST
        )



router.include_router(secure_router)