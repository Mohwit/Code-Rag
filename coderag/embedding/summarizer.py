"""Module for chunking and summarizing Python code at class and function levels."""
import sys
import os
from multiprocessing import Pool
import glob

# Get the parent directory and add it to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from utils.parser import (
    get_node_text,
    get_docstring,
    LANGUAGE_CONFIGS,
    PARSERS
)
from embedding.utility import generate_code_summary

# Define language-specific node types
LANGUAGE_NODE_TYPES = {
    'python': {
        'class': 'class_definition',
        'function': 'function_definition',
        'import': ['import_statement', 'import_from_statement'],
        'control_flow': [
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "with_statement"
        ],
        'assignment': [
            "assignment",
            "expression_statement",
            "augmented_assignment"
        ]
    },
    'javascript': {
        'class': 'class_declaration',
        'function': ['function_declaration', 'method_definition', 'arrow_function'],
        'import': ['import_statement', 'import_specifier'],
        'control_flow': [
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "with_statement"
        ],
        'assignment': [
            "assignment_expression",
            "variable_declaration",
            "expression_statement"
        ]
    },
    'typescript': {
        'class': 'class_declaration',
        'function': ['function_declaration', 'method_definition', 'arrow_function'],
        'import': ['import_statement', 'import_specifier'],
        'control_flow': [
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement",
            "with_statement"
        ],
        'assignment': [
            "assignment_expression",
            "variable_declaration",
            "expression_statement"
        ]
    },
    'java': {
        'class': 'class_declaration',
        'function': 'method_declaration',
        'import': ['import_declaration'],
        'control_flow': [
            "if_statement",
            "for_statement",
            "while_statement",
            "try_statement"
        ],
        'assignment': [
            "assignment_expression",
            "variable_declaration",
            "expression_statement"
        ]
    }
}

def _get_language_from_file_path(file_path):
    """Determine the language based on file extension."""
    file_ext = os.path.splitext(file_path)[1].lower()
    for lang, config in LANGUAGE_CONFIGS.items():
        if file_ext in config['extensions']:
            return lang
    return None

def _process_import_node(node, code_bytes, file_path, language):
    """Process an import statement and create a chunk."""
    import_code = get_node_text(node, code_bytes)
    if import_code.strip():
        return {
            "type": "import",
            "name": "import_statement",
            "code": import_code,
            "summary": "Import statement",
            "file_path": file_path,
            "docstring": ""
        }
    return None

def _process_standalone_code(nodes, code_bytes, file_path, start_byte, end_byte):
    """Process standalone code that isn't within classes, functions, or imports."""
    standalone_code = get_node_text(nodes, code_bytes)[start_byte:end_byte]
    if standalone_code.strip():
        return {
            "type": "standalone",
            "name": "standalone_code",
            "code": standalone_code,
            "summary": "Standalone code block with global variables or statements",
            "file_path": file_path,
            "docstring": ""
        }
    return None

def _process_import_nodes(nodes, code_bytes, file_path, start_idx, total_nodes, language):
    """Process consecutive import statements and create a single chunk."""
    import_codes = []
    end_idx = start_idx
    import_types = LANGUAGE_NODE_TYPES[language]['import']
    
    # Collect consecutive import statements
    while end_idx < total_nodes:
        node = nodes[end_idx]
        if node.type not in import_types:
            break
        import_codes.append(get_node_text(node, code_bytes))
        end_idx += 1
    
    if import_codes:
        combined_imports = "\n".join(import_codes)
        return {
            "type": "import",
            "name": "import_statements",
            "code": combined_imports,
            "summary": "Combined import statements",
            "file_path": file_path,
            "docstring": ""
        }, end_idx
    return None, start_idx

def _is_control_flow_node(node, language):
    """Check if node is a control flow statement."""
    return node.type in LANGUAGE_NODE_TYPES[language]['control_flow']

def _is_assignment_or_expr(node, language):
    """Check if node is an assignment or expression."""
    return node.type in LANGUAGE_NODE_TYPES[language]['assignment']

