from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from . import user_models
from . import task_models
from . import collection_models


DATABASE_URL = "sqlite+aiosqlite:///database.db"

connect_args = {"check_same_thread": False}
aengine = create_async_engine(DATABASE_URL, connect_args=connect_args)

async def get_db():
    async with AsyncSession(aengine) as session:
        yield session
