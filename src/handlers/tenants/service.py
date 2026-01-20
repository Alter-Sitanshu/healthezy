# database imports
from ...database.managers.manager import SessionMixin
from ...database.managers.tenants import TenantManager
from ...database.models.response_models import TenantResponse
from ...database.models.users import Tenant

# sqlalchemy imports
from sqlalchemy.orm import Session

# model imports
from .models import TenantCreate

# util imports
from uuid import uuid4
from typing import List, Any

class TenantService(SessionMixin):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._tenant_manager = TenantManager(session)
    
    async def create_tenant(self, payload: TenantCreate, created_by: str) -> TenantResponse:
        generated_code = f"TEN-{uuid4().hex[:8].upper()}"
        model = Tenant(
            tenant_code=generated_code,
            name=payload.name,
            description=payload.description,
            subdomain=payload.subdomain,
            contact_email=payload.contact_email,
            contact_phone=payload.contact_phone,
            address=payload.address,
            city=payload.city,
            state=payload.state,
            zip_code=payload.zip_code,
            country=payload.country,
            subscription_plan=payload.subscription_plan,
            status=payload.status,
            subscription_start_date=payload.subscription_start_date,
            subscription_end_date=payload.subscription_end_date,
            database_name=payload.database_name,
            max_users=payload.max_users,
            max_patients=payload.max_patients,
            max_doctors=payload.max_doctors,
            is_active=payload.is_active,
            created_by=created_by,
        )

        return self._tenant_manager.add_tenant(model)

    def get_tenant_by_id(self, id: int) -> TenantResponse | None:
        return self._tenant_manager.get_tenant_by_id(id)

    def get_tenant_by_code(self, tenant_code: str) -> TenantResponse | None:
        return self._tenant_manager.get_tenant_by_code(tenant_code)

    def update_details(self, payload: dict[str, Any], tenant_code: str) -> None:
        self._tenant_manager.update(payload, tenant_code)

    def delete(self, tenant_code: str) -> None:
        self._tenant_manager.delete(tenant_code)

    def list_tenants(self) -> List[TenantResponse]:
        return self._tenant_manager.list_all()