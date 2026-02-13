# fastapi imports
from fastapi import Request, Depends, HTTPException, APIRouter, status
from ...auth.dependencies import user_auth_guard, enforce_hospital_privilege#, get_tenant_id

# database imports
from ...database.models.response_models import HospitalResponse, UserResponse, DoctorResponse
from sqlalchemy.orm import Session
from ...database.sessions import create_session

# model imports
from .models import HospitalForm, HospitalUpdateForm, Location
from .service import HospitalService

from typing import List

router = APIRouter()
secure_router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

@secure_router.post("/", response_model=HospitalResponse,
            status_code=status.HTTP_201_CREATED, dependencies=[Depends(enforce_hospital_privilege)]
        )
async def create_hospital(
    request: Request,
    form: HospitalForm,
    session: Session = Depends(create_session),
    # tenant_id: int = Depends(get_tenant_id),
    # only hospital admins and superadmin can create/register a hospital
) -> HospitalResponse:
    
    current_user: UserResponse = request.state.user
    return await HospitalService(
        session
    ).create_hospital(form, created_by=current_user.id)

@secure_router.put("/{hospital_code}", status_code=status.HTTP_200_OK,
        dependencies=[Depends(enforce_hospital_privilege)]
    )
async def update_hospital_details(
    request: Request,
    hospital_code: str,
    update_form: HospitalUpdateForm,
    session: Session = Depends(create_session)
) -> None:
    is_payload_empty = len(update_form.model_dump_json(exclude_none=True)) == 0
    if is_payload_empty:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="empty update payload"
            )
    try:
        HospitalService(session).update_details(
            update_form.model_dump(exclude_none=True), 
            hospital_code,
            request.state.user.id,
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"cannot update hospital details for <{hospital_code}>"
        )

@secure_router.delete("/{hospital_code}", status_code=status.HTTP_200_OK,
        dependencies=[Depends(enforce_hospital_privilege)]
    )
async def delete_hospital(
    request: Request,
    hospital_code: str,
    session: Session = Depends(create_session)
) -> None:
    try:
        HospitalService(session).delete(
            hospital_code, request.state.user.id
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"could not delete hospital <{hospital_code}>"
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

router.include_router(secure_router)