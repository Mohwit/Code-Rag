""" Agent for code analyzer """
""" Testing"""

"""RUN : uvicorn agent:app --host 0.0.0.0 --port 8080 --reload"""

import anthropic
import json
import os
from dotenv import load_dotenv
import asyncio
import shutil
import tempfile
import uuid
from typing import List

from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

from tools.modify import modify_code_file
from tools.read import read_code_file
from tools.write import create_code_file
from tools.search import search_similar_code

from utils.prompts import system_prompt
from embedding.embedd import CodeEmbedder

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Create a directory to store uploaded files
UPLOAD_DIR = os.path.join(os.getcwd(), "uploaded_files")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Use the uploaded folder path if available, otherwise use the environment variable
CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")
print("CODE_REPO_PATH", CODE_REPO_PATH)

# Store session to folder mapping
session_folder_mapping = {}

tools = [    
    {
        "name": "read_code_file",
        "description": "Read complete file content or specific line ranges from a file",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path to the file to be read"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional starting line number to read from (1-based indexing)",
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional ending line number to read until (1-based indexing)",
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "modify_code_file",
        "description": "Modify a code file by either replacing a range of lines or inserting new code",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to modify"
                },
                "new_code": {
                    "type": "string",
                    "description": "New code to insert or replace with"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional starting line number for modification (1-based indexing)"
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional ending line number for modification (1-based indexing)"
                }
            },
            "required": ["file_path", "new_code"]
        }
    },
    {
        "name": "create_code_file",
        "description": "Create a new file or overwrite an existing one with the provided code",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The full path (including filename) where the file should be created"
                },
                "code": {
                    "type": "string",
                    "description": "The code (or text) to write into the file"
                }
            },
            "required": ["file_path", "code"]
        }
    },
    {
        "name": "search_similar_code",
        "description": "Search for similar code chunks in the codebase",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "1-2 sentence description of the code you are looking for"
                }
            },
            "required": ["query"]
        }
    }
]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def process_tool_call(tool_name, tool_input, folder_path=None):
    # If a folder path is provided, temporarily set it as the CODE_REPO_PATH
    original_code_repo_path = None
    if folder_path:
        original_code_repo_path = os.environ.get("CODE_REPO_PATH")
        os.environ["CODE_REPO_PATH"] = folder_path

    try:
        if tool_name == "read_code_file":
            return read_code_file(**tool_input)
        elif tool_name == "modify_code_file":
            return modify_code_file(**tool_input)
        elif tool_name == "create_code_file":
            return create_code_file(**tool_input)
        elif tool_name == "search_similar_code":
            return search_similar_code(**tool_input)
        return None
    finally:
        # Restore the original CODE_REPO_PATH if it was changed
        if original_code_repo_path:
            os.environ["CODE_REPO_PATH"] = original_code_repo_path

tool_name = None 
tool_result = []  # Convert to list if it's not already

def chat(user_message, folder_path=None):
    global tool_name
    global tool_result
    # 🔹 Ensure tool_result is a list
    if not isinstance(tool_result, list):
        tool_result = []  # Reset as an empty list before new tool calls

    messages = [
        {"role": "user", "content": user_message}
    ]
    try:
        response = client.messages.create(
            system=system_prompt,
            model="claude-3-5-sonnet-20240620",
            temperature=0,
            max_tokens=4096,
            tools=tools,
            messages=messages
        )
        print(f"\nInitial Response:")
        print(f"Stop Reason: {response.stop_reason}")
        print(f"Content: {response.content}")
        while response.stop_reason == "tool_use":
            tool_use = next(block for block in response.content if block.type == "tool_use")
            tool_name = tool_use.name
            tool_input = tool_use.input
            print(f"\nTool Used: {tool_name}")
            print(f"Tool Input:")
            print(json.dumps(tool_input, indent=2))
            # Pass the folder_path to process_tool_call if it exists
            tool_result.append(process_tool_call(tool_name, tool_input, folder_path))
            print(f"\nTool Result:")
            print(json.dumps(tool_result, indent=2))
            messages.extend([
                {"role": "assistant", "content": response.content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": str(tool_result)
                        }
                    ]
                }
            ])
            response = client.messages.create(
                system=system_prompt,
                model="claude-3-haiku-20240307",
                temperature=0,
                max_tokens=4096,
                tools=tools,
                messages=messages
            )
        # Extract final text response
        final_response = None
        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )
        print(f"\nFinal Response: {final_response}")
        return final_response
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    
##############################################################################################
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

