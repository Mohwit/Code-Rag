import os
import sys
# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from coderag.embedding.summarizer import process_directory
import anthropic
from dotenv import load_dotenv

load_dotenv()

class CodeEmbedder:
    def __init__(self, collection_name: str = "code_chunks", persist_directory: str = "../chroma_db", 
                 model_name: str = "all-MiniLM-L6-v2"):
        """Initialize ChromaDB client, collection, and sentence transformer."""
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=None  # We'll handle embeddings ourselves
        )
        self.model = SentenceTransformer(model_name)

    def embed_directory(self, directory_path: str) -> None:
        """
        Process a directory and embed all code chunks into ChromaDB.
        
        Args:
            directory_path (str): Path to directory containing Python files
        """
        # Process all Python files in directory
        file_chunks = process_directory(directory_path)
        
        for file_path, chunks in file_chunks.items():
            self.embed_chunks(chunks)
            
    def embed_chunks(self, chunks: List[Dict]) -> None:
        """
        Embed summaries of code chunks into ChromaDB, storing the actual code as metadata.
        
        Args:
            chunks (List[Dict]): List of code chunk dictionaries containing summaries
        """
        for chunk in chunks:
            # Debug print to verify summaries
            print("\n=== Embedding New Chunk ===")
            print(f"File: {chunk['file_path']}")
            print(f"Type: {chunk['type']}")
            print(f"Name: {chunk['name']}")
            print("Summary:", chunk.get("summary", "NO SUMMARY FOUND"))
            print("=" * 50)
            
            # Create document ID from file path and chunk name
            doc_id = f"{chunk['file_path']}_{chunk['type']}_{chunk['name']}"
            
            # Prepare metadata, converting None to empty string
            metadata = {
                "type": chunk["type"] or "",
                "name": chunk["name"] or "",
                "file_path": chunk["file_path"] or "",
                "docstring": chunk["docstring"] or "",
                "code": chunk["code"] or ""  # Store the actual code as metadata
            }
            
            # Add additional metadata if it exists
            if "metadata" in chunk:
                processed_metadata = {k: ','.join(v) if isinstance(v, list) else (str(v) if v is not None else "")
                                    for k, v in chunk["metadata"].items()}
                metadata.update(processed_metadata)
            
            # Add parameters if it's a function
            if chunk["type"] == "function":
                metadata["parameters"] = ','.join(chunk["parameters"]) if chunk.get("parameters") else ""
            
            # Generate embedding for the summary instead of code
            summary = chunk.get("summary", "")  # Get the summary, default to empty string if not present
            embedding = self.model.encode(summary).tolist()
            
            # Add to ChromaDB collection with summary as document
            self.collection.add(
                documents=[summary],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
    def generate_hypothetical_answer(self, query: str) -> str:
        """
        Generate a hypothetical code summary that would answer the query.
        This mimics the format of our stored code summaries.
        
        Args:
            query (str): Search query
            
        Returns:
            str: Hypothetical code summary
        """
        hyde_prompt = f"""Given this question about code: "{query}"
        Write a brief technical summary that would answer this question, as if describing a relevant code snippet.
        Focus on implementation details and keep it concise (2-3 sentences)."""
        
        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            temperature=0,
            max_tokens=4096,
            messages=[{"role": "user", "content": hyde_prompt}]
        )
        
        return response.content[0].text

    def search(self, query: str, n_results: int = 7, use_hyde: bool = True) -> List[Dict]:
        """
        Search for code chunks similar to query using HYDE technique.
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
            use_hyde (bool): Whether to use HYDE technique
            
        Returns:
            List[Dict]: List of matching summaries with metadata (including code)
        """
        if use_hyde:
            # Generate hypothetical answer and use it for embedding
            hypothetical_answer = self.generate_hypothetical_answer(query)
            query_embedding = self.model.encode(hypothetical_answer).tolist()
        else:
            # Use original query directly
            query_embedding = self.model.encode(query).tolist()
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        return results

if __name__ == "__main__":
    embedder = CodeEmbedder()
    embedder.embed_directory("../sephora-tiktok-trends-main")
    
    # Test the search function
    # results = embedder.search("Explain how comments are loaded from vector database and how is the chat response generated from them?")
    
    # # Print results in a clean format
    # for i, (summary, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
    #     print(f"\n=== Result {i} ===")
    #     print(f"File: {metadata['file_path']}")
    #     print(f"Type: {metadata['type']}")
    #     print(f"Name: {metadata['name']}")
    #     print("\nSummary:")
    #     print(summary)
    #     print("\nCode:")
    #     print(metadata['code'])
    #     print("\nDocstring:")
    #     print(metadata['docstring'])
    #     print("\nFunction Calls:")
    #     print(metadata['function_calls'])
    #     print("\nClass Instances:")
    #     print(metadata['class_instances'])
    #     print("=" * 50)
    