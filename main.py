import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database.database import SQLModel, aengine
from routing import (
    user_router,
    authentication_router,
    task_router,
    collection_router,
    chat_bot_router,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logging.getLogger("passlib").setLevel(logging.ERROR)

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with aengine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(authentication_router)
app.include_router(task_router)
app.include_router(collection_router)
app.include_router(chat_bot_router)
