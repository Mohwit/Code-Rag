import anthropic
from abc import ABC, abstractmethod
import os
class BaseTool(ABC):
    def __init__(self, system_prompt: str, model: str = "claude-3-5-sonnet-20240620", temperature: float = 0.0, max_tokens: int = 1000):
        self.client = anthropic.Anthropic()
        self.system_prompt = system_prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    def execute(self, user_message: str) -> str:
        pass
    
    def convert_to_absolute_path(self, file_path: str) -> str:
        # Convert relative path to absolute path if needed
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getenv("CODE_REPO_PATH"), file_path.lstrip('/'))

        # Ensure the parent directories exist
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        print(f"Converted {file_path} to absolute path: {file_path}")
        return file_path
    