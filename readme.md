# RAG System with JSON Aggregation

## Overview

This system integrates a **Retrieval-Augmented Generation (RAG)** architecture with **JSON aggregation**, enabling efficient document retrieval and structured data processing.

## Architecture

### Core Components

- **Document Ingestion (`DocumentIngestor`)**
  - Supports multiple file formats (PDF, DOCX, JSON, TXT)
  - Extracts content and metadata
  - Chunks content for non-JSON files
  - Generates embeddings using `SentenceTransformer`

- **RAG System (`RAGSystem`)**
  - Implements semantic search functionality
  - Uses vector similarity for document retrieval
  - Returns ranked results with relevance scores

- **JSON Aggregator (`JSONAggregator`)**
  - Performs aggregation operations on JSON fields
  - Supports nested JSON traversal
  - Provides multiple aggregation types (COUNT, SUM, MEAN, etc.)

- **Embedding Generator (`EmbeddingGenerator`)**
  - Uses `sentence-transformers/all-MiniLM-L6-v2`
  - Generates vector embeddings for text

## Data Flow

1. Documents are uploaded through the API.
2. Content is processed and stored in **Weaviate**.
3. Queries can be performed using **semantic search**.
4. JSON aggregations can be performed on stored documents.

## Installation

### Prerequisites

- Python 3.8+
- `pip` package manager
- Docker (for Weaviate)

### Setup

#### Clone the repository
```bash
git clone https://github.com/your-repo/rag-json-aggregation.git
cd rag-json-aggregation
```

#### Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```


#### Start Weaviate 
```bash
docker-compose up -d
```

#### Run the ingestion and search services
```bash
python3 -m app.main
```

The application will be available at http://localhost:8000

## API Documentation

The API provides the following endpoints:

### Upload Documents

* URL: ```POST /upload```

```bash
curl -X POST -F "file=@/path/to/your/document.pdf" http://localhost:8000/upload
```

### Query Documents

* URL: ```POST /query```

```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "your search query", "limit": 5}' \
  http://localhost:8000/query
```

### Aggregate JSON Field

* URL: ```GET /aggregate/{field_path}```

```bash
# Count aggregation
curl "http://localhost:8000/aggregate/json.customer_id?doc_id=<doc_id>&operation=count"

# Text occurrences
curl "http://localhost:8000/aggregate/json.membership?doc_id=<doc_id>&operation=text_occurrences"

# Numeric operations
curl "http://localhost:8000/aggregate/json.total_spent?doc_id=<doc_id>&operation=sum"
curl "http://localhost:8000/aggregate/json.total_spent?doc_id=<doc_id>&operation=mean"
curl "http://localhost:8000/aggregate/json.total_spent?doc_id=<doc_id>&operation=median"
curl "http://localhost:8000/aggregate/json.total_spent?doc_id=<doc_id>&operation=min"
curl "http://localhost:8000/aggregate/json.total_spent?doc_id=<doc_id>&operation=max"

```


### Notes

* Use ```doc_id``` to specify a particular document



### WIP: Aggregation with Query Text


```bash
curl "http://localhost:8000/aggregate/json.membership?doc_id=<doc_id>&operation=count&query_text=\"Gold\""

```

This should match the query_text with the values in the json field and return the count of the matching values.




## Supported Operations for JSON Aggregation

* COUNT
* SUM
* MEAN
* MODE
* MEDIAN
* MIN
* MAX
* TEXT_OCCURRENCES

## JSON Field Path Notation
* Simple paths: ```json.field1```
* Array access: ```json.field1[].field2```
* Nested arrays: ```json.field1[].field2[].field3```
* Nested objects: ```json.field1.field2.field3```

The architecture is designed to be modular and extensible, with clear separation of concerns between document processing, vector search, and aggregation functionalities.