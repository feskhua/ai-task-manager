from datetime import datetime
from logging import getLogger
from typing import TypedDict, Annotated

from fastapi import HTTPException
from langchain_core.messages import ToolMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from repositories.gemini_repo import GeminiRepository
from repositories.task_manager_repo import TaskManagerRepository


logger = getLogger(__name__)


class ChatBotState(TypedDict):
    """
    A typed dictionary defining the state structure for the chatbot workflow.

    Attributes:
        messages (Annotated[list, add_messages]): List of messages in the conversation.
        iterations (int): Number of remaining iterations for processing.
        response (str): The current response from the chatbot.
        token (str): Authentication token for API calls.
    """
    messages: Annotated[list, add_messages]
    iterations: int
    response: str
    token: str


class ChatBotService:
    """
    A service class for managing chatbot interactions with LLM and task manager.

    Attributes:
        gemini_repository (GeminiRepository): Repository for LLM interactions.
        task_manager_repository (TaskManagerRepository): Repository for task management functions.
    """
    def __init__(
            self,
            gemini_repository: GeminiRepository,
            task_manager_repository: TaskManagerRepository,
    ):
        self.gemini_repository = gemini_repository
        self.task_manager_repository = task_manager_repository

    async def call_llm_with_tools(self, state: ChatBotState) -> dict:
        """
        Call the language model with the current conversation state.

        Args:
            state (ChatBotState): The current state of the chatbot conversation.

        Returns:
            dict: Updated state with new message and decremented iterations.

        Raises:
            HTTPException: If the LLM call fails (status code 500).
        """
        messages = state["messages"]
        response = await self.gemini_repository.llm_generate(messages)
        logger.info("Called llm with messages(reversed): %s", messages[::-1])
        if response is None:
            raise HTTPException(status_code=500, detail="Error while calling LLM")

        iterations = state["iterations"] - 1
        return {"messages": [response], "iterations": iterations}

    async def call_task_manager_api(self, state: ChatBotState) -> dict:
        """
        Execute tool calls through the task manager API based on the last message.

        Args:
            state (ChatBotState): The current state of the chatbot conversation.

        Returns:
            dict: Updated state with tool execution results as messages.
        """
        messages = state["messages"]
        last_message = messages[-1]
        tool_messages = []
        for tool_call in last_message.tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("args")
            function_to_call = self.task_manager_repository.get_function_by_name(tool_name)
            logger.info("Calling function %s, with args %s", tool_name, tool_args)
            tool_args["token"] = state["token"]

            try:
                result = await function_to_call.ainvoke(tool_args)

            except Exception as e:
                logger.info("An error occurred when calling the api node %s", e)
                result = str(e)

            logger.info("Function result %s", result)
            tool_messages.append(ToolMessage(
                content=f"Function result is: {result}",
                tool_call_id=tool_call.get("id"),
                name=tool_name
            ))
        return {"messages": tool_messages}

    async def limit_llm_request_exceeded(self, state: ChatBotState) -> dict:
        """Handle the case when LLM request limit is exceeded for a single user message.

        Args:
            state (ChatBotState): The current state of the chat bot containing message history

        Returns:
            dict: Dictionary containing the limit prompt and LLM response messages

        Raises:
            HTTPException: If LLM generation fails (status code 500)
        """
        messages = state["messages"]
        limit_prompt = HumanMessage(
            content="""The chatbot has reached its maximum number of LLM API calls for this single user message. Please summarize the results obtained from previous API calls and inform the user that processing has stopped due to this limitation. Let them know they can continue by sending a new message with additional instructions, rather than this being a permanent limit on their account. Use a clear and friendly tone to explain this technical limitation.
            """
        )
        messages.append(limit_prompt)
        response = await self.gemini_repository.llm_generate(messages)
        logger.info("Called llm with messages(reversed): %s", messages[::-1])
        if response is None:
            raise HTTPException(status_code=500, detail="Error while calling LLM")

        return {"messages": [limit_prompt, response]}


    @staticmethod
    async def resolve_model_response(state: ChatBotState) -> str:
        """
        Determine the next step in the workflow based on the current state.

        Args:
            state (ChatBotState): The current state of the chatbot conversation.

        Returns:
            str: Either 'call_api' to continue with API calls or 'end' to finish.
        """
        messages = state["messages"]
        last_message = messages[-1]

        if not (hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0):
            return "end"

        return "call_api"

    @staticmethod
    async def check_gemini_limit_request(state: ChatBotState) -> str:
        """Check if the llm request limit has been reached.

        Args:
            state (ChatBotState): The current state of the chat bot containing iteration count

        Returns:
            str: "limit_llm_request" if limit is reached, "llm" if requests are still available
        """
        if state["iterations"] <= 0:
            return "limit_llm_request"

        return "llm"

    async def get_graph(self):
        """
        Create and configure the state graph for the chatbot workflow.

        Returns:
            Compiled StateGraph: The configured workflow graph for chatbot processing.
        """
        workflow = StateGraph(ChatBotState)

        workflow.add_node("llm", self.call_llm_with_tools)
        workflow.add_node("call_api", self.call_task_manager_api)
        workflow.add_node("limit_llm_request", self.limit_llm_request_exceeded)

        workflow.add_edge(START, "llm")
        workflow.add_conditional_edges(
            "llm",
            self.resolve_model_response,
            {
                "call_api": "call_api",
                "end": END,
            }
        )
        workflow.add_conditional_edges(
            "call_api",
            self.check_gemini_limit_request,
            {
                "llm": "llm",
                "limit_llm_request": "limit_llm_request",
                }
            )
        workflow.add_edge("limit_llm_request", END)

        return workflow.compile()

    @staticmethod
    async def get_setup_prompt() -> str:
        prompt = """
            Role: You are a Task Manager API assistant designed to execute user requests using function calling.
        
            ---
        
            ### Instructions:
            - Process each user request by selecting and calling the appropriate function from the available tools, you can call several functions at once if you have enough information.
            - Use the function's documentation and argument descriptions to determine how to extract and format parameters from the user request.
            - General guidelines for parameter extraction:
              - For fields like "title" or "name", use the main action, object, or keywords from the request (e.g., "sweep the floor" from "create task: sweep the floor").
              - For optional fields (e.g., "description", "deadline", "collection_id"), include them only if explicitly mentioned; otherwise, set to null or skip.
              - For datetime fields, use a simple format like "YYYY-MM-DD HH:MM:SS" based on the current datetime if relative time is mentioned (e.g., "tomorrow" or "by 6 PM").
            - Handle function call errors:
              - If arguments are invalid but fixable (e.g., wrong format), adjust them and retry.
              - If the error is server-side or the request was not completed successfully, respond with a polite message in the user's language indicating the request cannot be processed at this time.
            - When the user wants to create a task:
              1. First, use the 'collection_list' tool to retrieve the list of existing collections.
              2. Analyze the user's request and determine if it matches any collection based on its content:
                 - A task fits a collection if its meaning, purpose, or keywords align with the collection's theme (e.g., a task about cleaning fits 'home chores').
              3. Use the 'create_task' tool to create the task:
                 - If a matching collection is found, include it in the 'create_task' call with the task description and collection.
                 - If no collection matches, call 'create_task' with the task description and no collection.
            - Avoid placeholder values like "unknown". If parameters cannot be determined, respond with a polite request for clarification in the user's language.
            - If the requested action is impossible or already completed, provide a concise explanation in the user's language (e.g., "Task already exists" or "Collection not found").
            - Always respond in the same language as the user request.
            - Do not create new entities (e.g., collections) unnecessarily—check if they exist first, if applicable.

            ---
        
            ### About the Task Manager:
            - Supports CRUD operations for tasks and collections.
            - A collection can contain multiple tasks.
            - Tasks can exist independently if no suitable collection is specified.
        
            ---
        
            ### Datetime Context:
            - Include datetime parameters (e.g., "deadline") if the request mentions a date or time.
            - Current datetime: {current_datetime}.
            - If a date is provided but no time is specified, set the time to 23:59 of that day (e.g., "2025-03-19" becomes "2025-03-19T23:59:59.994Z").
            - If no date or time is provided, skip those arguments.
            - 
        
            ---
        
            ### User Request:
            User request below:
        """
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return prompt.format(current_datetime=current_datetime)
