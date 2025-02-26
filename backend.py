from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict
import asyncio
import anthropic
import json
import os
from dotenv import load_dotenv

from tools.read_code_snippet import read_code_snippet
from tools.modify_code_snippet import modify_code_snippet
from tools.write_new_file import create_code_file
from tools.read_file import read_file
from tools.modify_code_file import modify_code_file

from utils.prompts import system_prompt

# Load environment variables and set API key
load_dotenv()

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store conversation histories
conversation_histories: Dict[str, List[dict]] = {}

api_key = os.getenv("ANTHROPIC_API_KEY")
client = anthropic.Anthropic(api_key=api_key)



async def generate_events(user_message: str, session_id: str):
    
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
    
    if session_id not in conversation_histories:
        conversation_histories[session_id] = []
    
    # Copy previous conversation history and add the new user message.
    messages = conversation_histories[session_id].copy()
    messages.append({"role": "user", "content": user_message})

    try:

        response = client.messages.create(
            system=system_prompt,
            model="claude-3-haiku-20240307",
            temperature=0,
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        
        print(f"\nInitial Response:")
        print(f"Stop Reason: {response.stop_reason}")
        print(f"Content: {response.content}")

        # Process tool calls if the assistant's response asks for tool use.
        while response.stop_reason == "tool_use":
            # Locate the tool_use block within the structured response.
            tool_use = next(block for block in response.content if getattr(block, "type", None) == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input
            
            print(f"\nTool Used: {tool_name}")
            print(f"Tool Input:")
            print(json.dumps(tool_input, indent=2))

            tool_result, can_out = process_tool_call(tool_name, tool_input)
            if can_out != 'none':
                yield f"data: {json.dumps({'type': 'canvas', 'content': {'name': 'none', 'text': can_out}})}\n\n"
            
            print(f"\nTool Result:")
            print(json.dumps(tool_result, indent=2))

            # Append the assistant message without converting to string so its structure is preserved.
            messages.append({"role": "assistant", "content": response.content})
            # Append the tool result as a user message (structured as a list) so that it directly follows the assistant message.
            messages.append({
                "role": "user",
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": str(tool_result)
                }]
            })

            # Get the next response with the tool result provided.
            response = client.messages.create(
                system=system_prompt,
                model="claude-3-haiku-20240307",
                temperature=0,
                max_tokens=4096,
                tools=tools,
                messages=messages
            )


        # Extract the final text from the assistant response.
        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )
        
        print(f"\nFinal Response: {final_response}")
        
        messages.append({"role": "assistant", "content": final_response})
        conversation_histories[session_id] = messages

        yield f"data: {json.dumps({'type': 'message', 'content': {'name': 'none', 'text': final_response}})}\n\n"
        yield f"data: {json.dumps({'type': 'canvas', 'content': {'name': 'example.py', 'text': """def fibonacci(n, memo={}):
    # Base case
    if n <= 1:
        return n
    
    # Check if result is already computed
    if n not in memo:
        # Recursively compute and store in memo
        memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    
    # Return the stored result
    return memo[n]

# Test the function
n = 10
print(f"Fibonacci of {n} is {fibonacci(n)}")
 """ }})}\n\n"

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/chat")
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        user_message = data.get("message")
        session_id = data.get("session_id", "default")

        return StreamingResponse(
            generate_events(user_message, session_id),
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