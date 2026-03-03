from sqlalchemy.orm import Session, load_only
from sqlalchemy import select, update
from .manager import BaseDatabase
from ...exceptions import ManagerException

from ..models.users import Tenant
from ..models.response_models import TenantResponse
from typing import Any, List

from pydantic import TypeAdapter


class TenantManager(BaseDatabase):
	def __init__(self, session: Session) -> None:
		super().__init__(session)
		self.adapter = TypeAdapter(List[TenantResponse])

	def add_tenant(self, tenant: Tenant) -> TenantResponse:
		try:
			self.add_one(tenant)
			return tenant.to_response()

		except Exception as e:
			raise ManagerException("Tenant", str(e))

	def get_tenant_by_id(self, id: int) -> TenantResponse | None:
		tenant: Tenant | None = self.get_one(
			select(Tenant)
			.options(load_only(Tenant.id, Tenant.tenant_code, Tenant.subdomain))
			.where(Tenant.id == id)
		)
		if tenant is None:
			return tenant

		return tenant.to_response()

	def get_tenant_by_code(self, tenant_code: str) -> TenantResponse | None:
		tenant: Tenant | None = self.get_one(
			select(Tenant).where(Tenant.tenant_code == tenant_code)
		)
		if tenant is None:
			return tenant

		return tenant.to_response()

	def get_tenant_by_subdomain(self, subdomain: str) -> TenantResponse | None:
		tenant: Tenant | None = self.get_one(
			select(Tenant).where(Tenant.subdomain == subdomain)
		)
		if tenant is None:
			return tenant

		return tenant.to_response()

	def update(self, payload: dict[str, Any], tenant_code: str) -> None:
		self.session.execute(
			update(Tenant).where(
				Tenant.tenant_code == tenant_code
			).values(payload)
		)
		self.session.commit()

	def delete(self, tenant_code: str) -> None:
		target: Tenant | None = self.get_one(
			select(Tenant).where(Tenant.tenant_code == tenant_code)
		)
		if target is None:
			raise ManagerException("Tenant", f"invalid tenant code<{tenant_code}>")

		self.delete_one(target)

	def list_all(self) -> List[TenantResponse]:
		tenants = self.get_all(select(Tenant))
		return self.adapter.validate_python(tenants)

