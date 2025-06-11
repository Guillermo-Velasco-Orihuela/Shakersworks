from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time

from app.core.config import settings
from app.db.session import get_db
from app.models.schemas import RecommendRequest, Recommendation
from app.services.rec_service import RecService
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient
from app.utils.cache import get_cache, cache_get, cache_set
from app.utils.metrics import CACHE_HITS, CACHE_MISSES, REQUEST_LATENCY

router = APIRouter()

# Initialize embedding and vector store clients
emb_client = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
vector_store = VectorStoreClient()

# Cache setup with TTL
cache = get_cache()
CACHE_TTL = 300  # seconds


@router.post("", response_model=List[Recommendation])
def recommend_endpoint(
    body: RecommendRequest,
    db: Session = Depends(get_db),
):
    """
    Generate personalized recommendations for a user, with caching and metrics.
    """
    endpoint = "recommend"
    start = time.time()  # start timing for latency metrics

    # Use user ID as cache key (strip whitespace for consistency)
    uid = body.user_id.strip()
    key = f"recommend:{uid}"

    # Check for cached recommendations
    cached = cache_get(key)
    if cached is not None:
        # Cache hit: record and return
        CACHE_HITS.labels(endpoint=endpoint).inc()
        duration = time.time() - start
        REQUEST_LATENCY.labels(endpoint=endpoint, method="POST").observe(duration)
        return cached

    # Cache miss: record the miss
    CACHE_MISSES.labels(endpoint=endpoint).inc()

    # Generate new recommendations via the RecService
    service = RecService(
        db=db,
        embedding_client=emb_client,
        vector_store=vector_store,
    )
    recs = service.recommend(body.user_id)

    # Store generated recommendations in cache
    cache_set(key, recs, ttl=CACHE_TTL)

    # Record request latency and return results
    duration = time.time() - start
    REQUEST_LATENCY.labels(endpoint=endpoint, method="POST").observe(duration)
    return recs