def _process_logical_block(nodes, code_bytes, file_path, start_idx, total_nodes, language):
    """Process a logical block of related statements."""
    block_codes = []
    end_idx = start_idx
    current_context = None
    function_calls = set()
    class_instances = set()
    start_line = nodes[start_idx].start_point[0] + 1  # Adding 1 for 1-based line numbering
    
    while end_idx < total_nodes:
        node = nodes[end_idx]
        
        # Track function calls and class instantiations
        if node.type == "call" or node.type == "call_expression":
            function_node = node.child_by_field_name("function")
            if function_node:
                function_name = get_node_text(function_node, code_bytes)
                function_calls.add(function_name)
        elif node.type == LANGUAGE_NODE_TYPES[language]['class']:
            name_node = node.child_by_field_name("name")
            if name_node:
                class_name = get_node_text(name_node, code_bytes)
                class_instances.add(class_name)
        
        # Skip if this is part of a previously processed block
        if end_idx > start_idx and node.start_byte < nodes[start_idx].end_byte:
            end_idx += 1
            continue
            
        # Start a new context if we encounter a control flow statement
        if _is_control_flow_node(node, language):
            if current_context is None:
                current_context = node.type
                block_codes.append(get_node_text(node, code_bytes))
            else:
                # If we're already in a context and find another control flow,
                # stop here to keep logical blocks separate
                break
        
        # For assignment/expression statements
        elif _is_assignment_or_expr(node, language):
            if current_context is None:
                # Group related assignments/expressions
                if block_codes and len(block_codes) < 5:  # Adjust this threshold as needed
                    block_codes.append(get_node_text(node, code_bytes))
                else:
                    if block_codes:
                        break
                    block_codes.append(get_node_text(node, code_bytes))
            else:
                # If we're in a control flow context, add it to the current block
                block_codes.append(get_node_text(node, code_bytes))
        
        # If we encounter any other type of node, stop the current block
        else:
            if block_codes:
                break
        
        end_idx += 1
    
    if block_codes:
        combined_code = "\n".join(block_codes)
        block_type = current_context if current_context else "code_block"
        end_line = nodes[end_idx - 1].end_point[0] + 1
        
        # Create a meaningful name based on the content
        if current_context:
            name = f"{current_context}_block"
        else:
            # Try to create a meaningful name from the first line
            first_line = block_codes[0].strip().split('\n')[0]
            name = first_line[:30].replace(' ', '_').lower() + "_block"
        
        # Generate AI summary of the code block
        summary = generate_code_summary(combined_code)
        
        return {
            "type": block_type,
            "name": name,
            "code": combined_code,
            "summary": summary,
            "file_path": file_path,
            "docstring": "",
            "metadata": {
                "start_line": start_line,
                "end_line": end_line,
                "function_calls": list(function_calls),
                "class_instances": list(class_instances)
            }
        }, end_idx
    
    return None, start_idx

def chunk_code(file_path):
    """
    Chunks a code file into logical blocks of code.
    Supports Python, JavaScript, TypeScript, and Java.
    """
    chunks = []
    
    try:
        language = _get_language_from_file_path(file_path)
        if not language:
            print(f"Unsupported file type: {file_path}")
            return []
            
        with open(file_path, 'r', encoding='utf-8') as file:
            code_str = file.read()
        code_bytes = bytes(code_str, "utf8")
        
        # Get the appropriate parser for the language
        parser = PARSERS[language]
        tree = parser.parse(code_bytes)
        
        last_end = 0
        nodes = tree.root_node.children
        i = 0
        total_nodes = len(nodes)
        
        while i < total_nodes:
            node = nodes[i]
            
            # Process imports
            import_types = LANGUAGE_NODE_TYPES[language]['import']
            if node.type in import_types:
                import_chunk, new_idx = _process_import_nodes(nodes, code_bytes, file_path, i, total_nodes, language)
                if import_chunk:
                    chunks.append(import_chunk)
                    last_end = nodes[new_idx - 1].end_byte
                    i = new_idx
                    continue
            
            # Process classes
            if node.type == LANGUAGE_NODE_TYPES[language]['class']:
                class_chunk = _process_class(node, code_bytes, file_path, language)
                if class_chunk:
                    chunks.append(class_chunk)
                    last_end = node.end_byte
            
            # Process functions
            elif isinstance(LANGUAGE_NODE_TYPES[language]['function'], list):
                if node.type in LANGUAGE_NODE_TYPES[language]['function']:
                    function_chunk = _process_function(node, code_bytes, file_path, language)
                    if function_chunk:
                        chunks.append(function_chunk)
                        last_end = node.end_byte
            elif node.type == LANGUAGE_NODE_TYPES[language]['function']:
                function_chunk = _process_function(node, code_bytes, file_path, language)
                if function_chunk:
                    chunks.append(function_chunk)
                    last_end = node.end_byte
            
            # Process other code blocks
            else:
                logical_chunk, new_idx = _process_logical_block(nodes, code_bytes, file_path, i, total_nodes, language)
                if logical_chunk:
                    chunks.append(logical_chunk)
                    last_end = nodes[new_idx - 1].end_byte
                    i = new_idx
                    continue
            
            i += 1
        
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        
    return chunks

def _process_class(node, code_bytes, file_path, language):
    """Process a class node and create a chunk with summary."""
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
        
    class_name = get_node_text(name_node, code_bytes)
    class_code = get_node_text(node, code_bytes)
    
    # Get class docstring
    body_node = node.child_by_field_name("body")
    docstring = get_docstring(body_node, code_bytes) if body_node else ""
    
    # Get line numbers
    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    
    # Find function calls and class instances within the class
    function_calls = set()
    class_instances = set()
    
    def traverse_node(node):
        if node.type in ["call", "call_expression"]:
            function_node = node.child_by_field_name("function")
            if function_node:
                function_name = get_node_text(function_node, code_bytes)
                function_calls.add(function_name)
        elif node.type == LANGUAGE_NODE_TYPES[language]['class']:
            name_node = node.child_by_field_name("name")
            if name_node:
                class_name = get_node_text(name_node, code_bytes)
                class_instances.add(class_name)
        for child in node.children:
            traverse_node(child)
    
    traverse_node(node)
    
    # Generate AI summary of the class
    summary = generate_code_summary(class_code)
    
    return {
        "type": "class",
        "name": class_name,
        "code": class_code,
        "summary": summary,
        "file_path": file_path,
        "docstring": docstring,
        "metadata": {
            "start_line": start_line,
            "end_line": end_line,
            "function_calls": list(function_calls),
            "class_instances": list(class_instances)
        }
    }

