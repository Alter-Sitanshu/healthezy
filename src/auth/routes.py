from fastapi import APIRouter, Depends, status, HTTPException
import logging
from ..settings import get_settings

# Model and Service imports
from .models import (
    TokenSchema,
    OTPVerifyRequest, OTPResponse,
    SignUpForm, BasicSignUpForm, 
    LoginRequest, AdminForm
)
from .service import AuthService

# Database and Manager imports
from sqlalchemy.orm import Session
from ..database.sessions import create_session

settings = get_settings()
# logger initiation
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename=settings.logs_file)
file_handler.setLevel(settings.log_level)
file_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"))
logger.addHandler(file_handler)

router = APIRouter()
"""
    /login -> POST to generate token
    /signup -> POST to register a new user
    /signup_potential_user -> POST to register a new potential user
    /resend-otp -> GET to regenerate otp for the required user
    /verify-otp -> POST to verify the user's OTP (returns the token with it)
"""

@router.post("/signup", status_code=status.HTTP_201_CREATED, response_model=TokenSchema,
             name="Step 1: Sign up new user")
async def signup(
    payload: SignUpForm,
    session: Session = Depends(create_session)
) -> TokenSchema:
    service = AuthService(session)
    await service.create_user(payload)
    token: str = service.create_access_token(payload.email)
    return TokenSchema(
        access_token=token,
        token_type="Bearer"
    )

@router.post("/potential_user", status_code=status.HTTP_201_CREATED, 
             response_model=TokenSchema, name="Step 1: register a user", deprecated=True)
async def register_temp_user(
   payload: BasicSignUpForm,
   session: Session = Depends(create_session)
) -> TokenSchema:
    service = AuthService(session)
    user_exists: bool = service.user_exists(payload.email)
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user already exists"
        )
    service.create_temp_user(payload, "5678")
    # return the otp to the client
    return TokenSchema(
        access_token="5678",
        token_type="otp"
    )
    

@router.post("/login", response_model=TokenSchema,
            description="role can be user, hospital-admin, or doctor")
async def login(
    AuthForm: LoginRequest,
    session: Session = Depends(create_session),
) -> TokenSchema | None:
   """
   Creates a JWT Token for the user and returns it
   Mainly for login functionality
   
   :param AuthForm: Form accepting role, email and password
   :type AuthForm: LoginRequest
   :param session: Scoped session for DB operations
   :type session: Session
   :return: Token object with acces_token and toke_type
   :rtype: TokenSchema | None
   """
   try:
        service = AuthService(session)
        output = service.authenticate(
            AuthForm.role,
            AuthForm.email, AuthForm.password
        )
        logger.info("<{}> : <{}> logged in".format(AuthForm.role, AuthForm.email))
        return output
   except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="email or password incorrect"
        )     


@router.get("/resend-otp", response_model=TokenSchema, status_code=status.HTTP_200_OK, deprecated=True)
async def resend_otp(
    identifier: str,
    is_email: bool = False,
    session: Session = Depends(create_session),
) -> TokenSchema:
    """
    Re-generates new OTP for the potential user
    
    :param session: Description
    :type session: Session
    :param payload: user credentials to generate another OTP
    :type payload: OTPVerifyRequest
    :return: New OTP for the user requested
    :rtype: TokenSchema
    """
    success = await AuthService(session).regenerate_otp(
        identifier,
        is_email
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="could not regenerate otp. user does not exist"
        )
    return TokenSchema(
        access_token="5678",
        token_type="Bearer"
    )


@router.put("/verify-otp", response_model=OTPResponse, status_code=status.HTTP_200_OK,
             name="Step 2: Verify the OTP", deprecated=True)
async def verify_otp(
    payload: OTPVerifyRequest,
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
    email = service.verify_otp(
        payload.identifier, 
        payload.is_email, 
        payload.otp
    )
    
    if email is None:
        return OTPResponse(message="OTP verification failed", token=None)
    
    
    return OTPResponse(
        message="User verified successfully",
        token=None
    )


admin_router = APIRouter()

@admin_router.post("/", status_code=status.HTTP_201_CREATED, response_model=TokenSchema)
async def create_superadmin(
    form: AdminForm,
    session: Session = Depends(create_session)
) -> TokenSchema:
    service =  AuthService(session)
    await service.create_admin(form)
    access_token: str = service.create_access_token(form.email)

    return TokenSchema(
        access_token=access_token,
        token_type="Bearer"
    )