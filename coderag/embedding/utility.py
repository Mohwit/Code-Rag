import anthropic
from dotenv import load_dotenv

load_dotenv()

def generate_code_summary(code: str):
    """ Generate a summary of the code """
    
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        temperature=0,
        system="You are a helpful assistant that generates a summary of the code.",
        messages=[
            {"role": "user", "content": code}
        ]
    )
    summary = response.content[0].text
    return summary
    
    

if __name__ == "__main__":
    code = """
    def generate_code_summary(code: str):
        ```Generate a summary of the code ```
        summary = ""
        return summary
    """
    print(generate_code_summary(code))
