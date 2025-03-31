import os

from dotenv import load_dotenv


load_dotenv()

SECRET_KEY = os.environ.get("SECRET_KEY")
ALGORITHM = os.environ.get("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 9000

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL")
LIMIT_GEMINI_REQUEST_PER_MESSAGE = int(os.environ.get("LIMIT_GEMINI_REQUEST_PER_MESSAGE"))

TASK_MANAGER_BASE_URL = os.environ.get("TASK_MANAGER_BASE_URL")
