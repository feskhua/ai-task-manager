from fastapi import HTTPException, status
from pydantic import SecretStr
from sqlalchemy.exc import SQLAlchemyError

from database.user_models import UserORM
from repositories.user_repo import UserRepository
from services.authentication_service import AuthenticationService
from schemas.user_schemas import UserCreate, UserPasswordUpdate


class UserService:
    """Service class for managing user-related business logic."""

    def __init__(
            self,
            user_repository: UserRepository,
            authentication_service: AuthenticationService
    ):
        """
        Initialize the UserService with required dependencies.

        Args:
            user_repository: Repository instance for user database operations
            authentication_service: Service instance for authentication operations
        """
        self.user_repository = user_repository
        self.authentication_service = authentication_service

    async def create_user(self, user_data: UserCreate) -> UserORM:
        """
        Create a new user with hashed password.

        Args:
            user_data: UserCreate schema containing user data including plain password

        Returns:
            UserORM: Created user object with basic information

        Raises:
            HTTPException: If user creation fails (400 status)
        """
        user_data.password = SecretStr(await self.authentication_service.get_password_hash(
            user_data.password.get_secret_value()
        ))
        user = await self.user_repository.create_user(user_data)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cant create user")

        return user

    async def get_user(self, user_id: int) -> UserORM:
        """
        Retrieve a user from the database by their ID.

        Args:
            user_id (int): The unique identifier of the user to fetch.

        Returns:
            UserORM: The user object retrieved from the database.

        Raises:
            HTTPException: If a database error occurs (500) or if the user is not found (404).
        """
        try:
            user = await self.user_repository.get_user_by_id(user_id)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user

    async def change_password(self, user_id: int, passwords: UserPasswordUpdate) -> UserORM:
        """
        Change a user's password after verifying their old password.

        Args:
            user_id (int): The unique identifier of the user whose password needs to be changed.
            passwords (UserPasswordUpdate): Object containing the old and new passwords.

        Returns:
            UserORM: The updated user object with the new password hash.

        Raises:
            HTTPException: If the old password doesn't match (400) or if a database error occurs (500).
        """
        user = await self.get_user(user_id)

        if not await self.authentication_service.verify_password(
                passwords.old_password.get_secret_value(),
                user.password
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password doesn't match"
            )

        hashed_password = await self.authentication_service.get_password_hash(
            passwords.password.get_secret_value()
        )

        try:
            user = await self.user_repository.update_user_password(user, hashed_password)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        return user
