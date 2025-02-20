import weaviate
import json
from app.core.embeddings_generator import EmbeddingGenerator
from typing import List, Dict, Any
from weaviate.classes.query import MetadataQuery


class RAGSystem:
    """ 
    RAG System for semantic search and retrieval of documents
    """

    def __init__(self, store_client: weaviate.Client, embedding_generator: EmbeddingGenerator):
        self.store_client = store_client
        self.embedding_generator = embedding_generator

    def query(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        # Generate query embedding
        query_embedding = self.embedding_generator.generate(query)

        # Query the database
        response = (
            self.store_client.collections
            .get("Document")
            .query
            .near_vector(
                near_vector=query_embedding,
                limit=top_k,
                return_metadata=MetadataQuery(distance=True)
            )
        )

        # Process and format response
        result = []
        for obj in response.objects:
            try:
                metadata = json.loads(obj.properties["metadata"])
            except (json.JSONDecodeError, KeyError):
                metadata = {"error": "Failed to parse metadata"}

            # Get score
            distance = obj.metadata.distance
            similarity = 1-distance

            result.append({
                "content": obj.properties["content"],
                "metadata": metadata,
                "score": similarity,
                "doc_id": obj.properties["doc_id"],
                "chunk_id": obj.properties["chunk_id"],
                "file_type": obj.properties["file_type"]
            })
            
        return result
