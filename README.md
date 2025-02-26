# CodeRag

CodeRag is a powerful code analysis and modification tool that uses AI to help developers understand, search, and modify their codebase efficiently.

## Features

- **Code Search**: Semantic search across your codebase using embeddings
- **Code Analysis**: AI-powered analysis of code structure and functionality
- **Code Modification**: Intelligent code modification with context awareness
- **Code Understanding**: Generate summaries and explanations of code blocks

## Project Structure

```
coderag/
├── __init__.py
├── agent.py           # Main agent for handling code analysis requests
├── main.py           # CLI entry point
├── embedding/        # Code embedding and search functionality
│   ├── embedd.py    # Handles code embedding using SentenceTransformers
│   ├── summarizer.py # Generates code summaries and chunks
│   └── utility.py   # Utility functions for embedding
├── tools/           # Core tool implementations
│   ├── modify.py    # Code modification tools
│   ├── read.py      # File reading tools
│   ├── search.py    # Code search implementation
│   └── write.py     # File writing tools
└── utils/           # Utility modules
    ├── parser.py    # Code parsing using tree-sitter
    └── prompts.py   # System prompts for AI interactions
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/coderag.git
cd coderag
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   Create a `.env` file with:

```
ANTHROPIC_API_KEY=your_api_key_here
CODE_REPO_PATH=/path/to/your/code/repository
```

## Usage

### CLI Interface

Run the main CLI interface:

```bash
cd coderag
python main.py
```

This will start an interactive session where you can ask questions about your codebase.

## Core Components

### Agent (agent.py)

The main interface for handling code analysis requests. It coordinates between user queries and various tools using Claude AI.

### Embedding System (embedding/)

- **embedd.py**: Manages code embeddings using SentenceTransformers and ChromaDB
- **summarizer.py**: Chunks code and generates summaries
- **utility.py**: Helper functions for embedding operations

### Tools (tools/)

- **read.py**: File reading operations
- **modify.py**: Code modification functionality
- **search.py**: Semantic code search implementation
- **write.py**: File writing operations

### Utilities (utils/)

- **parser.py**: Code parsing using tree-sitter
- **prompts.py**: System prompts for AI interactions

## Features in Detail

### Code Search

Uses semantic embeddings to find relevant code snippets based on natural language queries. The search functionality considers:

- Code structure
- Function and class definitions
- Docstrings and comments
- Variable names and patterns

### Code Analysis

- Generates summaries of code blocks
- Identifies patterns and similar implementations
- Analyzes code structure and dependencies

### Code Modification

- Smart code insertion and replacement
- Context-aware modifications
- Maintains code style and structure

## Acknowledgments

- Claude AI by Anthropic for powering the code analysis
- SentenceTransformers for code embedding
- ChromaDB for vector storage
- Tree-sitter for code parsing
