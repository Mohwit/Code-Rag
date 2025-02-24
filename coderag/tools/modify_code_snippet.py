import textwrap
import json
from .helper import build_project_structure

def compute_line_col(content, byte_offset):
    """
    Computes (line, column) given a file content (as string) and a byte offset.
    Lines and columns are 0-indexed.
    """
    current_offset = 0
    lines = content.splitlines(keepends=True)
    for i, line in enumerate(lines):
        if current_offset + len(line) > byte_offset:
            col = byte_offset - current_offset
            return (i, col)
        current_offset += len(line)
    # Fallback: return the last line if something goes wrong.
    return (len(lines) - 1, 0)


def modify_code_snippet(name, new_code):
    """
    Updates the code for a given function, class, or method with `new_code`.
    Uses line/column positions to replace the block while preserving indentation.
    After an update, the stored positions are no longer valid—you should rebuild the project structure.
    
    Parameters:
      name (str): The name of the function, class, or method to update.
      new_code (str): The new code that will replace the existing block.
    
    Returns:
      A message indicating success or an error if the name is not found.
    """
    
    structure = build_project_structure("")
    
    # Locate the target item.
    item = None
    if name in structure["functions"]:
        item = structure["functions"][name]
    elif name in structure["classes"]:
        item = structure["classes"][name]
    else:
        for cls, cls_info in structure["classes"].items():
            if name in cls_info["functions"]:
                item = cls_info["functions"][name]
                break
    if item is None:
        return f"Error: '{name}' not found in project structure."

    file_path = item["file"]
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        file.seek(0)
        full_content = file.read()  # for fallback

    # Use stored start_point and end_point if available, otherwise compute them.
    if "start_point" in item:
        start_line, start_col = item["start_point"]
    else:
        start_line, start_col = compute_line_col(full_content, item["start"])
    if "end_point" in item:
        end_line, end_col = item["end_point"]
    else:
        end_line, end_col = compute_line_col(full_content, item["end"])

    # Get the base indentation from the first non-empty line of the block.
    base_indent = ""
    for line in lines[start_line : end_line + 1]:
        stripped = line.lstrip()
        if stripped:
            base_indent = line[: len(line) - len(stripped)]
            break

    # Dedent the new code (remove any common indentation) and reindent with base_indent.
    dedented_new_code = textwrap.dedent(new_code).rstrip("\n")
    reindented_new_lines = [
        (base_indent + line if line.strip() != "" else line)
        for line in dedented_new_code.splitlines()
    ]

    # Rebuild the file content:
    # - The block to be replaced spans from start_line (starting at start_col) to end_line (ending at end_col).
    before_block = lines[:start_line]
    after_block = lines[end_line + 1 :]

    # If the block starts mid-line, preserve the part before start_col.
    if start_col > 0:
        before_block[-1] = before_block[-1][:start_col]
    # If the block ends mid-line, preserve the part after end_col.
    if end_line < len(lines):
        if end_col < len(lines[end_line]):
            after_line = lines[end_line]
            after_block.insert(0, after_line[end_col:])

    new_block = [line + "\n" for line in reindented_new_lines]  # add newline for each line

    # Assemble the updated content.
    new_content = "".join(before_block + new_block + after_block)

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(new_content)
        
    # with open(file_path, "r") as file:
    #     content = file.read()
    
    return (f"Updated '{name}' in {file_path}. (Rebuild the project structure mapping if needed.)" , new_code)


# Example Usage:
if __name__ == "__main__":
    
    # Example: Update the code for "add_book" (modify its content).
    new_add_book_code = (
        "def add_book(self, title, author):\n"
        "    # Updated implementation\n"
        "    book = Book(title, author)\n"
        "    self.books.append(book)\n"
        "    print(f\"Book modified successfully: {book}\")\n"
    )
    update_message = modify_code_snippet("add_book", new_add_book_code)
    print("\nUpdate result:")
    print(update_message)
    
