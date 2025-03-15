import os
from globals import CODE_STORING_PATH
from dotenv import load_dotenv
from embedding.embedd import CodeEmbedder
from embedding.summarizer import process_file

load_dotenv()

# CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")

def create_code_file(file_path, code):
    """
    Creates a new file at the given file path and embeds it in ChromaDB.
    Automatically resolves relative paths to absolute paths using CODE_REPO_PATH.

    Parameters:
        file_path (str): The path (relative or absolute) where the file should be created
        code (str): The code to write into the file

    Returns:
        tuple: (success message, file content)
    """
    # Convert relative path to absolute path if needed
    if not os.path.isabs(file_path):
        file_path = os.path.join(CODE_STORING_PATH, file_path.lstrip('/'))

    # Ensure the parent directories exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the code to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    # Initialize embedder and embed the new file
    embedder = CodeEmbedder()
    _, chunks = process_file(file_path)
    if chunks:
        embedder.embed_chunks(chunks)
    
    # Read and return the file content
    with open(file_path, "r") as file:
        content = file.read()

    return (f"File created and embedded at: {file_path}\n", content)


# Example usage:
if __name__ == "__main__":
    new_code = (
        "def hello_world():\n"
        "    print('Hello, world!')\n"
        "\n"
        "if __name__ == '__main__':\n"
        "    hello_world()\n"
    )
    file_path = "/Users/msingh/Desktop/Demo/pepsico/PoseEstimation-Activity-Classification-master"  # Example file path.
    result = create_code_file(file_path, new_code)
    print(result)