import logging
from datetime import datetime

from fastapi import Query
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from database.task_models import TaskORM
from schemas import task_schemas


logger = logging.getLogger(__name__)


class TaskRepository:
    """Repository class for handling task-related database operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize the TaskRepository with a database session.

        Args:
            db: AsyncSession instance for database operations
        """
        self.db = db

    async def create_task(
            self,
            user_id: int,
            task: task_schemas.TaskCreate
    ) -> TaskORM:
        """
        Create a new task in the database.

        Args:
            user_id: User ID
            task: TaskCreate schema containing task data

        Returns:
            TaskORM: Created task object with collection relationship loaded
        """
        task_db = TaskORM.model_validate(task)
        task_db.user_id = user_id
        self.db.add(task_db)
        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        await self.db.refresh(task_db)
        task_db = await self.get_task_by_id(user_id, task_db.id)
        return task_db

    async def get_task_by_id(
            self,
            user_id: int,
            task_id: int
    ) -> TaskORM | None:
        """
        Retrieve a task by its ID with its collection relationship.

        Args:
            user_id: User ID
            task_id: ID of the task to retrieve

        Returns:
            TaskORM | None: Task object if found, None otherwise
        """
        statement = (
            select(TaskORM).options(selectinload(TaskORM.collection))
            .where(TaskORM.id == task_id)
            .where(TaskORM.user_id == user_id)
        )
        try:
            result = await self.db.exec(statement)
        except SQLAlchemyError as e:
            logger.error(e)
            raise

        collection = result.one_or_none()

        return collection

    async def get_all_tasks(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = Query(default=100, le=100),
            deadline: datetime | None = None,
            completed: bool = False
    ) -> list[TaskORM]:
        """
        Retrieve a list of tasks with optional filtering and pagination.

        Args:
            user_id: User ID
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100, max: 100)
            deadline: Optional deadline filter (tasks due by this date)
            completed: Optional completed filter(tasks completed, default: False)

        Returns:
            list[TaskORM]: List of task objects
        """
        statement = (
            select(TaskORM)
            .where(TaskORM.user_id == user_id)
            .where(TaskORM.completed == completed)
            .offset(offset)
            .limit(limit)
        )
        if deadline is not None:
            statement = statement.where(TaskORM.deadline <= deadline)

        try:
            results = await self.db.exec(statement)
        except SQLAlchemyError as e:
            logger.error(e)
            raise

        tasks = results.all()
        return list(tasks)

    async def update_task(
            self,
            user_id: int,
            task_id: int,
            task: task_schemas.TaskUpdate
    ) -> TaskORM | None:
        """
        Update an existing task with new data.

        Args:
            user_id: User ID
            task_id: ID of the task to update
            task: TaskUpdate schema with updated task data

        Returns:
            TaskORM | None: Updated task object if successful, None if task not found
        """
        task_db = await self.get_task_by_id(user_id, task_id)
        if task_db is None:
            return None

        task_data = task.model_dump(exclude_unset=True)

        task_db.sqlmodel_update(task_data)
        self.db.add(task_db)

        try:
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        await self.db.refresh(task_db)
        return task_db

    async def bulk_update_tasks_collection(
            self,
            user_id: int,
            task_ids: list[int],
            collection_id: int
    ) -> None:
        """
        Update the collection ID for multiple tasks in a single operation.

        Args:
            user_id: User ID
            task_ids: List of task IDs to update
            collection_id: New collection ID to assign to the tasks
        """
        statement = (
            update(TaskORM)
            .where(TaskORM.user_id == user_id)
            .where(TaskORM.id.in_(task_ids))
            .values(collection_id=collection_id)
        )
        try:
            await self.db.exec(statement)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise


    async def verify_tasks_exist(
            self,
            user_id: int,
            task_ids: list[int]
    ) -> list[int]:
        """
        Verify which tasks exist from a list of IDs.

        Args:
            user_id: User ID
            task_ids: List of task IDs to check

        Returns:
            list[int]: List of existing task IDs
        """
        statement = (
            select(TaskORM.id)
            .where(TaskORM.user_id == user_id)
            .where(TaskORM.id.in_(task_ids))
        )

        try:
            result = await self.db.exec(statement)
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        existing_ids = result.all()
        return existing_ids

    async def delete_task(
            self,
            user_id: int,
            task_id: int
    ) -> bool | None:
        """
        Delete a task from the database.

        Args:
            user_id: User ID
            task_id: ID of the task to delete

        Returns:
            bool | None: True if deletion successful, None if task not found
        """
        task_db = await self.get_task_by_id(user_id, task_id)
        if task_db is None:
            return None

        try:
            await self.db.delete(task_db)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(e)
            raise

        return True
