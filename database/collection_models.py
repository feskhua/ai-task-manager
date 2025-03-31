from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .task_models import TaskORM
    from .user_models import UserORM


class TaskCollectionORM(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    user_id: int | None = Field(default=None, foreign_key="userorm.id", ondelete="CASCADE")

    user: Optional["UserORM"] = Relationship(back_populates="collections")
    tasks: list["TaskORM"] = Relationship(back_populates="collection", cascade_delete=True)
