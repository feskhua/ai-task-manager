# AI-Task-Manager

This project is implemented on FastAPI using LangGraph, LangChain, and Gemini API to manage tasks and collections with CRUD operations and an integrated chatbot.

## Features

- CRUD API for tasks and collections
- JWT-based authentication for secure endpoint access
- Integrated chatbot capable of performing all CRUD operations on tasks and collections using tools
- Asynchronous processing of requests
- Support for task and collection management via AI-powered bot

## Tech Stack

**Core**:
- FastAPI
- SQLModel
- Pydantic
- SQLAlchemy
- LangGraph
- LangChain
- Gemini API

## How to Run

1. Navigate to the project directory:
```commandline
cd ai-task-manager
```
2. Ensure Poetry is installed (install it with `pip install poetry` if needed).
3. Create a virtual environment and install dependencies using Poetry:
```commandline
poetry install
```
This will create a virtual environment and install all project dependencies listed in `pyproject.toml`.
4. Copy `.env.sample` to `.env` and configure your environment variables (e.g., database URL, Gemini API key, JWT secret):
```commandline
cp .env.sample .env
```
5. Activate the virtual environment:
```commandline
poetry shell
```
6. Run the application:
```commandline
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```
he API will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Notes
- Authentication is required to access the endpoints; obtain a JWT token via the authentication endpoint.
- The chatbot leverages LangGraph and LangChain with the Gemini API to handle task and collection operations.
