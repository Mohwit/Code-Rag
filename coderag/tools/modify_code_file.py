import os

import os

def modify_code_file(file_path, new_code):
    """
    Overwrites an existing file or creates a new file with the provided code.

    Parameters:
      file_path (str): The full path (including filename) where the file should be created.
      new_code (str): The code (or text) to write into the file.

    Returns:
      str: The new code that was written to the file.
    """
    # Ensure the parent directories exist
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Write the new code to the file
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_code)
        
    return new_code


# Example usage:
if __name__ == "__main__":
    file_path = "./local-test-files/utils.py"  # Example file path.
    result = modify_code_file(file_path)
    print(result)
