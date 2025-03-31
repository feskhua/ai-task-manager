from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from services.authentication_service import AuthenticationService
from depends import get_authentication_service
from schemas.auth_schemas import Token
from config import ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter(prefix="/token", tags=["Authentication"])


@router.post("/")
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        authentication_service: AuthenticationService = Depends(get_authentication_service)
) -> Token:
    """
    Authenticate a user and generate an access token.

    Args:
        form_data: OAuth2 password request form containing username and password
        authentication_service: Dependency-injected AuthenticationService instance

    Returns:
        Token: Object containing the access token and token type

    Raises:
        HTTPException: If authentication fails (handled by AuthenticationService)
    """
    user = await authentication_service.authenticate(form_data)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await authentication_service.create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
