import anthropic

# Initialize the Anthropic client
client = anthropic.Anthropic()

# Define the user message to trigger tool usage
messages = [
    {"role": "user", "content": "Open the text editor and write 'Hello, world!' in it."}
]

# Call Claude with tools enabled
response = client.beta.messages.create(
    model="claude-3-7-sonnet-20250219",
    max_tokens=1024,
    tools=[
        {
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": 1024,
            "display_height_px": 768,
            "display_number": 1,
        },
        {
            "type": "text_editor_20250124",  # Corrected text editor tool
            "name": "str_replace_editor"
        },
        {
            "type": "bash_20250124",  # Fixed bash tool version
            "name": "bash"
        }
    ],
    messages=messages,
    betas=["computer-use-2025-01-24"],

)

# Print the full response to check what tools were used
print(response)
