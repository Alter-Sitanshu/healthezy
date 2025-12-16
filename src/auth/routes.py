from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

# Model and Service imports
from .models import TokenSchema, OTPVerifyRequest, OTPResponse, SignUpForm
from .service import AuthService

# Database and Manager imports
from sqlalchemy.orm import Session
from ..database.sessions import create_session

router = APIRouter()
"""
    /token -> POST to generate token (login)
    /signup -> POST to register a new user
    /verify-otp -> POST to verify the user's OTP (returns the token with it)
"""

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def registerUser(
    payload: SignUpForm = Depends(),
    session: Session = Depends(create_session)
) -> None:
    service = AuthService(session)
    service.create_user(payload)

@router.post("/token", response_model=TokenSchema)
async def generateToken(
    AuthForm: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(create_session),
) -> TokenSchema | None:
   """
   Creates a JWT Token for the user and returns it
   Mainly for login functionality
   
   :param AuthForm: Form accepting username and password
   :type AuthForm: OAuth2PasswordRequestForm
   :param session: Scoped session for DB operations
   :type session: Session
   :return: Token object with acces_token and toke_type
   :rtype: TokenSchema | None
   """
   return AuthService(session).authenticate(
      AuthForm.username, AuthForm.password
    )

@router.post("/verify-otp", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def verifyUser(
    payload: OTPVerifyRequest = Depends(),
    session: Session = Depends(create_session),
) -> OTPResponse:
    """
        Verifies the OTP against the user credentials
    
    :param payload: accepts identifier, is_mail(default True), otp
    :type payload: OTPVerifyRequest
    :param session: Scoped session for DB operations
    :type session: Session
    :return: OTPResponse object with a message
    :rtype: OTPResponse
    """
    service = AuthService(session)
    result = service.verify_otp(
        payload.identifier, 
        payload.is_email, 
        payload.otp
    )
    
    if result is None:
        return OTPResponse(message="OTP verification failed", token=None)
    
    (username, email) = result
    token = service.create_access_token(username, email)
    return OTPResponse(
        message="User verified successfully",
        token=TokenSchema(
            access_token=token,
            token_type="bearer"
        )
    )
   