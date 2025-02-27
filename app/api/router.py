from fastapi import APIRouter, UploadFile, HTTPException, File, Query
from typing import Optional, List
import uuid
from io import BytesIO
from app.types.query import QueryRequest, QueryResponse
from app.core.document_ingestor import DocumentIngestor
from app.utils.dependencies import weaviate_init, embedding_generator_init
from app.core.rag import RAGSystem
from app.core.json_aggregator import JSONAggregator, AggregationOperationType

router = APIRouter()


@router.post('/upload')
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a file to the knowledge base.
    Supports PDF, DOCX, JSON and TXT files.
    """

    try:

        # Generate unique doc_id
        doc_id = str(uuid.uuid4())

        # Validate file extension
        allowed_extensions = ["pdf", "docx", "json", "text"]
        file_extension = file.filename.split(".")[-1]

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, detail=f"Unsupported file extension. Only {', '.join(allowed_extensions)} are allowed.")

        # Initialize the ingestor
        ingestor = DocumentIngestor(
            store_client=weaviate_init(),
            embedding_generator=embedding_generator_init()
        )

        content = await file.read()
        file_obj = BytesIO(content)
        file_obj.name = file.filename

        # Process the file
        ingestor.process_document(
            file=file_obj,
            filename=file.filename,
            doc_id=doc_id
        )

        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "file_extension": file_extension,
            "file_size": file.size,
            "message": "Document processed successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing document: {str(e)}"
        )


@router.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the knowledge base for relevant documents based on the provided search terms.
    """

    try:
        # Initialize the RAG system
        rag_system = RAGSystem(
            store_client=weaviate_init(),
            embedding_generator=embedding_generator_init()
        )

        # Query the database
        results = rag_system.query(
            query=request.query,
            top_k=request.limit if request.limit else 5
        )

        return QueryResponse(query=request.query, results=results)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error querying documents: {str(e)}"
        )


@router.get("/aggregate/{field_path}")
async def aggregate_json_field(
    field_path: str,
    operation: AggregationOperationType,
    doc_id: Optional[str] = None,
    min_occurrences: Optional[str] = "1",
    distance: Optional[float] = Query(None, ge=0.0, le=1.0),
    query_text: Optional[str] = None,
):
    """ 
    Perform aggregation operations on json fields
    """

    try:
        # Initialize JSONAggregator
        processor = JSONAggregator(
            weaviate_init(), embedding_generator=embedding_generator_init())
        result = processor.aggregate(
            field_path=field_path,
            operation=operation,
            doc_id=doc_id,
            min_occurrences=int(min_occurrences),
            distance=distance,
            query_text=query_text
        )
        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error aggregating JSON field: {str(e)}"
        )
