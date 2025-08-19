from fastapi import FastAPI, HTTPException
import json
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

from rootagent.agent import root_agent
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

@app.post("/reconciliate")
async def run_reconciliation_agent():
    try:
        APP_NAME = "reconciliation"
        USER_ID = "user1"

        session_service = InMemorySessionService()

        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service
        )

        session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID
        )

        content = Content(role='user', parts=[Part(text="Run the Reconciliation pipeline")])

        events = runner.run_async(
            user_id=USER_ID,
            session_id=session.id,
            new_message=content
        )

        full_response_text = "No final response was received from the agent."
        async for event in events:
            print(f"Event received from: {event.author}")
            if event.is_final_response():
                if event.content and event.content.parts:
                    full_response_text = "".join(part.text for part in event.content.parts)
                else:
                    full_response_text = "Final response event had no content."
                break

        json_response = json.loads(full_response_text)
        return json_response
    
    except json.JSONDecodeError:
        return {
            "error": "Agent response could not be parsed as JSON.",
            "raw_response": full_response_text
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An internal error occurred while running the agent: {str(e)}"
        )
    