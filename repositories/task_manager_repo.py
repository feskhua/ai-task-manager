from logging import getLogger
from typing import Annotated

from langchain_core.tools import tool, InjectedToolArg
from httpx import AsyncClient, HTTPError

from config import TASK_MANAGER_BASE_URL
from schemas.task_schemas import TaskCreateAuth, TaskUpdateAuth, TaskCreate
from schemas.collection_schemas import CollectionCreateAuth, CollectionUpdateAuth


logger = getLogger(__name__)


class TaskManagerRepository:
    @staticmethod
    @tool(args_schema=TaskCreateAuth)
    async def create_task(
            title: str,
            description: str,
            token: Annotated[str, InjectedToolArg],
            deadline: str | None = None,
            collection_id: int | None = None
    ):
        """
        Create a new task.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        task = TaskCreate(
            title=title,
            description=description,
            deadline=deadline,
            collection_id=collection_id,
        )

        async with AsyncClient() as client:
            try:
                response = await client.post(
                    f"{TASK_MANAGER_BASE_URL}tasks/create",
                    json=task.model_dump(mode="json", exclude_unset=True),
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool
    async def read_task(task_id: int, token: Annotated[str, InjectedToolArg]):
        """
        Retrieve a task by ID.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{TASK_MANAGER_BASE_URL}tasks/{task_id}",
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool
    async def task_list(
            offset: int,
            limit: int,
            token: Annotated[str, InjectedToolArg],
            deadline: str | None = None,
            completed: bool | None = False
    ):
        """
        Retrieve a paginated list of tasks with "id" attribute and other.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{TASK_MANAGER_BASE_URL}tasks/",
                    params={
                        "offset": offset,
                        "limit": limit,
                        "deadline": deadline,
                        "completed": completed if completed else False,
                    },
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool(args_schema=TaskUpdateAuth)
    async def update_task(
            task_id: int,
            updated_fields: list[str],
            token: Annotated[str, InjectedToolArg],
            title: str | None = None,
            description: str | None = None,
            completed: bool = False,
            deadline: str | None = None,
            collection_id: int | None = None
    ):
        """
        Update an existing task by ID.
        """
        data = {
            "title": title,
            "description": description,
            "completed": completed,
            "deadline": deadline,
            "collection_id": collection_id,
        }

        data_to_update = {field: data[field] for field in updated_fields}
        logger.info(f"Update task with args: {data_to_update}")

        headers = {
            "Authorization": f"Bearer {token}"
        }

        async with AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{TASK_MANAGER_BASE_URL}tasks/{task_id}/update",
                    json=data_to_update,
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool
    async def delete_task(task_id: int, token: Annotated[str, InjectedToolArg]):
        """
        Delete a task by ID.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{TASK_MANAGER_BASE_URL}tasks/{task_id}/delete",
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool(args_schema=CollectionCreateAuth)
    async def create_collection(
            name: str,
            token: Annotated[str, InjectedToolArg],
            tasks: list[int] | None = None
    ):
        """
        Create a new collection.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        body = {
            "name": name,
            "tasks": tasks,
        }
        logger.info(f"Creating new collection with args: {body}")
        async with AsyncClient() as client:
            try:
                response = await client.post(
                    f"{TASK_MANAGER_BASE_URL}collections/create",
                    json=body,
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool
    async def read_collection(collection_id: int, token: Annotated[str, InjectedToolArg]):
        """
        Retrieve a collection by ID.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{TASK_MANAGER_BASE_URL}collections/{collection_id}",
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool
    async def collection_list(
            offset: int,
            limit: int,
            token: Annotated[str, InjectedToolArg]
    ):
        """
        Retrieve a paginated list of collections.
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with AsyncClient() as client:
            try:
                response = await client.get(
                    f"{TASK_MANAGER_BASE_URL}collections/",
                    params={
                        "offset": offset,
                        "limit": limit,
                    },
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool(args_schema=CollectionUpdateAuth)
    async def update_collection(
            collection_id: int,
            updated_fields: list[str],
            token: Annotated[str, InjectedToolArg],
            name: str | None = None,
    ):
        """
        Update an existing collection.
        """
        data = {
            "name": name,
        }
        data_to_update = {field: data[field] for field in updated_fields}
        logger.info(f"Update collection with args: {data_to_update}")

        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with AsyncClient() as client:
            try:
                response = await client.patch(
                    f"{TASK_MANAGER_BASE_URL}collections/{collection_id}/update",
                    json=data_to_update,
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    @staticmethod
    @tool
    async def delete_collection(collection_id: int, token: Annotated[str, InjectedToolArg]):
        """
        Delete a collection by ID.

        Args:
           collection_id: ID of the collection to delete

        Returns:
           CollectionDelete: Deletion response with ID and success status
        """
        headers = {
            "Authorization": f"Bearer {token}"
        }
        async with AsyncClient() as client:
            try:
                response = await client.delete(
                    f"{TASK_MANAGER_BASE_URL}collections/{collection_id}/delete",
                    headers=headers
                )
                response.raise_for_status()
            except HTTPError as e:
                logger.error(
                    "Error while making API call: %s, response: %s",
                    e,
                    response.json()
                )
                return str(e)

        return response.json()

    def get_function_by_name(self, name: str):
        """
        Retrieve a function by its name.

        This method returns a reference to a function based on the provided name.
        If the function name is not found in the predefined mapping, it raises a
        NotImplementedError.
        Args:
            name (str): The name of the function to retrieve.

        Returns:
            Callable: The corresponding function.

        Raises:
            NotImplementedError: If the function name is not found in the mapping.
        """
        funcs = {
            "create_task": self.create_task,
            "read_task": self.read_task,
            "task_list": self.task_list,
            "update_task": self.update_task,
            "delete_task": self.delete_task,
            "create_collection": self.create_collection,
            "read_collection": self.read_collection,
            "collection_list": self.collection_list,
            "update_collection": self.update_collection,
            "delete_collection": self.delete_collection,
        }
        func = funcs.get(name)
        if func is None:
            raise NotImplementedError(f"Function {name} is not implemented")

        return func
