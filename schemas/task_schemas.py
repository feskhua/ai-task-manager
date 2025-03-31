from datetime import datetime
from typing import Optional, Annotated

from langchain_core.tools import InjectedToolArg
from pydantic import field_validator
from sqlmodel import SQLModel, Field


class TaskBase(SQLModel):
    """Base model for task-related operations containing common fields."""
    title: str = Field(description="Task title")
    description: str = Field(description="Task description")
    deadline: datetime | None = Field(
        default=None,
        description="Task deadline in format: ISO 8601 YYYY-MM-DDTHH:MM:SS.sssZ"
    )

    @classmethod
    @field_validator("deadline")
    def validate_deadline(cls, value):
        """
        Validate and convert deadline field to datetime object if necessary.

        Args:
            value: The deadline value to validate (can be None, string, or datetime)

        Returns:
            datetime | None: Validated datetime object or None if input is None

        Raises:
            ValueError: If string value cannot be parsed to datetime
        """
        if value is None:
            return None
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class TaskCreate(TaskBase):
    """Model for creating a new task."""
    collection_id: int | None = Field(
        default=None, description="Task collection id"
    )


class TaskUpdate(TaskBase):
    """Model for updating an existing task with optional fields."""
    title: str | None = Field(default=None, description="Task title")
    description: str | None = Field(default=None, description="Task description")
    completed: bool = Field(default=False, description="Task completed status")
    collection_id: int | None = Field(default=None, description="Collection that task belongs to")


class TaskRetrieveWithCollection(TaskBase):
    """
    Model for retrieving a task with its associated collection information.

    Attributes:
        id: Unique identifier of the task
        completed: Task completion status
        created_at: Timestamp of task creation
        collection: Optional related collection data
    """
    id: int
    completed: bool = False
    created_at: datetime
    collection: Optional["CollectionRetrieve"] = None


class TaskRetrieve(TaskBase):
    """
    Model for retrieving basic task information.

    Attributes:
        id: Unique identifier of the task
        completed: Task completion status
        created_at: Timestamp of task creation
    """
    id: int
    completed: bool = False
    created_at: datetime


class TaskDelete(SQLModel):
    """
    Model for task deletion response.

    Attributes:
        id: ID of the task being deleted
        success: Indicates if deletion was successful
    """
    id: int
    success: bool


class TaskCreateAuth(TaskCreate):
    """
    A model for creating a task with authentication token.

    Attributes:
        token (Annotated[str, InjectedToolArg]): The authentication token for the request.
    """
    token: Annotated[str, InjectedToolArg]


class TaskUpdateAuth(TaskUpdate):
    """
    A model for updating a task with authentication token and tracking updated fields.

    Attributes:
        token (Annotated[str, InjectedToolArg]): The authentication token for the request.
        task_id (int): The unique identifier of the task to update.
        updated_fields (list[str]): List of field names that were modified in this update.
    """
    token: Annotated[str, InjectedToolArg]
    task_id: int = Field(description="Task id")
    updated_fields: list[str] = Field(description="List of updated fields")


from .collection_schemas import CollectionRetrieve
TaskRetrieveWithCollection.model_rebuild()
