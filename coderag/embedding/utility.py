import anthropic
from dotenv import load_dotenv

load_dotenv()

def generate_code_summary(code: str):
    """ Generate a summary of the code """
    
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=4096,
        temperature=0,
        system= """You are a helpful assistant that generates a summary of the code.\n
                The summary should be a 3-4 sentence that captures the main idea of the code.\n
                The summary will be utilized to embed the code and create a vector database of the code.\n
                And will be used to search for the code in the vector database based on user query to explain or modify the codebase.\n
                So, make sure to include all the important details of the code in the summary. 
                """,
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
