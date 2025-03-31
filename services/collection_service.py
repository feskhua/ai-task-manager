from fastapi import HTTPException, status, Query

from sqlalchemy.exc import SQLAlchemyError

from database.collection_models import TaskCollectionORM
from repositories.collection_repo import CollectionRepository
from repositories.task_repo import TaskRepository
from schemas.collection_schemas import (
    CollectionCreate,
    CollectionUpdate,
)


class CollectionService:
    """Service class for managing collection-related business logic."""

    def __init__(
            self,
            collection_repository: CollectionRepository,
            task_repository: TaskRepository
    ):
        """
        Initialize the CollectionService with required repositories.

        Args:
            collection_repository: Repository for collection operations
            task_repository: Repository for task operations
        """
        self.collection_repository = collection_repository
        self.task_repository = task_repository

    async def create_collection(
            self,
            user_id: int,
            collection: CollectionCreate
    ) -> TaskCollectionORM:
        """
        Create a new collection and optionally assign existing tasks to it.

        Args:
            user_id: User ID
            collection: CollectionCreate schema with collection data and optional task IDs

        Returns:
            TaskCollectionORM: Created collection object with loaded relationships
        """
        try:
            collection_db = await self.collection_repository.create_collection(user_id, collection)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        collection_db_id = collection_db.id
        if collection.tasks:
            task_ids_to_update = await self.task_repository.verify_tasks_exist(
                user_id,
                [task_id for task_id in collection.tasks]
            )
            try:
                await self.task_repository.bulk_update_tasks_collection(
                    user_id,
                    task_ids_to_update,
                    collection_db_id
                )
            except SQLAlchemyError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
                )

        collection = await self.get_collection_by_id(user_id, collection_db_id)
        return collection

    async def get_collection_by_id(
            self,
            user_id: int,
            collection_id: int
    ) -> TaskCollectionORM:
        """
        Retrieve a collection by its ID.

        Args:
            user_id: User ID
            collection_id: ID of the collection to retrieve

        Returns:
            TaskCollectionORM: Collection object with loaded relationships

        Raises:
            HTTPException: If collection is not found (404 status)
        """
        try:
            collection = await self.collection_repository.get_collection_by_id(user_id, collection_id)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if collection is None:
            raise HTTPException(status_code=404, detail="Collection not found")

        return collection

    async def get_collections(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = Query(default=100, le=100)
    ) -> list[TaskCollectionORM]:
        """
        Retrieve a paginated list of collections.

        Args:
            user_id: User ID
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100, max: 100)

        Returns:
            list[TaskCollectionORM]: List of collection objects
        """
        try:
            collections = await self.collection_repository.get_collections(user_id, offset, limit)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        return collections

    async def update_collection(
            self,
            user_id: int,
            collection_id: int,
            collection: CollectionUpdate
    ) -> TaskCollectionORM:
        """
        Update an existing collection.

        Args:
            user_id: User ID
            collection_id: ID of the collection to update
            collection: CollectionUpdate schema with updated data

        Returns:
            TaskCollectionORM: Updated collection object

        Raises:
            HTTPException: If collection is not found (404 status)
        """
        try:
            updated_collection = await self.collection_repository.update_collection(
                user_id,
                collection_id,
                collection
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if updated_collection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )

        return updated_collection

    async def delete_collection(
            self,
            user_id: int,
            collection_id: int
    ) -> dict:
        """
        Delete a collection by its ID.

        Args:
            user_id: User ID
           collection_id: ID of the collection to delete

        Returns:
           dict: Dictionary containing the collection ID and success status

        Raises:
           HTTPException: If collection is not found (404 status)
        """
        try:
            success = await self.collection_repository.delete_collection(user_id, collection_id)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if success is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Collection not found"
            )

        return {"id": collection_id, "success": success}
