from fastapi import Depends, HTTPException, status, Request#, Security
from fastapi.security import (
    HTTPBearer, HTTPAuthorizationCredentials,
    # APIKeyHeader
)
from .service import AuthService
from ..database.models.response_models import UserResponse#, TenantResponse
from sqlalchemy.orm import Session
from ..database.sessions import create_session

bearer_scheme = HTTPBearer(scheme_name="Authorization: Bearer ", auto_error=False)
# x_tenant_id = APIKeyHeader(
#     name="X-Tenant-ID",
#     scheme_name="X-Tenant-ID", 
#     auto_error=False
# )

async def user_auth_guard(
        request: Request,
        session: Session = Depends(create_session),
        token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
    ) -> UserResponse | None:
    """
    FastAPI dependency that:
    - extracts bearer token
    - validates JWT
    - returns authenticated user context
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if token.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    service = AuthService(session)
    jwt_token: str = token.credentials
    try:
        user = service.get_user_from_token(jwt_token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        request.state.user = user
        return user
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )

# async def get_tenant_id(
#     tenant_id: int = Security(x_tenant_id)
# ) -> int:
#     return tenant_id  

# async def verify_tenant(
#     tenant_id: int,
#     session: Session
# ) -> bool:
#     tenant: TenantResponse | None = AuthService(session).get_tenant(tenant_id)
#     if tenant is None:
#         return False

#     return True

async def enforce_hospital_privilege(
    request: Request
) -> None:
    try:
        current_user: UserResponse = request.state.user
        # if there is no logged in user this raises
        # a key error and the validation fails
        role: str = current_user.role.lower()
        if not current_user.is_superuser and (role != "hospital_admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="privileges required",
            )
    except Exception as e:
        # TODO: add logging
        raise ValueError(e)

async def enforce_admin_privilege(
    request: Request,
) -> None:
    try:
        current_user: UserResponse = request.state.user
        # if there is no logged in user this raises
        # a key error and the validation fails
        if not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="privileges required",
            )
    except Exception as e:
        # TODO: add loggging
        raise ValueError(e)