def _process_function(node, code_bytes, file_path, language):
    """Process a function node and create a chunk with summary."""
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
        
    func_name = get_node_text(name_node, code_bytes)
    func_code = get_node_text(node, code_bytes)
    
    # Get function docstring
    body_node = node.child_by_field_name("body")
    docstring = get_docstring(body_node, code_bytes) if body_node else ""
    
    # Get parameters based on language
    params = []
    parameters_node = node.child_by_field_name("parameters")
    
    if parameters_node:
        if language == 'python':
            for param in parameters_node.children:
                if param.type == "identifier":
                    params.append(get_node_text(param, code_bytes))
        elif language == 'java':
            for param in parameters_node.children:
                if param.type == "formal_parameter":
                    param_name = param.child_by_field_name("name")
                    if param_name:
                        params.append(get_node_text(param_name, code_bytes))
        elif language in ['javascript', 'typescript']:
            for param in parameters_node.children:
                if param.type == "identifier" or param.type == "formal_parameter":
                    params.append(get_node_text(param, code_bytes))
    
    # Get line numbers
    start_line = node.start_point[0] + 1
    end_line = node.end_point[0] + 1
    
    # Find function calls and class instances within the function
    function_calls = set()
    class_instances = set()
    
    def traverse_node(node):
        if node.type == "call":
            function_name = get_node_text(node.child_by_field_name("function"), code_bytes)
            function_calls.add(function_name)
        elif node.type == "class_definition":
            class_name = get_node_text(node.child_by_field_name("name"), code_bytes)
            class_instances.add(class_name)
        for child in node.children:
            traverse_node(child)
    
    traverse_node(node)
    
    # Generate AI summary of the function
    summary = generate_code_summary(func_code)
    
    return {
        "type": "function",
        "name": func_name,
        "code": func_code,
        "summary": summary,
        "file_path": file_path,
        "docstring": docstring,
        "parameters": params,
        "metadata": {
            "start_line": start_line,
            "end_line": end_line,
            "function_calls": list(function_calls),
            "class_instances": list(class_instances)
        }
    }

def process_file(file_path):
    """Process a single file and return its chunks."""
    print(f"Processing file: {file_path}")
    try:
        chunks = chunk_code(file_path)
        return file_path, chunks
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return file_path, []

def process_directory(directory_path, num_processes=None):
    """
    Process all supported code files in the given directory and its subdirectories in parallel.
    
    Args:
        directory_path (str): Path to the directory containing code files
        num_processes (int, optional): Number of processes to use. Defaults to CPU count.
    
    Returns:
        dict: Dictionary mapping file paths to their chunks
    """
    # Get all supported files in the directory and subdirectories
    supported_files = []
    supported_extensions = []
    
    # Collect all supported file extensions from language configs
    for lang, config in LANGUAGE_CONFIGS.items():
        supported_extensions.extend(config['extensions'])
    
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in supported_extensions:
                supported_files.append(os.path.join(root, file))
    
    if not supported_files:
        print(f"No supported code files found in {directory_path}")
        return {}
    
    # Create a process pool
    with Pool(processes=num_processes) as pool:
        # Process all files in parallel
        results = pool.map(process_file, supported_files)
    
    # Convert results to dictionary
    return dict(results)

if __name__ == "__main__":
    # Example usage with directory
    from dotenv import load_dotenv
    load_dotenv()
    test_dir = os.getenv("CODE_REPO_PATH")
    results = process_directory(test_dir)
    
    # Print results for each file
    for file_path, chunks in results.items():
        language = _get_language_from_file_path(file_path)
        print(f"\nFile: {file_path} (Language: {language})")
        print("="*50)
        for chunk in chunks:
            print(f"\nType: {chunk['type']}")
            print(f"Name: {chunk['name']}")
            print(f"Summary: {chunk['summary']}")
            
            # Print metadata information
            if 'metadata' in chunk:
                print("\nMetadata:")
                print(f"  Start Line: {chunk['metadata']['start_line']}")
                print(f"  End Line: {chunk['metadata']['end_line']}")
                if chunk['metadata'].get('function_calls'):
                    print(f"  Function Calls: {', '.join(chunk['metadata']['function_calls'])}")
                if chunk['metadata'].get('class_instances'):
                    print(f"  Class Instances: {', '.join(chunk['metadata']['class_instances'])}")
            
            # Print parameters if it's a function
            if chunk['type'] == 'function' and 'parameters' in chunk:
                print(f"Parameters: {', '.join(chunk['parameters'])}")
            
            print(f"Code:\n{chunk['code']}")
            print("-"*50)
