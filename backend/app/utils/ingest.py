# backend/app/utils/ingest.py

from pathlib import Path
from app.config import settings
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient

def ingest_corpus(max_words_per_chunk: int = 200):
    """
    Load all .md files under backend/data/, chunk them,
    embed each chunk, and upsert into the 'shakers' Chroma collection.
    """
    emb_client   = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
    vector_store = VectorStoreClient(url=settings.VECTOR_STORE_URL)

    base_dir   = Path(__file__).resolve().parents[2]
    corpus_dir = base_dir / "data"
    if not corpus_dir.exists():
        return

    records = []
    for md_file in corpus_dir.glob("*.md"):
        text   = md_file.read_text(encoding="utf-8")
        doc_id = md_file.stem
        url    = f"/docs/{doc_id}.md"

        # simple paragraph-based chunking
        paragraphs = text.split("\n\n")
        current = ""
        chunks  = []
        for p in paragraphs:
            combined = (current + "\n\n" + p).strip() if current else p
            if len(combined.split()) <= max_words_per_chunk:
                current = combined
            else:
                if current:
                    chunks.append(current)
                current = p
        if current:
            chunks.append(current)

        # embed & collect records
        for idx, chunk in enumerate(chunks):
            emb = emb_client.embed(chunk)
            records.append({
                "id":        f"{doc_id}_{idx}",
                "embedding": emb,
                "metadata": {
                    "title": doc_id,
                    "url":   url,
                    "text":  chunk,
                },
            })

    if records:
        print(f"▶ Ingesting {len(records)} chunks into vector store…")
        vector_store.upsert(records)
        print("▶ Ingestion complete.")

# Allow running this file directly:
if __name__ == "__main__":
    ingest_corpus()
