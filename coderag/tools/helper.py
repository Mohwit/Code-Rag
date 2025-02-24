import tree_sitter_python as tspython
from tree_sitter import Language, Parser
import os

# Initialize the Python parser.
PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def extract_structure(file_path):
    """Extracts function and class locations from a Python file."""
    with open(file_path, "r", encoding="utf-8") as file:
        code = file.read()

    tree = parser.parse(bytes(code, "utf8"))
    root_node = tree.root_node

    structure = {"classes": {}, "functions": {}}

    # Iterate over top-level nodes in the file.
    for child in root_node.children:
        if child.type == "class_definition":
            class_name = get_node_name(child, code)
            structure["classes"][class_name] = {
                "start": child.start_byte,
                "end": child.end_byte,
                "file": file_path,
                "functions": {}  # To hold methods inside the class.
            }
            extract_class_functions(child, code, structure["classes"][class_name]["functions"], file_path)
        elif child.type == "function_definition":
            function_name = get_node_name(child, code)
            structure["functions"][function_name] = {
                "start": child.start_byte,
                "end": child.end_byte,
                "file": file_path,
            }
    return structure


def extract_class_functions(class_node, code, class_functions, file_path):
    """
    Extracts function definitions inside a class.
    Looks for the 'body' child node and iterates over its children.
    """
    body_node = class_node.child_by_field_name("body")
    if body_node:
        for member in body_node.children:
            if member.type == "function_definition":
                function_name = get_node_name(member, code)
                class_functions[function_name] = {
                    "start": member.start_byte,
                    "end": member.end_byte,
                    "file": file_path,
                }


def get_node_name(node, code):
    """Extracts the name of a class or function from a node."""
    name_node = node.child_by_field_name("name")
    if name_node:
        return code[name_node.start_byte:name_node.end_byte]
    return ""


def build_project_structure(directory):
    """Builds a mapping of all functions and classes (and their methods) in a project."""
    structure = {"classes": {}, "functions": {}}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                file_structure = extract_structure(file_path)
                # Merge file-level classes and functions into the overall structure.
                structure["classes"].update(file_structure["classes"])
                structure["functions"].update(file_structure["functions"])
    return structure