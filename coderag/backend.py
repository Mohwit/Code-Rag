from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json

from agent import chat  # Ensure this exists

app = FastAPI()
conversation_histories = {} 

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Define request model
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

async def generate_events(user_message: str, session_id: str):

    if session_id not in conversation_histories:
        conversation_histories[session_id] = []

    # Check if the last message is already the same user input to prevent duplication
    if not conversation_histories[session_id] or conversation_histories[session_id][-1] != {"role": "user", "content": user_message}:
        conversation_histories[session_id].append({"role": "user", "content": user_message})

    try:
        final_response = chat(user_message)  # Call chat() to get the final response


        # Avoid appending duplicate responses
        if not conversation_histories[session_id] or conversation_histories[session_id][-1] != {"role": "assistant", "content": final_response}:
            conversation_histories[session_id].append({"role": "assistant", "content": final_response})

        yield f"data: {json.dumps({'type': 'message', 'content': {'name': 'none', 'text': final_response}})}\n\n"

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.get("/")
async def root():
    return {"message": "API is running"}


@app.post("/chat")
async def chat_endpoint(request_data: ChatRequest):
    try:
        return StreamingResponse(
            generate_events(request_data.message, request_data.session_id),  # Pass only 'message'
            media_type="text/event-stream",
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'
            }
        )

    except Exception as e:
        print(f"Error in chat_endpoint: {str(e)}")
        return StreamingResponse(
            [f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"],
            media_type="text/event-stream"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)