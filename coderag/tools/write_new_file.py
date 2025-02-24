import os

def create_code_file(file_path, code):
    """
    Creates a new file (or overwrites an existing one) at the given file path
    and writes the provided code into it.

    Parameters:
      file_path (str): The full path (including filename) where the file should be created.
      code (str): The code (or text) to write into the file.

    Returns:
      str: A success message indicating the file was created.
    """
    # Ensure the parent directories exist.
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the code to the file.
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)
    
    with open(file_path, "r") as file:
        content = file.read()

    return (f"File created at: {file_path}", content)


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
