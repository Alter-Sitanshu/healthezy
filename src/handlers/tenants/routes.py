from fastapi import Request, Depends, HTTPException, APIRouter, status
from ...auth.dependencies import user_auth_guard, enforce_admin_privilege

# database imports
from ...database.models.response_models import TenantResponse, UserResponse
from sqlalchemy.orm import Session
from ...database.sessions import create_session

# model & service imports
from .models import TenantCreate
from .service import TenantService

from typing import List, Any

router = APIRouter(
	dependencies=[Depends(user_auth_guard), Depends(enforce_admin_privilege)]
)


@router.post("/", response_model=TenantResponse, status_code=status.HTTP_200_OK)
async def create_tenant(
	request: Request,
	form: TenantCreate,
	session: Session = Depends(create_session),
) -> TenantResponse:
	current_user: UserResponse = request.state.user
	if not current_user.is_superuser:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient privileges")

	created_by: str = f"{current_user.email}{current_user.phone_number[-4:]}"
	return await TenantService(session).create_tenant(form, created_by=created_by)


@router.get("/", response_model=List[TenantResponse], status_code=status.HTTP_200_OK)
async def list_tenants(session: Session = Depends(create_session)) -> List[TenantResponse]:
	return TenantService(session).list_tenants()


@router.get("/code/{tenant_code}", response_model=TenantResponse, status_code=status.HTTP_200_OK)
async def get_tenant_by_code(tenant_code: str, session: Session = Depends(create_session)) -> TenantResponse:
	response = TenantService(session).get_tenant_by_code(tenant_code)
	if response is None:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid tenant code")
	return response


@router.get("/{tenant_id}", response_model=TenantResponse, status_code=status.HTTP_200_OK)
async def get_tenant_by_id(tenant_id: int, session: Session = Depends(create_session)) -> TenantResponse:
	response = TenantService(session).get_tenant_by_id(tenant_id)
	if response is None:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="invalid tenant id")
	return response


@router.put("/{tenant_code}", status_code=status.HTTP_200_OK)
async def update_tenant(
	request: Request,
	tenant_code: str,
	update_form: dict[str, Any],
	session: Session = Depends(create_session),
) -> None:
	current_user: UserResponse = request.state.user
	if not current_user.is_superuser:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient privileges")

	is_payload_empty = len(update_form) == 0
	if is_payload_empty:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="empty update payload")

	try:
		TenantService(session).update_details(update_form, tenant_code)
	except Exception:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"cannot update tenant <{tenant_code}>")


@router.delete("/{tenant_code}", status_code=status.HTTP_200_OK)
async def delete_tenant(
	request: Request,
	tenant_code: str,
	session: Session = Depends(create_session),
) -> None:
	current_user: UserResponse = request.state.user
	if not current_user.is_superuser:
		raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="insufficient privileges")

	try:
		TenantService(session).delete(tenant_code)
	except Exception:
		raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"could not delete tenant <{tenant_code}>")


