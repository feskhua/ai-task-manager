from typing import TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .task_models import TaskORM
    from .collection_models import TaskCollectionORM

class UserORM(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str | None = None
    password: str

    tasks: list["TaskORM"] = Relationship(back_populates="user", cascade_delete=True)
    collections: list["TaskCollectionORM"] = Relationship(back_populates="user", cascade_delete=True)
