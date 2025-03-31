from typing import Annotated

from fastapi import APIRouter, Depends, Query
from schemas.task_schemas import (
    TaskRetrieveWithCollection,
    TaskCreate,
    TaskRetrieve,
    TaskUpdate,
    TaskDelete,
)
from depends import get_current_user, get_task_service
from schemas.user_schemas import UserRead
from services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("/create", response_model=TaskRetrieveWithCollection)
async def create_task(
        task: TaskCreate,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        task_service: TaskService = Depends(get_task_service)
):
    """
    Create a new task.

    Args:
        task: TaskCreate schema with task data
        current_user_data: Tuple with current user data (UserRead, token)
        task_service: Dependency-injected TaskService instance

    Returns:
        TaskRetrieveWithCollection: Created task with collection relationship

    Raises:
        HTTPException: If creation fails (handled by TaskService)
    """
    user_id = current_user_data[0].id
    task = await task_service.create_task(user_id, task)
    return task

@router.get("/{task_id}", response_model=TaskRetrieveWithCollection)
async def get_task(
        task_id: int,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        task_service: TaskService = Depends(get_task_service)
):
    """
    Retrieve a task by ID.

    Args:
        task_id: ID of the task to retrieve
        current_user_data: Tuple with current user data (UserRead, token)
        task_service: Dependency-injected TaskService instance

    Returns:
        TaskRetrieveWithCollection: Task with collection relationship

    Raises:
        HTTPException: If task not found (404 status)
    """
    user_id = current_user_data[0].id
    task = await task_service.get_task(user_id, task_id)
    return task

@router.get("/", response_model=list[TaskRetrieve])
async def task_list(
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        offset: int = 0,
        limit: int = Query(default=100, le=100),
        deadline: str | None = None,
        completed: bool = False,
        task_service: TaskService = Depends(get_task_service)
):
    """
    Retrieve a paginated list of tasks with optional deadline filter.

    Args:
        current_user_data: Tuple with current user data (UserRead, token)
        offset: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
        deadline: Optional ISO format string to filter tasks by deadline
        task_service: Dependency-injected TaskService instance
        completed: Optional completed filter(tasks completed, default: False)

    Returns:
        list[TaskRetrieve]: List of tasks without collection details

    Raises:
        HTTPException: If deadline format is invalid (400 status)
    """
    user_id = current_user_data[0].id
    tasks = await task_service.get_tasks(user_id, offset, limit, deadline, completed)
    return tasks

@router.patch("/{task_id}/update", response_model=TaskRetrieveWithCollection)
async def update_task(
        task_id: int,
        task: TaskUpdate,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        task_service: TaskService = Depends(get_task_service),
):
    """
    Update an existing task.

    Args:
        task_id: ID of the task to update
        task: TaskUpdate schema with updated data
        current_user_data: Tuple with current user data (UserRead, token)
        task_service: Dependency-injected TaskService instance

    Returns:
        TaskRetrieveWithCollection: Updated task with collection relationship

    Raises:
        HTTPException: If task not found (404 status)
    """
    user_id = current_user_data[0].id
    task = await task_service.update_task(user_id, task_id, task)
    return task

@router.delete("/{task_id}/delete", response_model=TaskDelete)
async def delete_task(
        task_id: int,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        task_service: TaskService = Depends(get_task_service),
):
    """
    Delete a task by ID.

    Args:
        task_id: ID of the task to delete
        current_user_data: Tuple with current user data (UserRead, token)
        task_service: Dependency-injected TaskService instance

    Returns:
        TaskDelete: Deletion response with ID and success status

    Raises:
        HTTPException: If task not found (404 status)
    """
    user_id = current_user_data[0].id
    deleted_task = await task_service.delete_task(user_id, task_id)
    return deleted_task
