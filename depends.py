import logging
from typing import Annotated

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlmodel.ext.asyncio.session import AsyncSession

from config import SECRET_KEY, ALGORITHM, GEMINI_MODEL, GEMINI_API_KEY
from database.database import get_db
from database.user_models import UserORM
from repositories.collection_repo import CollectionRepository
from repositories.gemini_repo import GeminiRepository
from repositories.task_manager_repo import TaskManagerRepository
from repositories.task_repo import TaskRepository
from repositories.user_repo import UserRepository
from schemas.auth_schemas import TokenData
from services.authentication_service import AuthenticationService
from services.collection_service import CollectionService
from services.chat_bot_service import ChatBotService
from services.task_service import TaskService
from services.user_service import UserService


logger = logging.getLogger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_task_manager_repository():
    """Get an instance of TaskManagerRepository.

    Returns:
        TaskManagerRepository: A new instance of TaskManagerRepository
    """
    return TaskManagerRepository()

async def get_gemini_repository():
    """Get an instance of GeminiRepository.

    Returns:
        GeminiRepository: A new instance of GeminiRepository
    """
    return GeminiRepository(
        ChatGoogleGenerativeAI(
            model=GEMINI_MODEL,
            api_key=GEMINI_API_KEY,
            temperature=0.0
        )
    )

async def get_user_repository(
        session: AsyncSession = Depends(get_db)
):
    """Get an instance of UserRepository with database session.

    Args:
        session (AsyncSession): Database session from dependency injection

    Returns:
        UserRepository: Repository instance with session configured
    """
    return UserRepository(session)

async def get_task_repository(
        session: AsyncSession = Depends(get_db)
):
    """Get an instance of TaskRepository with database session.

    Args:
        session (AsyncSession): Database session from dependency injection

    Returns:
        TaskRepository: Repository instance with session configured
    """
    return TaskRepository(session)

async def get_collection_repository(
        session: AsyncSession = Depends(get_db)
):
    """Get an instance of CollectionRepository with database session.

    Args:
       session (AsyncSession): Database session from dependency injection

    Returns:
       CollectionRepository: Repository instance with session configured
    """
    return CollectionRepository(session)

async def get_authentication_service(
        user_repo: UserRepository = Depends(get_user_repository)
):
    """Get an instance of AuthenticationService with user repository.

    Args:
        user_repo (UserRepository): User repository from dependency injection

    Returns:
        AuthenticationService: Service instance with user repository configured
    """
    return AuthenticationService(user_repo)

async def get_chat_bot_service(
        gemini_repo: GeminiRepository = Depends(get_gemini_repository),
        task_manager_repo: TaskManagerRepository = Depends(get_task_manager_repository)
):
    """Get an instance of ChatBotService with required repositories.

    Args:
        gemini_repo (GeminiRepository): Gemini repository from dependency injection
        task_manager_repo (TaskManagerRepository): Task manager repository from dependency injection

    Returns:
        ChatBotService: Service instance with repositories configured
    """
    return ChatBotService(gemini_repo, task_manager_repo)

async def get_task_service(
        task_repo: TaskRepository = Depends(get_task_repository)
):
    """Get an instance of TaskService with task repository.

    Args:
        task_repo (TaskRepository): Task repository from dependency injection

    Returns:
        TaskService: Service instance with task repository configured
    """
    return TaskService(task_repo)

async def get_collection_service(
        collection_repo: CollectionRepository = Depends(get_collection_repository),
        task_repo: TaskRepository = Depends(get_task_repository)
):
    """Get an instance of CollectionService with required repositories.

    Args:
        collection_repo (CollectionRepository): Collection repository from dependency injection
        task_repo (TaskRepository): Task repository from dependency injection

    Returns:
        CollectionService: Service instance with repositories configured
    """
    return CollectionService(collection_repo, task_repo)

async def get_user_service(
        user_repo: UserRepository = Depends(get_user_repository),
        authentication_service: AuthenticationService = Depends(get_authentication_service)
):
    """Get an instance of UserService with required dependencies.

    Args:
        user_repo (UserRepository): User repository from dependency injection
        authentication_service (AuthenticationService): Authentication service from dependency injection

    Returns:
        UserService: Service instance with dependencies configured
    """
    return UserService(user_repo, authentication_service)


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        user_repository: UserRepository = Depends(get_user_repository),
) -> (UserORM, str):
    """Authenticate and retrieve the current user based on JWT token.

    Args:
        token (str): JWT token from OAuth2 dependency
        user_repository (UserRepository): User repository from dependency injection

    Returns:
        tuple: (UserORM object, token string)

    Raises:
        HTTPException: If credentials cannot be validated (401)
        HTTPException: If token has expired (401)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"verify_exp": True}
        )
        user_id = payload.get("sub")
        logger.info(f"user id: {user_id}")
        if user_id is None:
            raise credentials_exception

        token_data = TokenData(user_id=int(user_id))

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidTokenError:
        logger.info("InvalidTokenError")
        raise credentials_exception

    user = await user_repository.get_user_by_id(token_data.user_id)
    if user is None:
        raise credentials_exception

    return user, token
