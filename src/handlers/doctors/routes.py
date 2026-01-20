from fastapi import APIRouter, Request, Depends, status
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .models import NewDoctorForm, DoctorUpdateForm, DoctorLoginRequest, ResetPasswordForm
from .service import DoctorService
from ...database.models.response_models import (
    DoctorResponse, UserResponse
)
from ...database.sessions import create_session
from sqlalchemy.orm import Session
from ...auth.dependencies import user_auth_guard, authorise_hospital_privilege#, get_tenant_id
from ...auth.models import TokenSchema
from typing import List


router = APIRouter()

bearer_scheme = HTTPBearer(scheme_name="Authorization: Bearer ", auto_error=False)
def doctor_auth_guard(
        request: Request,
        session: Session = Depends(create_session),
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ) -> DoctorResponse | None:
    """
    FastAPI dependency that:
    - extracts bearer token
    - validates JWT
    - returns authenticated doctor context
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    service = DoctorService(session)
    jwt_token: str = token.credentials
    try:
        doc = service.get_doctor_from_token(jwt_token)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        request.state.doctor = doc
        return doc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

secure_router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

@secure_router.post("/", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
async def create_doctor(
    request: Request,
    form: NewDoctorForm,
    session: Session = Depends(create_session),
    _: None = Depends(authorise_hospital_privilege),
    # tenant_id: int = Depends(get_tenant_id),
) -> TokenSchema:
    """
    Docstring for create_doctor
    
    :param form: form for the new doctor's details
    :type form: NewDoctorForm
    :return: Doctor login Token and Doctor Code
    :rtype: TokenSchema
    - created by is user.id
    """
    current_user: UserResponse = request.state.user

    res = await DoctorService(session).create_doctor(
            form,
            # tenant_id,
            created_by=current_user.id
        )
    
    return TokenSchema(
        token_type=res["doc_code"],
        access_token=res["token"],
        # token is a temporary first use password
    )

@secure_router.put("/reset_password", status_code=status.HTTP_200_OK)
async def reset_password(
    request: Request,
    form: ResetPasswordForm,
    session: Session = Depends(create_session)
) -> None:
    try:
        doc: DoctorResponse = request.state.doctor
        DoctorService(session).reset_password(
            doc.id, form.old_password, form.new_password,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=TokenSchema)
async def login_doctor(
    form: DoctorLoginRequest,
    session: Session =  Depends(create_session)
) -> TokenSchema | None:
    try:
        schema = DoctorService(session).authenticate(
            form.doctor_code, form.password
        )

    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="doctor code or password incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return schema


@router.get("/specialization/{specialization}", response_model=List[DoctorResponse],
            status_code=status.HTTP_200_OK)
async def get_doctors_by_specialization(
    request: Request,
    specialization: str,
    session: Session = Depends(create_session)
) -> List[DoctorResponse]:
    return DoctorService(session).get_doctor_by_spec(specialization)

@router.get("/experience/{experience}", response_model=List[DoctorResponse],
            status_code=status.HTTP_200_OK)
async def get_doctors_by_experience(
    request: Request,
    experience: int,
    session: Session = Depends(create_session)
) -> List[DoctorResponse]:
    return DoctorService(session).get_doctor_by_experience(experience)

@router.get("/{id}", response_model=DoctorResponse,
            status_code=status.HTTP_200_OK, name="By Id")
async def get_doctor_by_id(
    request: Request,
    id: int,
    session: Session = Depends(create_session)
) -> DoctorResponse | None:
    response = DoctorService(session).get_doctor_by_id(id)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid arguments"
        )

    return response

@secure_router.put("/{doctor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_doctor_details(
    request: Request,
    doctor_id: int,
    form: DoctorUpdateForm,
    session: Session = Depends(create_session),
    _: None = Depends(authorise_hospital_privilege)
) -> None:
    updates: str = form.model_dump_json(exclude_none=True, exclude_unset=True)
    if len(updates) == 0:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="empty update payload"
            )
    try:
        await DoctorService(session).update_doctor(doctor_id, form.model_dump(exclude_none=True))
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"could not update doctor <Id:{doctor_id}>"
        )
    
@secure_router.delete("/{doctor_id}", status_code=status.HTTP_200_OK)
async def delete_doctor(
    request: Request,
    doctor_id: int,
    session: Session = Depends(create_session),
    _: None = Depends(authorise_hospital_privilege)
) -> None:
    try:
        DoctorService(session).delete_doctor(doctor_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

router.include_router(
    secure_router
)