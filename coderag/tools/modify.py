
"""
This tool is used to modify a code file by either replacing a range of lines or inserting new code.
"""
from globals import CODE_STORING_PATH
import os
from dotenv import load_dotenv
from embedding.embedd import CodeEmbedder
from embedding.summarizer import process_file
from typing import List, Dict

load_dotenv()

# CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")

def delete_file_embeddings(namespace, file_path: str) -> None:
    """
    Delete all embeddings for a specific file from TurboPuffer.
    
    Args:
        namespace: TurboPuffer namespace
        file_path (str): Path to the file whose embeddings should be deleted
    """
    # Delete documents where file_path matches exactly
    rows_affected = namespace.delete_by_filter(
        ['file_path', 'Eq', file_path]
    )
    
    print(f"Deleted {rows_affected} embeddings for file: {file_path}")

def modify_code_file(file_path, new_code):
    """
    Replaces the entire content of a code file and updates its embeddings in TurboPuffer.

    Parameters:
        file_path (str): Path to the file to modify (relative or absolute)
        new_code (str): New code to replace the entire file content with
    
    Returns:
        tuple: (str, str) - A success message and the updated file content
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        IOError: If there's an error modifying the file
    """

    try:
        # Convert relative path to absolute path if needed
        # if not os.path.isabs(file_path):
        #     file_path = os.path.join(CODE_STORING_PATH, file_path.lstrip('/'))
        


        # Read the old content
        old_code = ""
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                old_code = file.read()

        # Initialize embedder
        embedder = CodeEmbedder()
        
        # Delete existing embeddings for this file
        delete_file_embeddings(embedder.namespace, file_path)
            
        # Write new content to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_code)
        
        # Process and embed the updated file
        _, chunks = process_file(file_path)
        if chunks:
            embedder.embed_chunks(chunks)
            
        # Read and return the updated content
        with open(file_path, 'r', encoding='utf-8') as file:
            updated_content = file.read()
        # print (f"OLD CODE: {old_code}")
        # quit()
        return new_code, old_code, updated_content
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {file_path}")
    except IOError as e:
        raise IOError(f"Error modifying file {file_path}: {str(e)}")


if __name__ == "__main__":
    # Example usage
    try:
        # Create a test file path - use a temporary file for testing
        file_path = os.path.join(CODE_STORING_PATH, "example.py")
        
        # Sample code to write to the file
        new_code = """
def hello_world():
    "
    A simple function that prints a greeting message.
    This is a test function to verify the modify_code_file functionality.
    "
    print("Hello, world! This file was modified by the modify_code_file function.")
    
    # Adding some unique markers for testing embedding
    # TEST_MARKER: This is a test file for the modify_code_file function
    # EMBEDDING_TEST: This text should be indexed in TurboPuffer
    
    return "Hello, world!"

if __name__ == "__main__":
    result = hello_world()
    print(f"Function returned: {result}")
"""
        
        # First, create the file if it doesn't exist
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# Initial content")
            print(f"Created test file at: {file_path}")
        
        # Now test the modify_code_file function
        print(f"Testing modify_code_file on: {file_path}")
        result, content = modify_code_file(file_path, new_code)


        
        print(result)
        print("\nUpdated file content:")
        print("-" * 40)
        print(content)
        print("-" * 40)
        
        print("\nVerification complete. You can check the file and TurboPuffer embeddings.")
        
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}")
