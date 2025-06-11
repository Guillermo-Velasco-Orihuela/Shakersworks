from pathlib import Path
from app.core.config import settings
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient


def ingest_corpus(max_words_per_chunk: int = 200):
    """
    Load all Markdown files under 'data/', chunk them into text segments,
    generate embeddings for each chunk, and upsert them into the vector store.

    Args:
        max_words_per_chunk: Maximum number of words per chunk when splitting text.
    """
    # Initialize clients for embeddings and vector store operations
    emb_client = EmbeddingClient(api_key=settings.OPENAI_API_KEY)
    vector_store = VectorStoreClient(url=settings.VECTOR_STORE_URL)

    # Locate the corpus directory (project root /data)
    base_dir = Path(__file__).resolve().parents[2]
    corpus_dir = base_dir / "data"

    if not corpus_dir.exists():
        # Nothing to ingest if the data directory is missing
        return

    records = []
    # Iterate over each Markdown file in the corpus directory
    for md_file in corpus_dir.glob("*.md"):
        text = md_file.read_text(encoding="utf-8")
        doc_id = md_file.stem
        url = f"/docs/{doc_id}.md"

        # Split text into paragraphs, then build chunks based on word count
        paragraphs = text.split("\n\n")
        chunks = []
        current = ""
        for para in paragraphs:
            candidate = (current + "\n\n" + para).strip() if current else para
            if len(candidate.split()) <= max_words_per_chunk:
                current = candidate
            else:
                if current:
                    chunks.append(current)
                current = para
        if current:
            chunks.append(current)

        # Create embedding records for each chunk
        for idx, chunk in enumerate(chunks):
            emb = emb_client.embed(chunk)
            records.append({
                "id": f"{doc_id}_{idx}",
                "embedding": emb,
                "metadata": {
                    "title": doc_id,
                    "url": url,
                    "text": chunk,
                },
            })

    if records:
        print(f"▶ Ingesting {len(records)} chunks into vector store…")
        vector_store.upsert(records)
        print("▶ Ingestion complete.")


if __name__ == "__main__":  # pragma: no cover
    # Allow running this module directly for ingestion
    ingest_corpus()
