# fastapi imports
from fastapi import Depends, HTTPException, APIRouter, status
from ...auth.dependencies import user_auth_guard, require_role#, get_tenant_id
from ...auth.models import UserRoles

# database imports
from ...database.models.response_models import (
    HospitalResponse, UserResponse,
    DoctorResponse, AppointmentResponse
)
from sqlalchemy.orm import Session
from ...database.sessions import create_session

# model imports
from .models import HospitalForm, HospitalUpdateForm, Location, AppointmentFilter
from .service import HospitalService

from typing import List, Any


router = APIRouter()
secure_router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

@secure_router.post("/applications", response_model=HospitalResponse,
        status_code=status.HTTP_201_CREATED
    )
async def submit_hospital_application(
    form: HospitalForm,
    admin: UserResponse = Depends(require_role(UserRoles.HOS, UserRoles.SUPERADMIN, UserRoles.ADMIN)),
    session: Session = Depends(create_session),
    # tenant_id: int = Depends(get_tenant_id),
    # only hospital admins and superadmin can create/register a hospital
) -> HospitalResponse:
    
    return await HospitalService(
        session
    ).submit_hospital_application(form, submitted_by=admin.id)


@secure_router.patch(
    "/applications/{application_id}/withdraw", 
    status_code=status.HTTP_200_OK
)
async def withdraw_application(
    application_id: int,
    admin: UserResponse = Depends(require_role(UserRoles.HOS, UserRoles.SUPERADMIN, UserRoles.ADMIN)),
    session: Session = Depends(create_session)
) -> None:
    try:
        HospitalService(session).withdraw(application_id, admin.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@secure_router.put("/{hospital_id}", status_code=status.HTTP_200_OK)
async def update_hospital_details(
    hospital_id: int,
    update_form: HospitalUpdateForm,
    admin: UserResponse = Depends(require_role(UserRoles.HOS, UserRoles.SUPERADMIN, UserRoles.ADMIN)),
    session: Session = Depends(create_session)
) -> None:
    is_payload_empty = len(update_form.model_dump(exclude_none=True)) == 0
    if is_payload_empty:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="empty update payload"
            )
    try:
        updator: dict[str, Any] = {
                "is_admin": admin.is_superuser,
                "updator_id": admin.id
            }
        HospitalService(session).update_details(
            update_form.model_dump(exclude_none=True), 
            hospital_id,
            updator,
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"cannot update hospital details for <{hospital_id}>"
        )

@secure_router.delete("/delete/{hospital_id}", status_code=status.HTTP_200_OK)
async def delete_hospital(
    hospital_id: int,
    admin: UserResponse = Depends(require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN)),
    session: Session = Depends(create_session)
) -> None:
    try:
        HospitalService(session).mark_delete(
            hospital_id, admin.id
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"could not delete hospital <{hospital_id}>"
        )
    
@secure_router.put("/deactivate/{hospital_id}", status_code=status.HTTP_200_OK)
async def deactivate_hospital(
    hospital_id: int,
    admin: UserResponse = Depends(require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN, UserRoles.HOS)),
    session: Session = Depends(create_session)
) -> None:
    try:
        HospitalService(session).mark_delete(
            hospital_id, admin.id
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"could not delete hospital <{hospital_id}>"
        )


@router.get("/", status_code=status.HTTP_200_OK, response_model=List[HospitalResponse])
async def get_all_hospitals(
    session: Session = Depends(create_session)
) -> List[HospitalResponse]:
    
    return HospitalService(session).get_hospitals()


@router.get("/code/{hospital_code}", response_model=HospitalResponse, status_code=status.HTTP_200_OK)
async def get_hospital_by_code(
    hospital_code: str,
    session: Session = Depends(create_session)
) -> HospitalResponse:
    response: HospitalResponse | None = HospitalService(
        session
    ).get_hospital_by_code(hospital_code)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid hospital code"
        )
    
    return response

@router.get("/{hospital_id}", response_model=HospitalResponse, status_code=status.HTTP_200_OK)
async def get_hospital_by_id(
    hospital_id: int,
    session: Session = Depends(create_session)
) -> HospitalResponse:
    response: HospitalResponse | None = HospitalService(
        session
    ).get_hospital_by_id(hospital_id)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid hospital id"
        )
    
    return response

@router.get("/nearby", response_model=List[HospitalResponse], status_code=status.HTTP_200_OK)
async def get_hospitals_around(
    loc: Location = Depends(),
    session: Session = Depends(create_session)
) -> List[HospitalResponse]:
    return HospitalService(session).find_hospitals_around(
        loc.latitude,
        loc.longitude,
        loc.radius_km,
    )

@router.get("/city/{city}", status_code=status.HTTP_200_OK,
            response_model=List[HospitalResponse])
async def get_hospitals_by_specialization(
    city: str,
    session: Session = Depends(create_session)
) -> List[HospitalResponse]:
    return HospitalService(session).find_by_city(city)

@router.get("/type/{type}", status_code=status.HTTP_200_OK,
            response_model=List[HospitalResponse])
async def get_hospitals_by_type(
    type: str,
    session: Session = Depends(create_session)
) -> List[HospitalResponse]:
    return HospitalService(session).find_by_type(type)

@router.get("/{id}/doctors", response_model=List[DoctorResponse], 
            status_code=status.HTTP_200_OK)
async def get_hospital_doctors(
    id: int,
    session: Session = Depends(create_session)
) -> List[DoctorResponse]:
    try:
        return HospitalService(session).get_doctors(id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@secure_router.get(
    "/{hospital_id}/appointments",
    response_model=List[AppointmentResponse], 
    status_code=status.HTTP_200_OK)
async def get_hospital_appointments(
    hospital_id: int,
    filters: AppointmentFilter = Depends(),
    admin: UserResponse = Depends(
        require_role(
            UserRoles.SUPERADMIN, UserRoles.ADMIN, UserRoles.HOS
        )
    ),
    session: Session = Depends(create_session)
) -> List[AppointmentResponse]:
    try:
        return HospitalService(session).get_hospital_appointments(
            hospital_id = hospital_id,
            filters = filters.model_dump(exclude_none=True)
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error fetching hospital appointments"
        )
   
router.include_router(secure_router)