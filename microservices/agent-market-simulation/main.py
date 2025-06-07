# main.py
import asyncio

from fastapi import FastAPI, HTTPException
from google.adk import Runner
from google.adk.agents.invocation_context import InvocationContext
from google.adk.artifacts import InMemoryArtifactService
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel

from agent_core.agent import market_simulator_agent


# --- API Data Models ---
class ChatRequest(BaseModel):
    query: str
    user_id: str | None = None  # Optional: track conversation history


class ChatResponse(BaseModel):
    reply: str


# --- FastAPI Application ---
app = FastAPI(
    title="Order Status Agent API",
    description="An API for interacting with a Google ADK-powered agent.",
    version="1.0.0"
)


@app.get("/", tags=["General"])
def read_root():
    """A simple endpoint to check if the API is running."""
    return {"message": "Welcome to the Order Agent API. Use the /chat endpoint to interact."}

# Initialize session service and runner
APP_NAME = "my_first_adk_app"
USER_ID = "user_dev_1"
SESSION_ID = "session_main_1"

session_service = InMemorySessionService()
runner = Runner(agent=market_simulator_agent, app_name=APP_NAME, session_service=session_service)

# Create the session
session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

# Define FastAPI app
app = FastAPI(title="ADK Agent API")


@app.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    content = types.Content(role='user', parts=[types.Part(text=request.query)])
    final_response_text = "Agent did not produce a final response."

    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                elif event.actions and event.actions.escalate:
                    final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
                break
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    return ChatResponse(reply=final_response_text)
