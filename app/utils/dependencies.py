import weaviate
from functools import lru_cache
from app.core.embeddings_generator import EmbeddingGenerator
from weaviate.collections import Collection
from weaviate.classes.config import Property, DataType, Configure, VectorDistances


@lru_cache()
def weaviate_init() -> weaviate.Client:
    """Initialize Weaviate client with local connection"""
    client = weaviate.connect_to_local(
        host="127.0.0.1",
        port=8080,
    )

    # Create collection if it doesn't exist
    
    try:
        # Check if collection exists
        if "Document" not in client.collections.list_all():
            # Create collection with properties
            collection = client.collections.create(
                name="Document",
                properties=[
                    Property(
                        name="content",
                        data_type=DataType.TEXT,
                        description="The text content of the document chunk"
                    ),
                    Property(
                        name="json",
                        data_type=DataType.OBJECT_ARRAY,
                        description="JSON"
                    ),
                    Property(
                        name="metadata",
                        data_type=DataType.TEXT,
                        description="JSON string containing document metadata"
                    ),
                    Property(
                        name="doc_id",
                        data_type=DataType.TEXT,
                        description="Unique identifier for the document"
                    ),
                    Property(
                        name="chunk_id",
                        data_type=DataType.INT,
                        description="Index of this chunk within the document"
                    ),
                    Property(
                        name="file_type",
                        data_type=DataType.TEXT,
                        description="Type of the source file (pdf, docx, etc.)"
                    )
                ],
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric=VectorDistances.COSINE,
                )
            )
            print("Created Document collection")
        else:
            print("Document collection already exists")

    except Exception as e:
        print(f"Error creating schema: {str(e)}")
        raise

    return client


@lru_cache()
def embedding_generator_init() -> EmbeddingGenerator:
    """Initialize the embedding generator"""
    return EmbeddingGenerator()
