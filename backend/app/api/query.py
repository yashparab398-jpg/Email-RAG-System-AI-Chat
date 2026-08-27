from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(
    prefix="/query",
    tags=["Query"]
)


class QueryRequest(BaseModel):

    question: str = Field(
        ...,
        min_length=1,
        description="Natural language question about the Enron emails"
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Number of emails to retrieve"
    )


@router.post("")
def query(request: QueryRequest):

    from app.services.rag_service import answer_question

    result = answer_question(
        request.question,
        top_k=request.top_k
    )

    return {
        "question": request.question,
        "answer": result["answer"],
        "confidence": result["confidence"],
        "sources": result["sources"]
    }