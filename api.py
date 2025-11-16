from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from rag_road_helper import RoadRAGPipeline

class Query(BaseModel):
    query: str

app = FastAPI()

# Allow frontend to call backend from any origin (local browser)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your RAG pipeline
pipeline = RoadRAGPipeline("data/road_issues_example.json")

@app.post("/ask")
def ask(data: Query):
    answer, docs = pipeline.answer(data.query)

    return {
        "answer": answer,
        "documents": [
            {
                "problem": d.problem,
                "clause": d.clause,
                "score": score
            }
            for d, score in docs
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
