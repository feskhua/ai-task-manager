from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .collection_models import TaskCollectionORM
    from .user_models import UserORM


class TaskORM(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    description: str
    completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    deadline: datetime | None = None
    collection_id: int | None = Field(default=None, foreign_key="taskcollectionorm.id", ondelete="CASCADE")
    user_id: int | None = Field(default=None, foreign_key="userorm.id", ondelete="CASCADE")

    collection: Optional["TaskCollectionORM"] = Relationship(back_populates="tasks")
    user: Optional["UserORM"] = Relationship(back_populates="tasks")
