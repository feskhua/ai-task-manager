import logging

from fastapi import Query
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from database.collection_models import TaskCollectionORM
from schemas.collection_schemas import (
    CollectionCreate, CollectionUpdate
)


logger = logging.getLogger(__name__)


class CollectionRepository:
    """Repository class for handling collection-related database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the CollectionRepository with a database session.

        Args:
            db: AsyncSession instance for database operations
        """
        self.db = db

    async def create_collection(
            self,
            user_id: int,
            collection: CollectionCreate
    ) -> TaskCollectionORM:
        """
        Create a new collection in the database.

        Args:
            user_id: User ID
            collection: CollectionCreate schema containing collection data

        Returns:
            TaskCollectionORM: Created collection object
        """
        collection_db = TaskCollectionORM(
            name=collection.name,
            user_id=user_id
        )
        self.db.add(collection_db)
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        await self.db.refresh(collection_db)
        return collection_db

    async def get_collection_by_id(
            self,
            user_id: int,
            collection_id: int
    ) -> TaskCollectionORM | None:
        """
        Retrieve a collection by its ID with its tasks relationship.

        Args:
            user_id: User ID
            collection_id: ID of the collection to retrieve

        Returns:
            TaskCollectionORM | None: Collection object if found, None otherwise
        """
        statement = (
            select(TaskCollectionORM)
            .options(selectinload(TaskCollectionORM.tasks))
            .where(TaskCollectionORM.id == collection_id)
            .where(TaskCollectionORM.user_id == user_id)
        )

        try:
            result = await self.db.exec(statement)
        except SQLAlchemyError as e:
            logger.error(e)
            raise

        collection = result.one_or_none()
        return collection

    async def get_collections(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = Query(default=100, le=100)
    ) -> list[TaskCollectionORM]:
        """
        Retrieve a list of collections with pagination.

        Args:
            user_id: User ID
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100, max: 100)

        Returns:
            list[TaskCollectionORM]: List of collection objects
        """
        statement = (
            select(TaskCollectionORM)
            .where(TaskCollectionORM.user_id == user_id)
            .offset(offset)
            .limit(limit)
        )
        try:
            results = await self.db.exec(statement)
        except SQLAlchemyError as e:
            logger.error(e)
            raise

        collections = results.all()
        return list(collections)

    async def update_collection(
            self,
            user_id: int,
            collection_id: int,
            collection: CollectionUpdate
    ) -> TaskCollectionORM | None:
        """
        Update an existing collection with new data.

        Args:
            user_id: User ID
            collection_id: ID of the collection to update
            collection: CollectionUpdate schema with updated collection data

        Returns:
            TaskCollectionORM | None: Updated collection object if successful,
                                   None if collection not found
        """
        collection_db = await self.get_collection_by_id(user_id, collection_id)
        if collection_db is None:
            return None

        collection_data = collection.model_dump(exclude_unset=True)

        collection_db.sqlmodel_update(collection_data)
        self.db.add(collection_db)
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        await self.db.refresh(collection_db)
        return collection_db

    async def delete_collection(
            self,
            user_id: int,
            collection_id: int
    ) -> bool | None:
        """
        Delete a collection from the database.

        Args:
            user_id: User ID
            collection_id: ID of the collection to delete

        Returns:
            bool | None: True if deletion successful, None if collection not found
        """
        collection_db = await self.get_collection_by_id(user_id, collection_id)
        if collection_db is None:
            return None

        try:
            await self.db.delete(collection_db)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        return True
