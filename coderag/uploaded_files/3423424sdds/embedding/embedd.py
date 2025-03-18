import os
import sys
# Add the project root directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import turbopuffer as tpuf
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from coderag.embedding.summarizer import process_directory, _get_language_from_file_path
import anthropic
from dotenv import load_dotenv
from rerankers import Reranker

load_dotenv()

# Get TurboPuffer API key and set base URL
TURBOPUFFER_API_KEY = os.getenv("TURBOPUFFER_API_KEY")
tpuf.api_base_url = "https://gcp-us-central1.turbopuffer.com"

class CodeEmbedder:
    def __init__(self, collection_name: str = "uploaded_folder", 
                 model_name: str = "all-MiniLM-L6-v2"):
        """Initialize TurboPuffer namespace and sentence transformer."""
        self.namespace = tpuf.Namespace(
            name=collection_name,
            api_key=TURBOPUFFER_API_KEY
        )
        self.model = SentenceTransformer(model_name)

    def embed_directory(self, directory_path: str) -> None:
        """
        Process a directory and embed all code chunks into TurboPuffer.
        
        Args:
            directory_path (str): Path to directory containing code files
                                  (Python, JavaScript, TypeScript, Java)
        """
        # Process all supported code files in directory
        file_chunks = process_directory(directory_path)
        
        for file_path, chunks in file_chunks.items():
            self.embed_chunks(chunks)
            
    def embed_chunks(self, chunks: List[Dict]) -> None:
        """Embed summaries of code chunks into TurboPuffer."""
        for chunk in chunks:
            # Debug print to verify summaries
            print("\n=== Embedding New Chunk ===")
            print(f"File: {chunk['file_path']}")
            print(f"Type: {chunk['type']}")
            print(f"Name: {chunk['name']}")
            print("Summary:", chunk.get("summary", "NO SUMMARY FOUND"))
            
            # Get language from file path
            language = _get_language_from_file_path(chunk['file_path'])
            print(f"Language: {language}")
            print("=" * 50)
            
            # Create shorter document ID using just filename instead of full path
            filename = os.path.basename(chunk['file_path'])
            doc_id = f"{filename}_{chunk['type']}_{chunk['name']}"
            
            # If ID is still too long, hash it
            if len(doc_id.encode('utf-8')) >= 64:
                import hashlib
                doc_id = hashlib.md5(doc_id.encode('utf-8')).hexdigest()
            
            # Prepare metadata - wrap each value in a list
            metadata = {
                "type": [chunk["type"] or ""],
                "name": [chunk["name"] or ""],
                "file_path": [chunk["file_path"] or ""],
                "docstring": [chunk["docstring"] or ""],
                "code": [chunk["code"] or ""],
                "summary": [chunk.get("summary", "")],
                "language": [language or ""]  # Add language to metadata
            }
            
            # Add additional metadata if it exists
            if "metadata" in chunk:
                processed_metadata = {k: [','.join(v) if isinstance(v, list) else (str(v) if v is not None else "")]
                                    for k, v in chunk["metadata"].items()}
                metadata.update(processed_metadata)
            
            # Add parameters if it's a function
            if chunk["type"] == "function":
                metadata["parameters"] = [','.join(chunk["parameters"]) if chunk.get("parameters") else ""]
            
            # Generate embedding for the summary
            summary = chunk.get("summary", "")
            embedding = self.model.encode(summary).tolist()
            
            # Individual upsert to TurboPuffer
            self.namespace.upsert(
                ids=[doc_id],
                vectors=[embedding],
                attributes=metadata,
                distance_metric='cosine_distance',
                schema={
                    "summary": {
                        "type": "string",
                        "full_text_search": True,
                    },
                    "language": {
                        "type": "string",
                        "full_text_search": True,
                    }
                }
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
    
    def rerank_documents(self, query: str, docs: List[str]) -> List[int]:
        """
        Rerank documents based on relevance to the query.
        
        Args:
            query (str): Search query
            
        Returns:
            List[int]: List of reranked indices
        """
        ranker = Reranker("answerdotai/answerai-colbert-small-v1", model_type='colbert', verbose=0)
        # Get the reranked results and convert to list
        reranked = list(ranker.rank(query=query, docs=docs))
        # Create a mapping of original positions to new positions
        original_indices = list(range(len(docs)))
        return [original_indices[i] for i in range(len(reranked))]

    def search(self, query: str, n_results: int = 7, use_hyde: bool = True, language_filter: str = None) -> Dict:
        """
        Search for code chunks using TurboPuffer.
        
        Args:
            query (str): Search query
            n_results (int): Number of results to return
            use_hyde (bool): Whether to use hypothetical document embedding
            language_filter (str): Filter results by programming language (python, javascript, typescript, java)
            
        Returns:
            Dict: Search results
        """
        if use_hyde:
            hypothetical_answer = self.generate_hypothetical_answer(query)
            query_embedding = self.model.encode(hypothetical_answer).tolist()
        else:
            query_embedding = self.model.encode(query).tolist()
        
        # Prepare filter if language is specified
        filter_expr = None
        if language_filter:
            filter_expr = f"language == '{language_filter.lower()}'"
        
        # Query TurboPuffer
        results = self.namespace.query(
            vector=query_embedding,
            top_k=n_results,
            distance_metric="cosine_distance",
            include_attributes=True,
            include_vectors=False,
            #filter=filter_expr
        )
        
        # Extract data from results
        docs = [result.attributes.get("summary", [""])[0] for result in results]
        ids = [result.id for result in results]
        attributes = [result.attributes for result in results]
        distances = [result.dist for result in results]
        
        # Rerank the documents
        reranked_indices = self.rerank_documents(query, docs)
        
        # Reorder results
        return {
            'ids': [ids[i] for i in reranked_indices],
            'documents': [[docs[i] for i in reranked_indices]],
            'metadatas': [[attributes[i] for i in reranked_indices]],
            'distances': [distances[i] for i in reranked_indices]
        }


if __name__ == "__main__":
    
    embedder = CodeEmbedder()
    # embedder.embed_directory("../sephora-tiktok-trends-main")
    
    # Test the search function
    results = embedder.search("Explain how comments are loaded from vector database and how is the chat response generated from them?")
    
    # # Print results in a clean format
    for i, (summary, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
        print(f"\n=== Result {i} ===")
        print(f"File: {metadata['file_path']}")
        print(f"Type: {metadata['type']}")
        print(f"Name: {metadata['name']}")
        print(f"Language: {metadata['language']}")
        print("\nSummary:")
        print(summary)
        print("\nCode:")
        print(metadata['code'])
        print("\nDocstring:")
        print(metadata['docstring'])
        print("\nFunction Calls:")
        print(metadata.get('function_calls', ''))
        print("\nClass Instances:")
        print(metadata.get('class_instances', ''))
        print("=" * 50)
    