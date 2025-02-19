import uvicorn
import weaviate
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="RAG System",
    description="A system for retrieving information from a knowledge base usin RAG.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup():
    print("RAG System is starting...")

    client = weaviate.connect_to_local(
        host='127.0.0.1',
        port=8080
    )

    if client.is_ready():
        print("Weaviate is ready.")


@app.get("/")
def read_root():
    return {"message": "Welcome to the RAG System!"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
