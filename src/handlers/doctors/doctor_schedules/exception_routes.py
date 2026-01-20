from fastapi import Request, APIRouter, Depends, status, HTTPException
from ....database.sessions import create_session
from sqlalchemy.orm import Session

from ..models import ScheduleExcPayload, UpdateException
from ....database.models.response_models import DoctorScheduleExpResp, DoctorResponse
from ..service import DoctorService
from ..routes import doctor_auth_guard

from typing import List
   
router = APIRouter()
secure_router = APIRouter(
    dependencies=[Depends(doctor_auth_guard)]
)


@secure_router.post("/{doctor_id}", status_code=status.HTTP_201_CREATED, response_model=DoctorScheduleExpResp)
async def create_schedule_exception(
    doctor_id: int,
    payload: ScheduleExcPayload,
    session: Session = Depends(create_session),
    # tenant_id: int = Depends(get_tenant_id)
) -> DoctorScheduleExpResp:
    
    try:
        return await DoctorService(session).add_exception(
            doctor_id,
            # tenant_id,
            payload,
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="could not add exception. try again"
        )
    

@secure_router.put("/{exception_id}", status_code=status.HTTP_200_OK)
async def update_schedule_exception(
    request: Request,
    exception_id: int,
    payload: UpdateException,
    session: Session = Depends(create_session)
) -> None:
    
    try:
        doc: DoctorResponse = request.state.doctor
        DoctorService(session).update_exception(
            doc.id, exception_id, payload
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@secure_router.delete("/{exception_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exception(
    request: Request,
    exception_id: int,
    session: Session = Depends(create_session)
) -> None:

    try:
        doc: DoctorResponse = request.state.doctor
        DoctorService(session).delete_exception(
            doc.id, exception_id
        )
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="doctor unauthorised"
        )

@router.get("/{doctor_id}", status_code=status.HTTP_200_OK,
        response_model=List[DoctorScheduleExpResp]            
)
async def doctor_schedule_exceptions(
    doctor_id: int,
    session: Session = Depends(create_session)
) -> List[DoctorScheduleExpResp]:

    return DoctorService(session).get_exceptions(doctor_id)

router.include_router(secure_router)