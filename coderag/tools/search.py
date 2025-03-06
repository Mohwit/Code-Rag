from embedding.embedd import CodeEmbedder

def search_similar_code(query):
    code_embedder = CodeEmbedder()
    results = code_embedder.search(query, n_results=5)
    
    output = []
    for i, (summary, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        result = f"\n=== Result {i} ===\n"
        result += f"File: {metadata['file_path']}\n"
        result += f"Type: {metadata['type']}\n"
        result += f"Name: {metadata['name']}\n"
        result += "\nSummary:\n"
        result += f"{summary}\n"
        result += "\nCode:\n"
        result += f"{metadata['code']}\n"
        result += "\nDocstring:\n"
        result += f"{metadata['docstring']}\n"
        result += "\nFunction Calls:\n"
        result += f"{metadata['function_calls']}\n"
        result += "\nClass Instances:\n"
        result += f"{metadata['class_instances']}\n"
        result += "=" * 50 + "\n"
        output.append(result)
    
    return "".join(output)
