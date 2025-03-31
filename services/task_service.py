from datetime import datetime

from fastapi import HTTPException, status, Query
from sqlalchemy.exc import SQLAlchemyError

from database.task_models import TaskORM
from repositories.task_repo import TaskRepository
from schemas.task_schemas import (
    TaskCreate,
    TaskUpdate,
)


class TaskService:
    """Service class for managing task-related business logic."""

    def __init__(self, task_repository: TaskRepository):
        """
        Initialize the TaskService with a task repository.

        Args:
            task_repository: Repository instance for task operations
        """
        self.task_repository = task_repository

    async def create_task(self, user_id: int, task: TaskCreate) -> TaskORM:
        """
        Create a new task.

        Args:
            user_id: User ID
            task: TaskCreate schema containing task data

        Returns:
            TaskORM: Created task object with loaded relationships

        Raises:
            HTTPException: If task creation fails (404 status)
        """
        try:
            task = await self.task_repository.create_task(user_id, task)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Created task not found or error raised during task creation"
            )

        return task

    async def get_task(self, user_id: int, task_id: int) -> TaskORM:
        """
        Retrieve a task by its ID.

        Args:
            user_id: User ID
            task_id: ID of the task to retrieve

        Returns:
            TaskORM: Task object with loaded relationships

        Raises:
            HTTPException: If task is not found (404 status)
        """
        try:
            task = await self.task_repository.get_task_by_id(user_id, task_id)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        return task

    async def get_tasks(
            self,
            user_id: int,
            offset: int = 0,
            limit: int = Query(default=100, le=100),
            deadline: str | None = None,
            completed: bool = False
    ) -> list[TaskORM]:
        """
        Retrieve a paginated list of tasks with optional deadline filter.

        Args:
            user_id: User ID
            offset: Number of records to skip (default: 0)
            limit: Maximum number of records to return (default: 100, max: 100)
            deadline: Optional ISO format string to filter tasks by deadline
            completed: Optional completed filter(tasks completed, default: False)

        Returns:
            list[TaskORM]: List of task objects

        Raises:
            HTTPException: If deadline format is invalid (400 status)
        """
        if deadline is not None and deadline:
            try:
                deadline = datetime.fromisoformat(deadline)
            except ValueError:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Deadline invalid")

        else:
            deadline = None

        try:
            tasks = await self.task_repository.get_all_tasks(
                user_id,
                offset,
                limit,
                deadline,
                completed,
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        return tasks

    async def update_task(
            self,
            user_id: int,
            task_id: int,
            task: TaskUpdate
    ) -> TaskORM:
        """
        Update an existing task.

        Args:
            user_id: User ID
            task_id: ID of the task to update
            task: TaskUpdate schema with updated task data

        Returns:
            TaskORM: Updated task object

        Raises:
            HTTPException: If task is not found (404 status)
        """
        try:
            task = await self.task_repository.update_task(user_id, task_id, task)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        return task

    async def delete_task(self, user_id: int, task_id: int) -> dict:
        """
        Delete a task by its ID.

        Args:
            user_id: User ID
            task_id: ID of the task to delete

        Returns:
            dict: Dictionary containing the task ID and success status

        Raises:
            HTTPException: If task is not found (404 status)
        """
        try:
            success = await self.task_repository.delete_task(user_id, task_id)
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        if success is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

        return {"id": task_id, "success": success}