# Define request models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class FolderUploadResponse(BaseModel):
    session_id: str
    message: str
    file_count: int

async def generate_events(user_message: str, session_id: str):
    global tool_result, tool_name  # Ensure tool_name is accessible

    if session_id not in conversation_histories:
        conversation_histories[session_id] = []

    # Avoid duplicate user messages
    if not conversation_histories[session_id] or conversation_histories[session_id][-1] != {"role": "user", "content": user_message}:
        conversation_histories[session_id].append({"role": "user", "content": user_message})

    try:
        # Check if this session has associated files
        folder_path = None
        if session_id in session_folder_mapping:
            folder_path = os.path.join(UPLOAD_DIR, session_id)
            
        final_response = chat(user_message, folder_path)  # Pass folder_path to chat

        print(f"\nFinal Response: {final_response}")

        # Tools that require canvas updates
        canvas_tools = {"modify_code_file", "create_code_file"}

        # Check if the tool used is one that requires a canvas update
        use_canvas = tool_name in canvas_tools  

        # Avoid duplicate assistant responses
        if not conversation_histories[session_id] or conversation_histories[session_id][-1] != {"role": "assistant", "content": final_response}:
            conversation_histories[session_id].append({"role": "assistant", "content": final_response})

        if use_canvas:
            # Ensure tool_result is treated as a list
            tool_results = tool_result if isinstance(tool_result, list) else [tool_result]

            # After all canvas updates, send the final message to chat
            yield f"data: {json.dumps({'type': 'message', 'content': {'name': 'none', 'text': final_response}})}\n\n"

            # Send canvas updates for each tool call
            for result in tool_results:
                yield f"data: {json.dumps({'type': 'canvas', 'content': {'name': 'none', 'text': result}})}\n\n"
                await asyncio.sleep(5)  # Allow time for frontend to process
        else:
            yield f"data: {json.dumps({'type': 'message', 'content': {'name': 'none', 'text': final_response}})}\n\n"

        tool_result = []
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.get("/file")
#async def fetch_file(session_id: str, file_path: str):
async def fetch_file(request: Request, path: str):

    """
    Fetch a specific file from the uploaded folder structure.

    Args:
        session_id (str): The session ID where the files were uploaded.
        file_path (str): The relative path of the requested file.

    Returns:
        FileResponse: Serves the requested file.
    """

    print(path)
    # Construct full file path
    full_path = os.path.join(UPLOAD_DIR, '3423424sdds' ,  path)
    #print ("\n\n SESSION DIR", full_path)

    # Validate file existence
    if not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")


    return FileResponse(full_path, filename=os.path.basename(full_path))


@app.post("/upload-folder")
async def upload_folder(files: List[UploadFile] = File(...), session_id: str = Form(None)):
    """
    Upload multiple files that represent a folder structure.
    Returns a session_id to use for subsequent chat interactions.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Generate a new session_id if none provided
    if not session_id:
        session_id = "3423424sdds"  # Consider using a UUID instead
    
    # Create a session directory
    session_dir = os.path.join(UPLOAD_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    file_count = 0
    for file in files:
        # Create full path for the file
        file_path = os.path.join(session_dir, file.filename)
        
        # Create directories in the path if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        file_count += 1
    
    # Store the mapping between session and folder
    session_folder_mapping[session_id] = True
    
    # Initialize the embedder
    print("EMBEDDING ...")
    embedder = CodeEmbedder()  # Set verbose to True to see detailed logs
    
    # Embed all code in the SESSION directory, not a constant path
    num_embedded = embedder.embed_directory(session_dir)
    print(f"Embedded {num_embedded} code chunks from {session_dir}")
    
    return FolderUploadResponse(
        session_id=session_id,
        message="Folder uploaded successfully",
        file_count=file_count
    )

@app.post("/chat")
async def chat_endpoint(request_data: ChatRequest):
    try:
        return StreamingResponse(
            generate_events(request_data.message, request_data.session_id),  
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

# Keep the original GET endpoint for backward compatibility
@app.get("/chat")
async def chat_endpoint_get(request: Request):
    try:
        message = request.query_params.get("message", "")
        session_id = "3423424sdds"
        return StreamingResponse(
            generate_events(message, session_id),
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

####################################################################################################
if __name__ == "__main__":
    pass
    # modify_code_file("../local-test-files/pose_classification_model_train.py")