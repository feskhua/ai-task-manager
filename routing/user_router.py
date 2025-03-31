from typing import Annotated

from fastapi import APIRouter, Depends
from schemas.user_schemas import UserCreate, UserRead, UserPasswordUpdate
from depends import get_user_service, get_current_user
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserRead)
async def read_users_me(
        current_user_data: Annotated[UserRead, Depends(get_current_user)]
):
    """
    Retrieve information about the current authenticated user.

    Args:
        current_user_data: Tuple with current user data (UserRead, token)

    Returns:
        UserRead: Basic user information of the authenticated user
    """
    return current_user_data[0]

@router.post("/create", response_model=UserRead)
async def create_user(
        user_data: UserCreate,
        user_service: UserService = Depends(get_user_service),
):
    """
    Create a new user.

    Args:
        user_data: UserCreate schema with user creation data
        user_service: Dependency-injected UserService instance

    Returns:
        UserRead: Created user with basic information

    Raises:
        HTTPException: If user creation fails (handled by UserService)
    """
    user = await user_service.create_user(user_data)
    return user

@router.post("/me/password", response_model=UserRead)
async def update_password(
        passwords: UserPasswordUpdate,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        user_service: UserService = Depends(get_user_service),
):
    """
    Update the password for the currently authenticated user.

    Args:
        passwords (UserPasswordUpdate): Object containing the old and new passwords.
        current_user_data (Annotated[UserRead, Depends(get_current_user)]):
            The authenticated user's data obtained from dependency injection.
        user_service (UserService, optional):
            The user service instance obtained from dependency injection.
            Defaults to result of get_user_service.

    Returns:
        UserRead: The updated user object in the response model format.

    Note:
        This endpoint requires authentication and uses the current user's ID
        to update their password through the user service.
    """
    user_id = current_user_data[0].id
    user = await user_service.change_password(user_id, passwords)
    return user
