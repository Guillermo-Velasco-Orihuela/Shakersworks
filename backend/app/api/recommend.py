from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.models.schemas import RecommendRequest, Recommendation
from app.services.rec_service import RecService
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient
from app.utils.cache import get_cache, cache_get, cache_set

router = APIRouter()

emb_client   = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
vector_store = VectorStoreClient(url=settings.VECTOR_STORE_URL)

cache      = get_cache()
CACHE_TTL  = 300  # seconds

@router.post("", response_model=List[Recommendation])
def recommend_endpoint(
    body: RecommendRequest,
    db: Session = Depends(get_db),
):
    # Normalize user_id and build cache key
    uid = body.user_id.strip()
    cache_key = f"recommend:{uid}"

    # 1) Try to return cached recommendations
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    # 2) Otherwise compute via RecService
    service = RecService(
        db=db,
        embedding_client=emb_client,
        vector_store=vector_store,
    )
    recs = service.recommend(body.user_id)

    # 3) Cache and return
    cache_set(cache_key, recs, ttl=CACHE_TTL)
    return recs
