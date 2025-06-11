from pydantic import BaseModel
from typing import List

# Pydantic models for request and response schemas
class QueryRequest(BaseModel):
    """
    Request schema containing the user's query.
    """
    question: str


class SourceDoc(BaseModel):
    """
    Schema for a source document referenced in query responses.
    """
    title: str
    url: str


class QueryResponse(BaseModel):
    """
    Response schema with the generated answer and related source documents.
    """
    answer: str
    source_docs: List[SourceDoc]


class RecommendRequest(BaseModel):
    """
    Request schema for recommendations, specifying the user ID.
    """
    user_id: str


class Recommendation(BaseModel):
    """
    Schema for a recommendation item including a title and explanation.
    """
    title: str
    explanation: str


class TalentRequest(BaseModel):
    """
    Incoming JSON body for talent recommendations.
    """
    request: str  # e.g. "I need an Android developer with 8 years of experience"


class TalentRecommendation(BaseModel):
    """
    One recommended talent.
    """
    name: str
    role: str
    experience: int
    explanation: str