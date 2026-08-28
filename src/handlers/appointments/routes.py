from fastapi import APIRouter, status, HTTPException, Depends, Request
from .models import *
from .service import AppointmentService
from ...exceptions import ManagerException

# database imports
from ...database.sessions import create_session
from ...database.models.response_models import AppointmentResponse
from sqlalchemy.orm import Session

# util imports
from typing import List
from datetime import datetime

# dependency
from ...auth.dependencies import user_auth_guard
from ...handlers.doctors.routes import doctor_auth_guard

router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)

doctor_router = APIRouter(
    dependencies=[Depends(doctor_auth_guard)]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AppointmentResponse)
async def create_appointment(
    request: Request,
    form: AppointmentRequest,
    session: Session = Depends(create_session)
) -> AppointmentResponse:
    
    try:
        return AppointmentService(session).create_appointment(form)
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="could not create appointment, try again"
        )

@router.put("/cancel/{appointment_id}", status_code=status.HTTP_200_OK)
async def cancel_appointment(
    request: Request,
    appointment_id: int,
    session: Session = Depends(create_session)
) -> None:
    current_user = request.state.user
    try:
        AppointmentService(session).cancel_appointment(
            current_user.id, appointment_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.put("/{appointment_id}", status_code=status.HTTP_200_OK)
async def update_appointment(
    request: Request,
    appointment_id: int,
    form: UpdateAppointment,
    session: Session = Depends(create_session)
) -> None:
    current_user = request.state.user
    try:
        AppointmentService(session).update_appointment(
            current_user.id, appointment_id, form
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

@router.get("/my", status_code=status.HTTP_200_OK,
        response_model=List[AppointmentResponse])
async def get_my_appointments(
    request: Request,
    session: Session = Depends(create_session)
) -> List[AppointmentResponse]:
    current_user = request.state.user
    try:
        return AppointmentService(session).get_my_appointments(current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@doctor_router.patch("/invalidate/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def invalidate_appointment(
    request: Request,
    appointment_id: int,
    session: Session = Depends(create_session)
) -> None:
    try:
        AppointmentService(session).invalidate(appointment_id, request.state.doctor.id)
    except ManagerException:
        raise HTTPException(
            detail="invalid credentials",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except:
        raise HTTPException(
            detail="server errror",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

@doctor_router.patch("/completed/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def mark_appointment_completed(
    request: Request,
    check_in: datetime,
    check_out: datetime,
    appointment_id: int,
    session: Session = Depends(create_session)
) -> None:
    try:
        AppointmentService(session).mark_completed(
            appointment_id, 
            request.state.doctor.id,
            {
                "in": check_in,
                "out": check_out
            }
        )
    except ManagerException:
        raise HTTPException(
            detail="invalid credentials",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except:
        raise HTTPException(
            detail="server errror",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

router.include_router(
    doctor_router
)