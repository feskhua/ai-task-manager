from typing import Annotated

from langchain_core.tools import InjectedToolArg
from sqlmodel import SQLModel, Field


class CollectionBase(SQLModel):
    """Base model for collection-related operations containing common fields."""
    name: str


class CollectionCreate(CollectionBase):
    """
    Model for creating a new collection.

    Attributes:
        tasks: Optional list of task IDs to associate with the collection
    """
    tasks: list[int] | None = None


class CollectionRetrieve(CollectionBase):
    """
    Model for retrieving basic collection information.

    Attributes:
        id: Unique identifier of the collection
    """
    id: int


class CollectionRetrieveWithTasks(CollectionBase):
    """
    Model for retrieving a collection with its associated tasks.

    Attributes:
        id: Unique identifier of the collection
        tasks: List of task objects associated with the collection
    """
    id: int
    tasks: list["TaskRetrieve"] = []


class CollectionList(CollectionBase):
    """
    Model for listing collections in a simplified format.

    Attributes:
        id: Unique identifier of the collection
    """
    id: int


class CollectionUpdate(SQLModel):
    """
    Model for updating an existing collection with optional fields.

    Attributes:
        name: Optional new name for the collection
    """
    name: str | None = None


class CollectionDelete(SQLModel):
    """
    Model for collection deletion response.

    Attributes:
        id: ID of the collection being deleted
        success: Indicates if deletion was successful
    """
    id: int
    success: bool = False


class CollectionCreateAuth(CollectionCreate):
    """
    A model for creating a collection with authentication token.

    Attributes:
        token (Annotated[str, InjectedToolArg]): The authentication token for the request.
    """
    token: Annotated[str, InjectedToolArg]


class CollectionUpdateAuth(CollectionUpdate):
    """
    A model for updating a collection with authentication token and tracking updated fields.

    Attributes:
        token (Annotated[str, InjectedToolArg]): The authentication token for the request.
        collection_id (int): The unique identifier of the collection to update.
        updated_fields (list[str]): List of field names that were modified in this update.
    """
    token: Annotated[str, InjectedToolArg]
    collection_id: int = Field(description="Collection id")
    updated_fields: list[str] = Field(description="List of updated fields")


from .task_schemas import TaskRetrieve
CollectionRetrieveWithTasks.model_rebuild()
