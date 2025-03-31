from typing import Annotated

from fastapi import APIRouter, Depends
from langchain_core.messages import HumanMessage, SystemMessage

from config import LIMIT_GEMINI_REQUEST_PER_MESSAGE
from depends import get_chat_bot_service, get_current_user
from schemas.user_schemas import UserRead, UserMessage
from services.chat_bot_service import ChatBotService


router = APIRouter(prefix="/chat", tags=["Chats"])

@router.post("/")
async def chat(
        message: UserMessage,
        current_user_data: Annotated[UserRead, Depends(get_current_user)],
        chat_bot_service: ChatBotService = Depends(get_chat_bot_service),
):
    """
    Handle a chat message from a user and return the bot's response.

    Args:
        message (UserMessage): The message sent by the user.
        current_user_data (Annotated[UserRead, Depends(get_current_user)]):
            The authenticated user's data obtained from dependency injection.
        chat_bot_service (ChatBotService, optional):
            The chat bot service instance obtained from dependency injection.
            Defaults to result of get_chat_bot_service.

    Returns:
        str: The content of the last message in the conversation, typically the bot's response.

    Note:
        This endpoint uses a graph-based system to process the chat message asynchronously.
        The LIMIT_GEMINI_REQUEST_PER_MESSAGE constant defines the maximum iterations.
    """
    system_prompt = await chat_bot_service.get_setup_prompt()
    system_prompt = SystemMessage(content=system_prompt)
    user_message = HumanMessage(content=message.message)

    graph = await chat_bot_service.get_graph()
    result = await graph.ainvoke(
        {
            "messages": [system_prompt, user_message],
            "iterations": LIMIT_GEMINI_REQUEST_PER_MESSAGE,
            "token": current_user_data[1],
        }
    )
    return result.get("messages")[-1].content
