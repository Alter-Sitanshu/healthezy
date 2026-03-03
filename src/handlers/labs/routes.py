# fastapi imports
from fastapi import Request, Depends, HTTPException, APIRouter, status
from ...auth.dependencies import user_auth_guard, enforce_lab_admin_privilege, enforce_admin_privilege

# database imports
from ...database.models.response_models import LabResponse, LabTestResponse, UserResponse
from sqlalchemy.orm import Session
from ...database.sessions import create_session

# model imports
from ...auth.models import SignUpForm
from .models import NewLab, NewLabTest, LabUpdates, Location
from .service import LabService

# auth service imports
from ...auth.service import AuthService

from typing import List

# Public router for publicly accessible endpoints
router = APIRouter()

# Secure router for authenticated admin endpoints
secure_router = APIRouter(
    dependencies=[Depends(user_auth_guard), Depends(enforce_lab_admin_privilege)]
)


# ==================== PUBLIC ROUTES ====================
@router.post(
    "/admin/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(enforce_admin_privilege)]
)
async def create_lab_admin(
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
    
    return await service.create_lab_admin(form)


@router.get("/", 
    status_code=status.HTTP_200_OK, 
    response_model=List[LabResponse],
)
async def get_all_labs(
    session: Session = Depends(create_session)
) -> List[LabResponse]:
    """Get all active labs (Public - No authentication required)"""
    return LabService(session).get_all_labs()


@router.get("/code/{lab_code}", 
    response_model=LabResponse, 
    status_code=status.HTTP_200_OK,
)
async def get_lab_by_code(
    lab_code: str,
    session: Session = Depends(create_session)
) -> LabResponse:
    """Get lab by code (Public - No authentication required)"""
    lab: LabResponse | None = LabService(session).get_lab_by_code(lab_code)
    if lab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab with code {lab_code} not found"
        )
    return lab

@router.get("/{lab_id}", 
    response_model=LabResponse, 
    status_code=status.HTTP_200_OK,
)
async def get_lab_by_id(
    lab_id: int,
    session: Session = Depends(create_session)
) -> LabResponse:
    """Get lab by ID (Public - No authentication required)"""
    lab: LabResponse | None = LabService(session).get_lab_by_id(lab_id)
    if lab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab with ID {lab_id} not found"
        )
    return lab


@router.get("/city/{city}", 
    response_model=List[LabResponse], 
    status_code=status.HTTP_200_OK,
)
async def get_labs_by_city(
    city: str,
    session: Session = Depends(create_session)
) -> List[LabResponse]:
    """Get all labs in a specific city (Public - No authentication required)"""
    return LabService(session).get_labs_by_city(city)

@router.get("/nearby", 
    response_model=List[LabResponse], 
    status_code=status.HTTP_200_OK,
)
async def get_labs_nearby(
    loc: Location = Depends(),
    session: Session = Depends(create_session)
) -> List[LabResponse]:
    """Get all labs in a specific city (Public - No authentication required)"""
    return LabService(session).get_labs_nearby(
        loc.latitude,
        loc.longitude,
        loc.radius_km,
    )


@router.get("/{lab_id}/tests", 
    response_model=List[LabTestResponse], 
    status_code=status.HTTP_200_OK,
)
async def get_lab_tests(
    lab_id: int,
    session: Session = Depends(create_session)
) -> List[LabTestResponse]:
    """Get all available tests for a lab (Public - No authentication required)"""
    # Get lab by code first
    lab: LabResponse | None = LabService(session).get_lab_by_id(lab_id)
    if lab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab with ID {lab_id} not found"
        )
    
    return LabService(session).get_lab_tests(lab.id)


# ==================== SECURED ROUTES ====================
@secure_router.post("/applications", 
    response_model=LabResponse,
    status_code=status.HTTP_201_CREATED,
)
async def submit_lab_application(
    request: Request,
    lab_data: NewLab,
    session: Session = Depends(create_session),
) -> LabResponse:
    """Submit the New Lab registration form"""
    current_user: UserResponse = request.state.user
    return await LabService(session).submit_lab_application(lab_data, submitted_by=current_user.id)

@secure_router.patch(
    "/applications/{application_id}/withdraw", 
    status_code=status.HTTP_200_OK,
)
async def withdraw_application(
    request: Request,
    application_id: int,
    session: Session = Depends(create_session)
) -> None:
    try:
        LabService(session).withdraw(application_id, request.state.user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@secure_router.put("/{lab_id}", 
    status_code=status.HTTP_200_OK,
)
async def update_lab(
    request: Request,
    lab_id: int,
    update_data: LabUpdates,
    session: Session = Depends(create_session)
) -> dict[str, str]:
    """Update lab details (Admin only)"""
    payload = update_data.model_dump(exclude_none=True)
    if not payload or len(payload) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    
    try:
        LabService(session).update_lab(
            lab_id,
            request.state.user.is_superuser,
            payload,
            request.state.user.id,
        )
        return {"message": f"Lab {lab_id} updated successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update lab: {str(e)}"
        )


@secure_router.delete("/{lab_id}", 
    status_code=status.HTTP_200_OK,
)
async def delete_lab(
    request: Request,
    lab_id: int,
    session: Session = Depends(create_session)
) -> dict[str, str]:
    """Delete a lab (Admin only)"""
    try:
        admin_id: int | None = None
        if not request.state.user.is_superuser:
            admin_id = request.state.user.id
        LabService(session).delete_lab(lab_id, admin_id)
        return {"message": f"Lab {lab_id} deleted successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete lab: {str(e)}"
        )


@secure_router.post("/{lab_id}/tests", 
    response_model=LabTestResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_lab_test(
    request: Request,
    lab_id: int,
    test_data: NewLabTest,
    session: Session = Depends(create_session),
) -> LabTestResponse:
    """Add a new test to a lab (Admin only)"""
    
    try:
        current_user: UserResponse = request.state.user
        return await LabService(session).create_lab_test(lab_id, test_data, created_by=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot create lab test: {str(e)}"
        )


@secure_router.delete("/{lab_id}/tests/{test_id}", 
    status_code=status.HTTP_200_OK,
)
async def delete_lab_test(
    request: Request,
    lab_id: int,
    test_id: int,
    session: Session = Depends(create_session)
) -> dict[str, str]:
    """Delete a lab test (Admin only)"""
    # Verify lab exists
    lab: LabResponse | None = LabService(session).get_lab_by_id(lab_id)
    if lab is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lab with ID {lab_id} not found"
        )
    
    # Verify test exists and belongs to this lab
    test = LabService(session).get_lab_test_by_id(test_id)
    if test is None or test.lab_id != lab.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with id {test_id} not found in lab {lab_id}"
        )
    
    try:
        LabService(session).delete_lab_test(test_id)
        return {"message": f"Test {test_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete test: {str(e)}"
        )


router.include_router(secure_router)