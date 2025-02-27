""" Agent for code analyzer """
""" Testing"""
import anthropic
import json
import os
from dotenv import load_dotenv

from tools.modify import modify_code_file
from tools.read import read_code_file
from tools.write import create_code_file
from tools.search import search_similar_code

from utils.prompts import system_prompt

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")
print("CODE_REPO_PATH", CODE_REPO_PATH)


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
        "description": "Modify a code file by replacing a range of lines with new code. When modifying existing code, start_line and end_line must be specified to indicate the exact lines to replace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to modify"
                },
                "new_code": {
                    "type": "string",
                    "description": "New code to replace the specified line range"
                },
                "start_line": {
                    "type": "integer",
                    "description": "Starting line number for modification (1-based indexing). Must be provided when modifying existing code."
                },
                "end_line": {
                    "type": "integer",
                    "description": "Ending line number for modification (1-based indexing). Must be provided when modifying existing code."
                }
            },
            "required": ["file_path", "new_code", "start_line", "end_line"]
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

def process_tool_call(tool_name, tool_input):
    if tool_name == "read_code_file":
        return read_code_file(**tool_input)
    elif tool_name == "modify_code_file":
        return modify_code_file(**tool_input)
    elif tool_name == "create_code_file":
        return create_code_file(**tool_input)
    elif tool_name == "search_similar_code":
        return search_similar_code(**tool_input)
    return None

def chat(user_message, messages=None):
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
    
    # Initialize or update messages list
    if messages is None:
        messages = []
    messages.append({"role": "user", "content": user_message})
    
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
            tool_result = process_tool_call(tool_name, tool_input)
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
            # print(f"\nFollow-up Response:")
            # print(f"Stop Reason: {response.stop_reason}")
            # print(f"Content: {response.content}")
        # Extract final text response
        final_response = None
        final_response = next(
            (block.text for block in response.content if hasattr(block, "text")),
            None,
        )
        print(f"\nFinal Response: {final_response}")
        return final_response, messages
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None, messages
    

if __name__ == "__main__":
    pass
    # modify_code_file("../local-test-files/pose_classification_model_train.py")