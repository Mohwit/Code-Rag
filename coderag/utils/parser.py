import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import os

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

def get_node_text(node, code_bytes):
    """Helper function to get node text"""
    return code_bytes[node.start_byte:node.end_byte].decode("utf-8")

def get_docstring(body_node, code_bytes):
    """Extract docstring from a body node"""
    if body_node and len(body_node.children) > 0:
        for child in body_node.children:
            if child.type == "expression_statement":
                expr = child.children[0] if child.children else None
                if expr and expr.type == "string":
                    docstring = get_node_text(expr, code_bytes)
                    # Remove quotes and indentation from docstring
                    return docstring.strip('\'\"').strip()
    return None

def get_return_info(body_node, code_bytes):
    """Extract return information from a body node"""
    returns = []
    if body_node:
        for child in body_node.children:
            if child.type == "return_statement":
                return_expr = child.children[1] if len(child.children) > 1 else None
                if return_expr:
                    returns.append(get_node_text(return_expr, code_bytes))
    return returns

def get_assignments(body_node, code_bytes):
    """Extract assignments from a body node"""
    assignments = []
    if body_node:
        for child in body_node.children:
            if child.type == "assignment":
                left = child.child_by_field_name("left")
                right = child.child_by_field_name("right")
                if left and right:
                    assignments.append((
                        get_node_text(left, code_bytes),
                        get_node_text(right, code_bytes)
                    ))
    return assignments

def get_file_info(code_bytes, root_node, indent=""):
    """Extract detailed information about a single Python file."""
    info = []
    
    for child in root_node.children:
        if child.type == "class_definition":
            name_node = child.child_by_field_name("name")
            class_name = get_node_text(name_node, code_bytes) if name_node else ""
            info.append(f"{indent}Class: {class_name}")
            
            body_node = child.child_by_field_name("body")
            docstring = get_docstring(body_node, code_bytes)
            if docstring:
                info.append(f"{indent}  ├── Docstring: {docstring}")
            
            assignments = get_assignments(body_node, code_bytes)
            if assignments:
                info.append(f"{indent}  ├── Class Attributes:")
                for var, val in assignments:
                    info.append(f"{indent}  │   └── {var} = {val}")
            
            if body_node:
                for method in body_node.children:
                    if method.type == "function_definition":
                        method_name = method.child_by_field_name("name")
                        if method_name:
                            method_name = get_node_text(method_name, code_bytes)
                            params = []
                            parameters_node = method.child_by_field_name("parameters")
                            if parameters_node:
                                for param in parameters_node.children:
                                    if param.type == "identifier":
                                        params.append(get_node_text(param, code_bytes))
                            
                            info.append(f"{indent}  ├── Method: {method_name}({', '.join(params)})")
                            
                            method_body = method.child_by_field_name("body")
                            method_docstring = get_docstring(method_body, code_bytes)
                            if method_docstring:
                                info.append(f"{indent}  │   ├── Docstring: {method_docstring}")
                            
                            returns = get_return_info(method_body, code_bytes)
                            if returns:
                                info.append(f"{indent}  │   └── Returns: {', '.join(returns)}")
        
        elif child.type == "function_definition":
            name_node = child.child_by_field_name("name")
            func_name = get_node_text(name_node, code_bytes) if name_node else ""
            params = []
            parameters_node = child.child_by_field_name("parameters")
            if parameters_node:
                for param in parameters_node.children:
                    if param.type == "identifier":
                        params.append(get_node_text(param, code_bytes))
            
            info.append(f"{indent}Function: {func_name}({', '.join(params)})")
            
            body_node = child.child_by_field_name("body")
            docstring = get_docstring(body_node, code_bytes)
            if docstring:
                info.append(f"{indent}  ├── Docstring: {docstring}")
            
            returns = get_return_info(body_node, code_bytes)
            if returns:
                info.append(f"{indent}  └── Returns: {', '.join(returns)}")
            
        elif child.type in ["import_from_statement", "import_statement"]:
            import_text = get_node_text(child, code_bytes)
            info.append(f"{indent}Import: {import_text}")

    return "\n".join(info)

def process_directory(directory, indent=""):
    """Process directory and return formatted string of project structure with file contents."""
    output = []
    entries = sorted(os.listdir(directory))
    entries = [e for e in entries if not e.startswith('.')]

    for index, entry in enumerate(entries):
        path = os.path.join(directory, entry)
        is_last = (index == len(entries) - 1)
        
        if os.path.isdir(path):
            output.append(f"{indent}├── {entry}/")
            new_indent = f"{indent}│   " if not is_last else f"{indent}    "
            output.extend(process_directory(path, new_indent))
        else:
            if entry.endswith('.py'):
                output.append(f"{indent}└── {entry}")
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        code_str = file.read()
                    code_bytes = bytes(code_str, "utf8")
                    tree = parser.parse(code_bytes)
                    file_info = get_file_info(code_bytes, tree.root_node, indent + "        ")
                    if file_info:
                        output.append(f"{indent}        |")
                        output.append(file_info)
                except Exception as e:
                    output.append(f"{indent}        | Error parsing file: {str(e)}")
            else:
                output.append(f"{indent}└── {entry}")

    return output

def parse_project(project_directory):
    """Main function to parse the project."""
    base_name = os.path.basename(project_directory)
    print("base_name", base_name)
    output = [f"{base_name}/"]
    output.extend(process_directory(project_directory))
    print("output", output, "\n")
    return "\n".join(output)

if __name__ == "__main__":
    out = parse_project("../local-test-files")
    print(out)