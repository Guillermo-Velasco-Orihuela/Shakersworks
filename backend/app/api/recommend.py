# backend/app/api/recommend.py

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time

from app.config import settings
from app.db.session import get_db
from app.models.schemas import RecommendRequest, Recommendation
from app.services.rec_service import RecService
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient
from app.utils.cache import get_cache, cache_get, cache_set
from app.utils.metrics import CACHE_HITS, CACHE_MISSES, REQUEST_LATENCY

router = APIRouter()

emb_client   = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
vector_store = VectorStoreClient()

cache     = get_cache()
CACHE_TTL = 300

@router.post("", response_model=List[Recommendation])
def recommend_endpoint(
    body: RecommendRequest,
    db: Session = Depends(get_db),
):
    endpoint = "recommend"
    start = time.time()

    uid = body.user_id.strip()
    key = f"recommend:{uid}"

    cached = cache_get(key)
    if cached is not None:
        CACHE_HITS.labels(endpoint=endpoint).inc()
        duration = time.time() - start
        REQUEST_LATENCY.labels(endpoint=endpoint, method="POST").observe(duration)
        return cached

    CACHE_MISSES.labels(endpoint=endpoint).inc()

    service = RecService(
        db=db,
        embedding_client=emb_client,
        vector_store=vector_store,
    )
    recs = service.recommend(body.user_id)

    cache_set(key, recs, ttl=CACHE_TTL)

    duration = time.time() - start
    REQUEST_LATENCY.labels(endpoint=endpoint, method="POST").observe(duration)
    return recs
