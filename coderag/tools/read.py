"""
This tool is used to read the content of a file.
It can read the entire file or a specific line range.
"""
from globals import CODE_STORING_PATH
import os
from dotenv import load_dotenv

load_dotenv()

# CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")

def read_code_file(file_path, start_line=None, end_line=None):
    """
    Reads and returns the content of a file at the given path.
    Automatically resolves relative paths to absolute paths using CODE_REPO_PATH.

    Parameters:
        file_path (str): The path to the file to be read (relative or absolute)
        start_line (int, optional): Starting line number to read from (1-based indexing)
        end_line (int, optional): Ending line number to read until (1-based indexing)

    Returns:
        str: The content of the file or specified line range
        
    Raises:
        FileNotFoundError: If the specified file does not exist
        IOError: If there are issues reading the file
        ValueError: If invalid line numbers are provided
    """
    try:
        # Ensure the file path is correctly resolved
        if not os.path.isabs(file_path):
            # Avoid duplicate prepending
            if not file_path.startswith(CODE_STORING_PATH):
                file_path = os.path.join(CODE_STORING_PATH, file_path.lstrip("/"))
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found at path: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as file:
            if start_line is None and end_line is None:
                return file.read()
            
            # Convert to 0-based indexing
            start = (start_line - 1) if start_line else 0
            
            # Read all lines
            lines = file.readlines()
            
            if start_line and start_line < 1:
                raise ValueError("start_line must be greater than 0")
            if end_line and end_line > len(lines):
                raise ValueError(f"end_line exceeds file length of {len(lines)} lines")
            if start_line and end_line and start_line > end_line:
                raise ValueError("start_line cannot be greater than end_line")
                
            # Select specified range
            selected_lines = lines[start:end_line]
            return ''.join(selected_lines)
            
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {file_path}")
    except IOError as e:
        raise IOError(f"Error reading file {file_path}: {str(e)}")


if __name__ == "__main__":
    # Example usage
    try:
        file_path = "../sephora-tiktok-trends-main/backend/invertedIndexData/InvertedIndex.py"
        # Read entire file
        content = read_code_file(file_path)
        print("Complete file content:")
        print(content)
        
        # Read specific line range
        content = read_code_file(file_path, start_line=12, end_line=22)
        print("\nContent from lines 12-22:")
        print(content)
    except (FileNotFoundError, IOError, ValueError) as e:
        print(f"Error: {e}")