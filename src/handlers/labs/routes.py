# fastapi imports
from fastapi import Depends, HTTPException, APIRouter, status
from ...auth.dependencies import user_auth_guard, require_role, exclude_role

# database imports
from ...database.models.response_models import LabResponse, LabTestResponse, UserResponse
from sqlalchemy.orm import Session
from ...database.sessions import create_session

# model imports
from ...auth.models import SignUpForm, UserRoles
from .models import NewLab, NewLabTest, LabUpdates, Location
from .service import LabService

# auth service imports
from ...auth.service import AuthService

from typing import List

# Public router for publicly accessible endpoints
router = APIRouter()

# Secure router for authenticated admin endpoints
secure_router = APIRouter(
    dependencies=[Depends(user_auth_guard)]
)


# ==================== PUBLIC ROUTES ====================
@router.post(
    "/admin/register", 
    response_model=UserResponse, 
    status_code=status.HTTP_201_CREATED
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
    """Get all labs around a specific proximity (Public - No authentication required)"""
    return LabService(session).get_labs_nearby(
        loc.latitude,
        loc.longitude,
        loc.radius_km,
    )


@router.get("/{lab_id}/tests", 
    response_model=List[LabTestResponse], 
    status_code=status.HTTP_200_OK,
)
async def get_lab_offered_tests(
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
    lab_data: NewLab,
    admin: UserResponse = Depends(
        require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN, UserRoles.MOD, UserRoles.LAB)
    ),
    session: Session = Depends(create_session),
) -> LabResponse:
    """Submit the New Lab registration form"""
    return await LabService(session).submit_lab_application(
        lab_data, submitted_by=admin.id)

@secure_router.patch(
    "/applications/{application_id}/withdraw", 
    status_code=status.HTTP_200_OK,
    description='''
    Excludes the HOS-ADMINS and NORMAL user requests
    As they are not allowed to submit the application and thus access revoked here
    '''
)
async def withdraw_application(
    application_id: int,
    user: UserResponse = Depends(
        exclude_role(UserRoles.HOS, UserRoles.NORMAL, UserRoles.SUPPORT)
    ),
    session: Session = Depends(create_session)
) -> None:
    try:
        LabService(session).withdraw(application_id, user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@secure_router.put("/{lab_id}", 
    status_code=status.HTTP_200_OK,
)
async def update_lab(
    lab_id: int,
    update_data: LabUpdates,
    admin: UserResponse = Depends(
        exclude_role(UserRoles.SUPPORT, UserRoles.HOS, UserRoles.NORMAL)
    ),
    session: Session = Depends(create_session)
) -> None:
    """Update lab details (Admin only)"""
    payload = update_data.model_dump(exclude_none=True)
    if not payload or len(payload) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No data provided for update"
        )
    updator: dict[str, int | bool] = {
                "is_admin": admin.is_superuser,
                "updator_id": admin.id
            }
    try:
        LabService(session).update_lab(
            lab_id,
            payload,
            updator
        )
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


@secure_router.delete("/delete/{lab_id}", 
    status_code=status.HTTP_200_OK,
    description="ADMIN ONLY ACCESS"
)
async def delete_lab(
    lab_id: int,
    admin: UserResponse = Depends(require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN)),
    session: Session = Depends(create_session)
) -> None:
    """Delete a lab (Admin only)"""
    try:
        LabService(session).delete_lab(lab_id)
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

@secure_router.put("/deactivate/{lab_id}", 
    status_code=status.HTTP_200_OK,
)
async def mark_delete_lab(
    lab_id: int,
    admin: UserResponse = Depends(
        require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN, UserRoles.LAB)
    ),
    session: Session = Depends(create_session)
) -> None:
    """Delete a lab (Admin only)"""
    try:
        LabService(session).mark_delete_lab(lab_id, admin.id)
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
    lab_id: int,
    test_data: NewLabTest,
    admin: UserResponse = Depends(
        require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN, UserRoles.LAB)
    ),
    session: Session = Depends(create_session),
) -> LabTestResponse:
    """Add a new test to a lab (Admin only)"""
    
    try:
        return await LabService(session).create_lab_test(
            lab_id, test_data, created_by=admin.id)
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
    lab_id: int,
    test_id: int,
    admin: UserResponse = Depends(
        require_role(UserRoles.SUPERADMIN, UserRoles.ADMIN, UserRoles.LAB)
    ),
    session: Session = Depends(create_session)
) -> None:
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not delete test: {str(e)}"
        )


router.include_router(secure_router)