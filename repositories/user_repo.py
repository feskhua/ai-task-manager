import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


from database.user_models import UserORM
from schemas.user_schemas import UserCreate


logger = logging.getLogger(__name__)


class UserRepository:
    """Repository class for handling user-related database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the UserRepository with a database session.

        Args:
            db: AsyncSession instance for database operations
        """
        self.db = db

    async def create_user(self, user: UserCreate) -> UserORM | None:
        """
        Create a new user in the database.

        Args:
            user: UserCreate schema containing user data to create

        Returns:
            UserORM | None: Created user object with basic info if successful
        """
        new_user = UserORM(
            username=user.username,
            email=user.email,
            password=user.password.get_secret_value(),
        )
        self.db.add(new_user)
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        await self.db.refresh(new_user)
        return new_user

    async def get_user_by_id(self, user_id: int) -> UserORM | None:
        """
        Retrieve a user by their ID.

        Args:
            user_id: ID of the user to retrieve

        Returns:
            UserORM | None: User object with basic info if found, None otherwise
        """
        statement = select(UserORM).where(UserORM.id == user_id)

        try:
            result = await self.db.exec(statement)
        except SQLAlchemyError as e:
            logger.error(e)
            raise

        user = result.one_or_none()

        if user is None:
            return None

        return user

    async def get_user_by_username(self, username: str) -> UserORM | None:
        """
        Retrieve a user by their username with detailed information.

        Args:
           username: Username of the user to retrieve

        Returns:
           UserORM | None: User object or None
        """
        query = select(UserORM).where(UserORM.username == username)
        try:
            result = await self.db.exec(query)
        except SQLAlchemyError as e:
            logger.error(e)
            raise

        user = result.one_or_none()

        if user is None:
            return None

        return user

    async def update_user_password(self, user: UserORM, password: str) -> UserORM:
        """
        Update a user's password in the database.

        Args:
            user (UserORM): The user object to be updated.
            password (str): The new password hash to be set.

        Returns:
            UserORM: The updated user object with the new password.

        Raises:
            SQLAlchemyError: If a database error occurs during the commit operation.
        """
        user.password = password
        self.db.add(user)
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        await self.db.refresh(user)

        return user
