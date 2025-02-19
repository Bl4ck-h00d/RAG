from fastapi import APIRouter, UploadFile, HTTPException, File
from typing import Optional, List
import uuid
from app.types.query import QueryRequest, QueryResponse


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

        # TODO: ingest the file

        return {
            "doc_id": doc_id,
            "filename": file.filename,
            "file_extension": file_extension,
            "file_size": file.size
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

    # TODO: implement query logic

    return {}
