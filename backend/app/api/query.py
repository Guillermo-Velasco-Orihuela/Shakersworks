# backend/app/api/query.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import time

from app.config import settings
from app.db.session import get_db
from app.models.schemas import QueryRequest, QueryResponse
from app.services.rag_service import RagService
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient
from app.utils.llm import LLMClient
from app.utils.cache import get_cache, cache_get, cache_set
from app.utils.metrics import CACHE_HITS, CACHE_MISSES, LLM_CALLS, REQUEST_LATENCY

router = APIRouter()

emb_client   = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
vector_store = VectorStoreClient()
llm_client   = LLMClient(api_key=settings.OPENAI_API_KEY)

cache     = get_cache()
CACHE_TTL = 300

@router.post("", response_model=QueryResponse)
def query_endpoint(
    body: QueryRequest,
    db: Session = Depends(get_db),
):
    endpoint = "query"
    start = time.time()

    q = body.question.strip()
    key = f"query:{q}"

    cached = cache_get(key)
    if cached is not None:
        CACHE_HITS.labels(endpoint=endpoint).inc()
        duration = time.time() - start
        REQUEST_LATENCY.labels(endpoint=endpoint, method="POST").observe(duration)
        return cached

    CACHE_MISSES.labels(endpoint=endpoint).inc()
    LLM_CALLS.labels(endpoint=endpoint).inc()

    service = RagService(
        db_session=db,
        embedding_client=emb_client,
        vector_store=vector_store,
        llm_client=llm_client,
    )
    result = service.ask(body.question)

    cache_set(key, result, ttl=CACHE_TTL)

    duration = time.time() - start
    REQUEST_LATENCY.labels(endpoint=endpoint, method="POST").observe(duration)
    return result
