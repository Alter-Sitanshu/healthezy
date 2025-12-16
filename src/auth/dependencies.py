from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from .service import AuthService
from ..database.models import UserResponse
from sqlalchemy.orm import Session
from ..database.sessions import create_session

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def user_auth_guard(
        request: Request,
        session: Session = Depends(create_session),
        token: str = Depends(oauth2_bearer)
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
    
    service = AuthService(session)

    try:
        user = service.get_user_from_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User unauthorized",
                headers={"WWW-Authenticate": "Bearer"},
            )
        request.state.user = user
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        )