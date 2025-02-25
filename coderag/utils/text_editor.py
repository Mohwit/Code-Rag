import anthropic
import os

# Initialize client with API key (Ensure you have set ANTHROPIC_API_KEY in your environment)
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Send initial request to Claude
response = client.beta.messages.create(
    model="claude-3-7-sonnet-20250219",  # Use the model from the example
    max_tokens=1025,  # Increased max_tokens
    tools=[
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
            "display_number": 1,
        },
        {
            "type": "text_editor_20250124",
            "name": "str_replace_editor",
        },
        {
            "type": "bash_20250124",
            "name": "bash",
        },
    ],
    messages=[{"role": "user", "content": "Open a text editor and write 'Hello, world!'"}],
    betas=["computer-use-2025-01-24"],
    thinking={"type": "enabled", "budget_tokens": 1024},
)

# Print response for debugging
print("Initial Response:", response)

# Extract tool use blocks properly
tool_use_blocks =  [] # Initialize as a list
for block in response.content:
    if hasattr(block, 'type') and block.type == 'tool_use':  # Check for 'type' attribute and its value
        tool_use_blocks.append(block)

print("Tool Use Blocks Detected:", tool_use_blocks)

# Handle tool execution based on detected tool requests
for tool_block in tool_use_blocks:
    if tool_block.name == "str_replace_editor":
        # The anthropic API will handle the text editor actions.
        print("Text editor tool was called")

print("Script completed successfully.")