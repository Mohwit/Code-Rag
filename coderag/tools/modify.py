"""
This tool is used to modify a code file by either replacing a range of lines or inserting new code.
"""

import os
from dotenv import load_dotenv

load_dotenv()

CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")

def modify_code_file(file_path, new_code, start_line=None, end_line=None):
    """
    Modifies a code file. Automatically resolves relative paths to absolute paths
    using CODE_REPO_PATH.

    Parameters:
        file_path (str): Path to the file to modify (relative or absolute)
        new_code (str): New code to insert or replace with
        start_line (int, optional): Starting line number for modification (1-based indexing)
        end_line (int, optional): Ending line number for modification (1-based indexing)
                                If None, new_code will be inserted at start_line
    
    Returns:
        tuple: (str, str) - A success message and the updated file content
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist
        ValueError: If invalid line numbers are provided
    """
    try:
        # Convert relative path to absolute path if needed
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getenv("CODE_REPO_PATH"), file_path.lstrip('/'))

        # Read existing file content
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            
        if start_line and start_line < 1:
            raise ValueError("start_line must be greater than 0")
        if end_line and end_line > len(lines):
            raise ValueError(f"end_line exceeds file length of {len(lines)} lines")
        if start_line and end_line and start_line > end_line:
            raise ValueError("start_line cannot be greater than end_line")
            
        # Convert to 0-based indexing
        start = (start_line - 1) if start_line else 0
        
        # If end_line is provided, replace the range
        # Otherwise insert at start_line
        if end_line:
            lines[start:end_line] = new_code.splitlines(True)
        else:
            lines.insert(start, new_code + '\n')
            
        # Write back to file
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
            
        # Read and return the updated content
        with open(file_path, 'r', encoding='utf-8') as file:
            updated_content = file.read()
            
        return f"File modified successfully at: {file_path}", updated_content
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {file_path}")
    except IOError as e:
        raise IOError(f"Error modifying file {file_path}: {str(e)}")


if __name__ == "__main__":
    # Example usage
    try:
        file_path = "example.py"
        new_code = "def new_function():\n    print('New function added!')\n"
        
        # Insert new code at line 5
        result, content = modify_code_file(file_path, new_code, start_line=5)
        print(result)
        
        # Replace lines 5-7 with new code
        result, content = modify_code_file(file_path, new_code, start_line=5, end_line=7)
        print(result)
        
    except (FileNotFoundError, IOError, ValueError) as e:
        print(f"Error: {e}")

