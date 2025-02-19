
from typing import BinaryIO, Dict, Any
from datetime import datetime
import pdfplumber


class DocumentIngestor:
    def __init__(self, store_client, embedding_generator):
        self.store_client = store_client
        self.embedding_generator = embedding_generator

    def process_document(self, file: BinaryIO, filename: str, doc_id: str):
        """ 
        Process the document and ingest it into the database
        """

        file_type = filename.split('.')[-1].lower()
        metadata = self._extract_metadata(file, file_type)
        content = self._extract_content(file, file_type)

        # Chunkify the content
        chunks = self._chunkify_content(content)

        # Generate embeddings for each chunk
        for idx, chunk in enumerate(chunks):
            embedding = self.embedding_generator.generate(chunk)
            document = self.store_client.collections.get("Document")

        # Store the document metadata and embeddings in the database
        self._store_document(doc_id, metadata, embeddings)

    def _extract_metadata(self, file: BinaryIO, file_type: str) -> Dict[str, Any]:
        """
        Extract metadata from the document
        """

        metadata = {
            "file_type": file_type,
            "timestamp": datetime.now().isoformat()
        }

        try:
            match file_type:
                case "pdf":
                    pos = file.tell()
                    file.seek(0)

                    with pdfplumber.open(file) as pdf:
                        pdf_meta = pdf.metadata
                        metadata.update({
                            "file_type": file_type,
                            "title": pdf_meta.get("Title", "Untitled"),
                            "author": pdf_meta.get("Author", "Unknown"),
                            "page_count": len(pdf.pages),
                            "creation_date": pdf_meta.get("CreationDate", "Unknown"),
                            "modified_date": pdf_meta.get("ModDate", "Unknown"),
                        })
                    file.seek(pos)
                
                case "docx":
                    # TODO: Implement docx metadata extraction
                    pass

                case "json":
                    # TODO: Implement JSON metadata extraction
                    pass

                case "txt":
                    # TODO: Implement TXT metadata extraction
                    pass
        except Exception as e:
            print(f"Error extracting metadata: {e}")
