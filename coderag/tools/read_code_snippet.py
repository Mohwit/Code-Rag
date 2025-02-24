from .helper import build_project_structure


def read_code_snippet(name):
    """
    Reads and returns the code of a function or class (or method) from the structure.
    `name`: The name of the function or class (or method).
    """
    structure = build_project_structure("../local-test-files")
    
    # Look for a standalone function.
    if name in structure["functions"]:
        item = structure["functions"][name]
    # Look for a class.
    elif name in structure["classes"]:
        item = structure["classes"][name]
    else:
        # Check within class functions (methods).
        for cls, cls_info in structure["classes"].items():
            if name in cls_info["functions"]:
                item = cls_info["functions"][name]
                break
        else:
            return f"Error: '{name}' not found in project structure."

    with open(item["file"], "r", encoding="utf-8") as file:
        file.seek(item["start"])
        code_snippet = file.read(item["end"] - item["start"])
    

    return (f"File: {item['file']}\n\n{code_snippet}", code_snippet)


# Example Usage
if __name__ == "__main__":
    
    # Example: Fetch class "Book" snippet.
    print("\nFetching class 'Book' snippet:")
    print(read_code_snippet("TransactionService"))

    # Example: Fetch method "add_book" snippet from within a class.
    print("\nFetching function/method 'add_book' snippet:")
    print(read_code_snippet("list_transactions"))
