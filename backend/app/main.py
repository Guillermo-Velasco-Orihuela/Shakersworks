# backend/app/main.py

from fastapi import FastAPI
from app.db.session import engine, Base
from app.api.query import router as query_router
from app.api.recommend import router as rec_router

# import the ingestion function
from app.utils.ingest import ingest_corpus

# CREATE TABLES (dev/demo only)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Shakers RAG + Recommender")

# run ingestion at startup
@app.on_event("startup")
def on_startup():
    ingest_corpus(max_words_per_chunk=200)

app.include_router(query_router, prefix="/query", tags=["query"])
app.include_router(rec_router,  prefix="/recommend", tags=["recommend"])
