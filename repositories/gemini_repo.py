from logging import getLogger

from langchain_core.exceptions import LangChainException
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai.chat_models import ChatGoogleGenerativeAIError

from config import GEMINI_MODEL, GEMINI_API_KEY
from repositories.task_manager_repo import TaskManagerRepository


logger = getLogger(__name__)

tools = [
    TaskManagerRepository.create_task,
    TaskManagerRepository.read_task,
    TaskManagerRepository.task_list,
    TaskManagerRepository.update_task,
    TaskManagerRepository.delete_task,
    TaskManagerRepository.create_collection,
    TaskManagerRepository.read_collection,
    TaskManagerRepository.collection_list,
    TaskManagerRepository.update_collection,
    TaskManagerRepository.delete_collection,
]


class GeminiRepository:
    def __init__(self, model: ChatGoogleGenerativeAI):
        self.model = model
        self.model_with_tools = self.model.bind_tools(tools)


    async def llm_generate(
            self,
            messages,
            with_tools: bool = True,
    ):
        try:
            if with_tools:
                response = await self.model_with_tools.ainvoke(messages)
            else:
                response = await self.model.ainvoke(messages)
            logger.info("Gemini response: %s", response)
        except ChatGoogleGenerativeAIError as e:
            logger.error(
                "Error handling Gemini API request, %s",
                e
            )
            return None

        except LangChainException as e:
            logger.error(str(e))
            return None

        return response
