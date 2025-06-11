from pydantic import BaseModel
from typing import List

class QueryRequest(BaseModel):
    question: str

class SourceDoc(BaseModel):
    title: str
    url: str

class QueryResponse(BaseModel):
    answer: str
    source_docs: List[SourceDoc]

class RecommendRequest(BaseModel):
    user_id: str

class Recommendation(BaseModel):
    title: str
    explanation: str
