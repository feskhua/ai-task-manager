from typing import Annotated

from fastapi import APIRouter, Depends, Query

from depends import get_current_user, get_collection_service
from schemas.user_schemas import UserRead
from services.collection_service import CollectionService
from schemas.collection_schemas import (
    CollectionCreate,
    CollectionRetrieveWithTasks,
    CollectionRetrieve,
    CollectionUpdate, CollectionDelete,
)


router = APIRouter(prefix="/collections", tags=["Collections"])

@router.post("/create", response_model=CollectionRetrieveWithTasks)
async def create_collection(
        collection: CollectionCreate,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        collection_service: CollectionService = Depends(get_collection_service)
):
    """
    Create a new collection.

    Args:
        collection: CollectionCreate schema with collection data
        current_user_data: Tuple with current user data (UserRead, token)
        collection_service: Dependency-injected CollectionService instance

    Returns:
        CollectionRetrieveWithTasks: Created collection with task relationships

    Raises:
        HTTPException: If creation fails (handled by CollectionService)
    """
    user_id = current_user_data[0].id
    collection = await collection_service.create_collection(user_id, collection)
    return collection

@router.get("/{collection_id}", response_model=CollectionRetrieveWithTasks)
async def get_collection(
        collection_id: int,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        collection_service: CollectionService = Depends(get_collection_service)
):
    """
    Retrieve a collection by ID.

    Args:
        collection_id: ID of the collection to retrieve
        current_user_data: Tuple with current user data (UserRead, token)
        collection_service: Dependency-injected CollectionService instance

    Returns:
        CollectionRetrieveWithTasks: Collection with task relationships

    Raises:
        HTTPException: If collection not found (404 status)
    """
    user_id = current_user_data[0].id
    collection = await collection_service.get_collection_by_id(user_id, collection_id)
    return collection

@router.get("/", response_model=list[CollectionRetrieve])
async def collection_list(
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        offset: int = 0,
        limit: int = Query(default=100, le=100),
        collection_service: CollectionService = Depends(get_collection_service)
):
    """
    Retrieve a paginated list of collections.

    Args:
        current_user_data: Tuple with current user data (UserRead, token)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        collection_service: Dependency-injected CollectionService instance

    Returns:
        list[CollectionRetrieve]: List of collections without task details
    """
    user_id = current_user_data[0].id
    collections = await collection_service.get_collections(user_id, offset, limit)
    return collections

@router.patch("/{collection_id}/update", response_model=CollectionRetrieveWithTasks)
async def update_collection(
        collection_id: int,
        collection: CollectionUpdate,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        collection_service: CollectionService = Depends(get_collection_service)
):
    """
    Update an existing collection.

    Args:
        collection_id: ID of the collection to update
        collection: CollectionUpdate schema with updated data
        current_user_data: Tuple with current user data (UserRead, token)
        collection_service: Dependency-injected CollectionService instance

    Returns:
        CollectionRetrieveWithTasks: Updated collection with task relationships

    Raises:
        HTTPException: If collection not found (404 status)
    """
    user_id = current_user_data[0].id
    task = await collection_service.update_collection(user_id, collection_id, collection)
    return task

@router.delete("/{collection_id}/delete", response_model=CollectionDelete)
async def delete_collection(
        collection_id: int,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        collection_service: CollectionService = Depends(get_collection_service),
):
    """
    Delete a collection by ID.

    Args:
       collection_id: ID of the collection to delete
       current_user_data: Tuple with current user data (UserRead, token)
       collection_service: Dependency-injected CollectionService instance

    Returns:
       CollectionDelete: Deletion response with ID and success status

    Raises:
       HTTPException: If collection not found (404 status)
    """
    user_id = current_user_data[0].id
    deleted_collection = await collection_service.delete_collection(user_id, collection_id)
    return deleted_collection
