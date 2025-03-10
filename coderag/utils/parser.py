import tree_sitter_python as tspython
import tree_sitter_javascript as tsjavascript
import tree_sitter_java as tsjava
import tree_sitter_typescript as tstypescript
from tree_sitter import Language, Parser
import os

# Language configurations
LANGUAGE_CONFIGS = {
    'python': {
        'module': tspython,
        'extensions': ['.py'],
        'docstring_node_type': 'string',
        'class_node_type': 'class_definition',
        'function_node_type': 'function_definition',
        'import_node_types': ['import_from_statement', 'import_statement']
    },
    'javascript': {
        'module': tsjavascript,
        'extensions': ['.js', '.jsx'],
        'docstring_node_type': 'comment',
        'class_node_type': 'class_declaration',
        'function_node_type': ['function_declaration', 'method_definition'],
        'import_node_types': ['import_statement', 'import_specifier']
    },
    'typescript': {
        'module': tstypescript,
        'extensions': ['.ts', '.tsx'],
        'docstring_node_type': 'comment',
        'class_node_type': 'class_declaration',
        'function_node_type': ['function_declaration', 'method_definition'],
        'import_node_types': ['import_statement', 'import_specifier']
    },
    'java': {
        'module': tsjava,
        'extensions': ['.java'],
        'docstring_node_type': 'comment',
        'class_node_type': 'class_declaration',
        'function_node_type': 'method_declaration',
        'import_node_types': ['import_declaration']
    }
}

# Initialize parsers for each language
PARSERS = {}
for lang, config in LANGUAGE_CONFIGS.items():
    try:
        if lang == 'typescript':
            # TypeScript often has a different structure
            # It might have separate parsers for TS and TSX
            try:
                lang_obj = Language(tstypescript.language_typescript())
            except AttributeError:
                # Some versions use this format instead
                lang_obj = Language(tstypescript.get_language("typescript"))
        else:
            lang_obj = Language(config['module'].language())
        
        parser = Parser()
        parser.language = lang_obj
        PARSERS[lang] = parser
    except Exception as e:
        print(f"Failed to initialize {lang} parser: {e}")

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
                # Java return statements might have a different structure
                return_expr = None
                for c in child.children:
                    if c.type not in ["return", ";"]:
                        return_expr = c
                        break
                
                if not return_expr and len(child.children) > 1:
                    return_expr = child.children[1]
                
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

def get_file_info(code_bytes, root_node, indent="", file_extension=".py"):
    """Extract detailed information about a file based on its language."""
    # Determine language from file extension
    language = None
    for lang, config in LANGUAGE_CONFIGS.items():
        if any(file_extension.lower() == ext for ext in config['extensions']):
            language = lang
            break
    
    if not language:
        return f"{indent}Unsupported file type: {file_extension}"

    config = LANGUAGE_CONFIGS[language]
    info = []
    
    for child in root_node.children:
        if child.type == config['class_node_type']:
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
                    # Handle Java method_declaration differently
                    if language == 'java' and method.type == 'method_declaration':
                        method_name = method.child_by_field_name("name")
                        if method_name:
                            method_name = get_node_text(method_name, code_bytes)
                            params = []
                            parameters_node = method.child_by_field_name("parameters")
                            if parameters_node:
                                for param in parameters_node.children:
                                    if param.type == "formal_parameter":
                                        param_name = param.child_by_field_name("name")
                                        if param_name:
                                            params.append(get_node_text(param_name, code_bytes))
                            
                            info.append(f"{indent}  ├── Method: {method_name}({', '.join(params)})")
                            
                            method_body = method.child_by_field_name("body")
                            # Java docstrings are typically comments before the method
                            # This is a simplification - proper Java docstring extraction would need more work
                            method_docstring = None
                            if method.prev_sibling and method.prev_sibling.type == "comment":
                                method_docstring = get_node_text(method.prev_sibling, code_bytes)
                            
                            if method_docstring:
                                info.append(f"{indent}  │   ├── Docstring: {method_docstring}")
                            
                            returns = get_return_info(method_body, code_bytes)
                            if returns:
                                info.append(f"{indent}  │   └── Returns: {', '.join(returns)}")
                    elif method.type == "function_definition":
                        # Existing code for Python methods
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
        
        elif child.type in (config['function_node_type'] if isinstance(config['function_node_type'], list) 
                          else [config['function_node_type']]):
            # Handle Java method_declaration at the top level (outside of classes)
            if language == 'java' and child.type == 'method_declaration':
                name_node = child.child_by_field_name("name")
                func_name = get_node_text(name_node, code_bytes) if name_node else ""
                params = []
                parameters_node = child.child_by_field_name("parameters")
                if parameters_node:
                    for param in parameters_node.children:
                        if param.type == "formal_parameter":
                            param_name = param.child_by_field_name("name")
                            if param_name:
                                params.append(get_node_text(param_name, code_bytes))
                
                info.append(f"{indent}Function: {func_name}({', '.join(params)})")
                
                body_node = child.child_by_field_name("body")
                # Check for Java docstring (comment)
                docstring = None
                if child.prev_sibling and child.prev_sibling.type == "comment":
                    docstring = get_node_text(child.prev_sibling, code_bytes)
                
                if docstring:
                    info.append(f"{indent}  ├── Docstring: {docstring}")
                
                returns = get_return_info(body_node, code_bytes)
                if returns:
                    info.append(f"{indent}  └── Returns: {', '.join(returns)}")
            else:
                # Existing code for Python/TypeScript functions
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
            
        elif child.type in config['import_node_types']:
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
            file_ext = os.path.splitext(entry)[1]
            supported_extensions = [ext for config in LANGUAGE_CONFIGS.values() for ext in config['extensions']]
            
            if file_ext in supported_extensions:
                output.append(f"{indent}└── {entry}")
                try:
                    with open(path, 'r', encoding='utf-8') as file:
                        code_str = file.read()
                    code_bytes = bytes(code_str, "utf8")
                    
                    # Get appropriate parser for the file extension
                    parser = None
                    for lang, config in LANGUAGE_CONFIGS.items():
                        if file_ext in config['extensions']:
                            parser = PARSERS[lang]
                            break
                    
                    if parser:
                        tree = parser.parse(code_bytes)
                        file_info = get_file_info(code_bytes, tree.root_node, indent + "        ", file_ext)
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
    # print("base_name", base_name)
    output = [f"{base_name}/"]
    output.extend(process_directory(project_directory))
    # print("output", output, "\n")
    return "\n".join(output)

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")
    out = parse_project(CODE_REPO_PATH)
    print(out)