from fastapi import Request, APIRouter, Depends, status, HTTPException
from ....database.sessions import create_session
from sqlalchemy.orm import Session

from ..models import SchedulePayload, ScheduleUpdatePayload, Slot
from ..service import DoctorService
from ..routes import doctor_auth_guard

from typing import List

router = APIRouter()

secure_router = APIRouter(
    prefix="/private",
    dependencies=[Depends(doctor_auth_guard)]
)

@router.get("/{schedule_id}", status_code=status.HTTP_200_OK)
async def get_schedule_by_id(
    schedule_id: int,
    session: Session = Depends(create_session),
) -> List[Slot]:
    return DoctorService(session).get_schedule(schedule_id)

@router.get("/{doctor_id}", status_code=status.HTTP_200_OK)
async def get_doctor_schedules(
    doctor_id: int,
    session: Session = Depends(create_session),
) -> List[Slot]:
    return DoctorService(session).get_doctor_schedules(doctor_id)
    

# ---- Secure/Protected routes for schedules -----

@secure_router.post("", status_code=status.HTTP_201_CREATED)
async def add_schedule(
    request: Request,
    schedule: SchedulePayload,
    session: Session = Depends(create_session),
    # tenant_id: int = Depends(get_tenant_id),
) -> None:
    success = DoctorService(session).add_schedule(schedule)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="could not add schedule. try again"
        )
    
@secure_router.put("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def edit_schedule(
    request: Request,
    schedule_id: int,
    payload: ScheduleUpdatePayload,
    session: Session = Depends(create_session),
) -> None:
    is_payload_empty = len(payload.model_dump_json(exclude_none=True)) == 0
    if is_payload_empty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="empty payload not allowed"
        )
    try:
        DoctorService(session).edit_schedule(schedule_id, payload.model_dump(exclude_none=True))
    except:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cannot update schedule. try again later"
        )

@secure_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_doctor_schedule(
    request: Request,
    id: int,
    session: Session = Depends(create_session),
) -> None:
    try:
        DoctorService(session).delete_schedule(id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
router.include_router(secure_router)