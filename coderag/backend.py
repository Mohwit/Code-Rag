from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json

from agent import chat  # Ensure this exists

app = FastAPI()

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


async def generate_events(user_message: str):
    try:
        # Call the chat function in a non-blocking way
        response = await asyncio.to_thread(chat, user_message)

        # Determine if canvas is required
        use_canvas = False
        tool_name = response.get("tool_name")  # Extract tool_name from response
        if tool_name in ["modify_code_file", "create_code_file"]:
            use_canvas = True

        response_payload = {
            "type": "canvas" if use_canvas else "message",
            "content": {
                "name": response.get("file_name", "None") if use_canvas else "None",
                "text": response.get("text", ""),
            }
        }

        # Yield response as an event stream
        yield f"data: {json.dumps(response_payload)}\n\n"

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
            generate_events(request_data.message),  # Pass only 'message'
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
