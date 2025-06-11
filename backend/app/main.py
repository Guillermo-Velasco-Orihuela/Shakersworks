from fastapi import FastAPI, Response

from app.db.session import engine, Base
from app.api.admin import router as admin_router  # Admin endpoint for index reloading
from app.api.query import router as query_router  # RAG query endpoint
from app.api.recommend import router as rec_router  # Recommendation endpoint
from app.utils.ingest import ingest_corpus         # Corpus ingestion utility
from app.utils.metrics import metrics_response      # Prometheus metrics endpoint

# ----- Startup Tasks -----
# Create database tables
Base.metadata.create_all(bind=engine)
# Ingest corpus into vector store on startup
ingest_corpus()

# Initialize FastAPI app with a descriptive title
app = FastAPI(title="Shakers RAG + Recommender")

# Mount API routers with appropriate prefixes and tags
app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(rec_router, prefix="/recommend", tags=["recommend"])
app.include_router(admin_router)  # POST /reload-index to refresh the vector index


@app.get("/metrics")
def metrics():
    """
    Expose Prometheus metrics for cache hits, misses, requests, and LLM calls.

    Returns:
        A streaming response in Prometheus text format.
    """
    data, media_type = metrics_response()
    return Response(content=data, media_type=media_type)
