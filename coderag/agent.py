""" Agent for code analyzer """

import anthropic
import json
import os
from dotenv import load_dotenv

from tools.read_code_snippet import read_code_snippet
from tools.modify_code_snippet import modify_code_snippet
from tools.write_new_file import create_code_file
from tools.modify_code_file import modify_code_file

from utils.prompts import system_prompt

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")
print("CODE_REPO_PATH", CODE_REPO_PATH)


tools = [
    {
        "name": "read_code_snippet",
        "description": "Read code snippets from different section of code base",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of function or class to read, e.g. add_book, TransactionService, Book",
                }
            },
            "required": ["name"],
        },
    },
    {
        "name": "modify_code_snippet",
        "description": "Modify different section of the code base",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The function or class to modify",
                },
                "new_code": {
                    "type": "string",
                    "description": "The new code for function or class to modify"
                }
            },
            "required": ["name", "new_code"],
        },
    },
    {
        "name": "create_code_file",
        "description": "Create a new code file and write complete code from scratch",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The complete file path where the new code file is needed to be created.",
                },
                "code": {
                    "type": "string",
                    "description": "The complete code that to be needed to write in the file."
                }
            },
            "required": ["file_path", "code"],
        },
    },
    {
        "name": "read_file",
        "description": "Read complete files content",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The complete file path where the new code file is needed to be created.",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "modify_code_file",
        "description": "Modify the complete code of the file",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The complete file path where the new code file is needed to be created.",
                },
                "new_code": {
                    "type": "string",
                    "description": "The complete code that to be needed to write in the file."
                }
            },
            "required": ["file_path", "new_code"],
        },
    }
]

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def process_tool_call(tool_name, tool_input):
    if tool_name == "read_code_snippet":
        return read_code_snippet(tool_input["name"])
    elif tool_name == "modify_code_snippet":
        return modify_code_snippet(tool_input["name"], tool_input["new_code"])  # Fixed parameter passing
    return None

def chat(user_message):
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")
    messages = [
        {"role": "user", "content": user_message}
    ]
    try:
        response = client.messages.create(
            system= system_prompt,
            model="claude-3-haiku-20240307",
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
                system= system_prompt,
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
        return final_response
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return None
    

if __name__ == "__main__":
    modify_code_file("../local-test-files/pose_classification_model_train.py")