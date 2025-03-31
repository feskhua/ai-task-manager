from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from database.user_models import UserORM
from repositories.user_repo import UserRepository
from config import SECRET_KEY, ALGORITHM


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthenticationService:
    """Service class for handling user authentication operations."""

    def __init__(self, user_repository: UserRepository):
        """
        Initialize the AuthenticationService with a user repository.

        Args:
            user_repository: UserRepository instance for database operations
        """
        self.user_repository = user_repository

    async def authenticate(self, user_data) -> UserORM:
        """
        Authenticate a user based on provided credentials.

        Args:
            user_data: Object containing username and password

        Returns:
            UserORM: Authenticated user details

        Raises:
            HTTPException: If username or password is incorrect (400 status)
        """
        user = await self.user_repository.get_user_by_username(user_data.username)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password"
            )

        if not await self.verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username or password"
            )

        return user

    @staticmethod
    async def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain password against a hashed password.

        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against

        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    async def get_password_hash(password: str) -> str:
        """
        Generate a hashed version of a password.

        Args:
            password: Plain text password to hash

        Returns:
            str: Hashed password
        """
        return pwd_context.hash(password)

    @staticmethod
    async def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
        """
        Create a JWT access token with specified data and expiration.

        Args:
            data: Dictionary of data to encode in the token
            expires_delta: Optional timedelta for token expiration
                          (defaults to 15 minutes if None)

        Returns:
            str: Encoded JWT token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta

        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
