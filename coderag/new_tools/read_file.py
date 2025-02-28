from .base import BaseTool

class ReadFileTool(BaseTool):
    def execute(self, user_message: str) -> str:
        """
        Reads the content of a specified code file.

        Parameters:
            user_message (str): The message containing the file path to read.

        Returns:
            str: The content of the file or an error message if the file cannot be read.
        """
        # Extract file path from user message (assuming a simple format)
        file_path = user_message.strip()

        try:
            # Convert relative path to absolute path
            absolute_path = self.convert_to_absolute_path(file_path)

            # Read the file content
            with open(absolute_path, 'r', encoding='utf-8') as file:
                content = file.read()

            return content

        except FileNotFoundError:
            return f"Error: File not found at path: {file_path}"
        except IOError as e:
            return f"Error reading file {file_path}: {str(e)}"


if __name__ == "__main__":
    tool = ReadFileTool(
        system_prompt="You are a helpful assistant that can read code files and return the content.",
        model="claude-3-5-sonnet-20240620",
        temperature=0.0,
        max_tokens=1000
    )
    
    ## main agent will send a query to the tool and the tool will read the files and return the conclusion 
    ## the main agent will also have a list of files that it can read from

      