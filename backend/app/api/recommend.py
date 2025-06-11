from fastapi import APIRouter, HTTPException
from typing import List
from app.core.config import settings
from app.models.schemas import TalentRequest, TalentRecommendation
from app.services.rec_service import RecService

router = APIRouter(tags=["recommend"])

@router.post("", response_model=List[TalentRecommendation])
def recommend_endpoint(body: TalentRequest):
    """
    Recommend the most suitable talents based on a natural-language request.
    """
    try:
        svc = RecService(
            api_key=settings.OPENAI_API_KEY,
            persist_directory=settings.VECTOR_STORE_URL,
        )
        return svc.recommend(body.request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {e}")