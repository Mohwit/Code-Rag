"""Module for chunking and summarizing Python code at class and function levels."""
import sys
import os
from multiprocessing import Pool
import glob

# Get the parent directory and add it to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from utils.parser import (
    PY_LANGUAGE,
    parser,
    get_node_text,
    get_docstring
)
from embedding.utility import generate_code_summary

def _process_import_node(node, code_bytes, file_path):
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

def _process_import_nodes(nodes, code_bytes, file_path, start_idx, total_nodes):
    """Process consecutive import statements and create a single chunk."""
    import_codes = []
    end_idx = start_idx
    
    # Collect consecutive import statements
    while end_idx < total_nodes:
        node = nodes[end_idx]
        if node.type not in ["import_statement", "import_from_statement"]:
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

def _is_control_flow_node(node):
    """Check if node is a control flow statement."""
    return node.type in [
        "if_statement",
        "for_statement",
        "while_statement",
        "try_statement",
        "with_statement"
    ]

def _is_assignment_or_expr(node):
    """Check if node is an assignment or expression."""
    return node.type in [
        "assignment",
        "expression_statement",
        "augmented_assignment"
    ]

def _process_logical_block(nodes, code_bytes, file_path, start_idx, total_nodes):
    """Process a logical block of related statements."""
    block_codes = []
    end_idx = start_idx
    current_context = None
    
    while end_idx < total_nodes:
        node = nodes[end_idx]
        
        # Skip if this is part of a previously processed block
        if end_idx > start_idx and node.start_byte < nodes[start_idx].end_byte:
            end_idx += 1
            continue
            
        # Start a new context if we encounter a control flow statement
        if _is_control_flow_node(node):
            if current_context is None:
                current_context = node.type
                block_codes.append(get_node_text(node, code_bytes))
            else:
                # If we're already in a context and find another control flow,
                # stop here to keep logical blocks separate
                break
        
        # For assignment/expression statements
        elif _is_assignment_or_expr(node):
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
            "docstring": ""
        }, end_idx
    
    return None, start_idx

def chunk_code(file_path):
    """
    Chunks a Python file into logical blocks of code.
    """
    chunks = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            code_str = file.read()
        code_bytes = bytes(code_str, "utf8")
        tree = parser.parse(code_bytes)
        
        last_end = 0
        nodes = tree.root_node.children
        i = 0
        total_nodes = len(nodes)
        
        while i < total_nodes:
            node = nodes[i]
            
            # Process imports
            if node.type in ["import_statement", "import_from_statement"]:
                import_chunk, new_idx = _process_import_nodes(nodes, code_bytes, file_path, i, total_nodes)
                if import_chunk:
                    chunks.append(import_chunk)
                    last_end = nodes[new_idx - 1].end_byte
                    i = new_idx
                    continue
            
            # Process classes and functions
            elif node.type == "class_definition":
                class_chunk = _process_class(node, code_bytes, file_path)
                if class_chunk:
                    chunks.append(class_chunk)
                    last_end = node.end_byte
            elif node.type == "function_definition":
                function_chunk = _process_function(node, code_bytes, file_path)
                if function_chunk:
                    chunks.append(function_chunk)
                    last_end = node.end_byte
            
            # Process other code blocks
            else:
                logical_chunk, new_idx = _process_logical_block(nodes, code_bytes, file_path, i, total_nodes)
                if logical_chunk:
                    chunks.append(logical_chunk)
                    last_end = nodes[new_idx - 1].end_byte
                    i = new_idx
                    continue
            
            i += 1
        
    except Exception as e:
        print(f"Error processing file {file_path}: {str(e)}")
        
    return chunks

def _process_class(node, code_bytes, file_path):
    """Process a class node and create a chunk with summary."""
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
        
    class_name = get_node_text(name_node, code_bytes)
    class_code = get_node_text(node, code_bytes)
    
    # Get class docstring
    body_node = node.child_by_field_name("body")
    docstring = get_docstring(body_node, code_bytes) if body_node else ""
    
    # Generate AI summary of the class
    summary = generate_code_summary(class_code)
    
    return {
        "type": "class",
        "name": class_name,
        "code": class_code,
        "summary": summary,
        "file_path": file_path,
        "docstring": docstring
    }

def _process_function(node, code_bytes, file_path):
    """Process a function node and create a chunk with summary."""
    name_node = node.child_by_field_name("name")
    if not name_node:
        return None
        
    func_name = get_node_text(name_node, code_bytes)
    func_code = get_node_text(node, code_bytes)
    
    # Get function docstring
    body_node = node.child_by_field_name("body")
    docstring = get_docstring(body_node, code_bytes) if body_node else ""
    
    # Get parameters
    params = []
    parameters_node = node.child_by_field_name("parameters")
    if parameters_node:
        for param in parameters_node.children:
            if param.type == "identifier":
                params.append(get_node_text(param, code_bytes))
    
    # Generate AI summary of the function
    summary = generate_code_summary(func_code)
    
    return {
        "type": "function",
        "name": func_name,
        "code": func_code,
        "summary": summary,
        "file_path": file_path,
        "docstring": docstring,
        "parameters": params
    }

def process_file(file_path):
    """Process a single file and return its chunks."""
    print(f"Processing file: {file_path}")
    try:
        chunks = a(file_path)
        return file_path, chunks
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return file_path, []

def process_directory(directory_path, num_processes=None):
    """
    Process all Python files in the given directory in parallel.
    
    Args:
        directory_path (str): Path to the directory containing Python files
        num_processes (int, optional): Number of processes to use. Defaults to CPU count.
    
    Returns:
        dict: Dictionary mapping file paths to their chunks
    """
    # Get all Python files in the directory
    py_files = glob.glob(os.path.join(directory_path, "*.py"))
    
    if not py_files:
        print(f"No Python files found in {directory_path}")
        return {}
    
    # Create a process pool
    with Pool(processes=num_processes) as pool:
        # Process all files in parallel
        results = pool.map(process_file, py_files)
    
    # Convert results to dictionary
    return dict(results)

if __name__ == "__main__":
    # Example usage with directory
    test_dir = "../local-test-files"
    results = process_directory(test_dir)
    
    # Print results for each file
    for file_path, chunks in results.items():
        print(f"\nFile: {file_path}")
        print("="*50)
        for chunk in chunks:
            print(f"\nType: {chunk['type']}")
            print(f"Name: {chunk['name']}")
            print(f"Summary: {chunk['summary']}")
            print(f"Code:\n{chunk['code']}")
