import os
import glob
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the backend directory to sys.path for importing app modules
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
)

from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient


# Module-level docstring
"""
CLI script to load Markdown files, chunk text into segments,
generate embeddings, and upsert records into the vector store.
"""

def load_markdown_files(path: str) -> list[dict]:
    """
    Load all '.md' files from the given directory.

    Each document is represented with its ID, title, raw text, and URL.

    Args:
        path: Filesystem path to search for Markdown files.

    Returns:
        A list of dicts containing document metadata.
    """
    files = glob.glob(os.path.join(path, "*.md"))
    docs = []
    for file in files:
        # Read the full text of each Markdown file
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        title = os.path.splitext(os.path.basename(file))[0]
        docs.append({
            "id": title,
            "text": text,
            "title": title,
            "url": f"/docs/{title}.md",
        })
    return docs


def chunk_text(text: str, max_words: int = 200) -> list[str]:
    """
    Split text into paragraph-based chunks not exceeding max_words.

    Args:
        text: Raw text to be chunked.
        max_words: Maximum number of words allowed per chunk.

    Returns:
        A list of text chunks.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for para in paragraphs:
        # Combine paragraphs until exceeding the word limit
        candidate = (current + "\n\n" + para).strip() if current else para
        if len(candidate.split()) <= max_words:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks


def main():
    """
    Entry point for the ingestion CLI.

    Steps:
      1) Load environment variables from .env.
      2) Initialize embedding and vector store clients.
      3) Load and chunk all Markdown docs.
      4) Generate embeddings and upsert records in batch.
    """
    # Load .env from the project root
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

    # Instantiate clients using environment settings
    api_key = os.getenv("OPENAI_API_KEY")
    store_url = os.getenv("VECTOR_STORE_URL")
    emb_client = EmbeddingClient(api_key=api_key)
    vector_store = VectorStoreClient(url=store_url)

    # Prepare to collect embedding records
    corpus_dir = os.path.join(os.path.dirname(__file__), "../data")
    records = []

    # Process each document: load, chunk, embed
    for doc in load_markdown_files(corpus_dir):
        for idx, chunk in enumerate(chunk_text(doc["text"])):
            embedding = emb_client.embed(chunk)
            records.append({
                "id": f"{doc['id']}_{idx}",
                "embedding": embedding,
                "metadata": {
                    "title": doc["title"],
                    "url": doc["url"],
                    "text": chunk,
                },
            })

    # Batch upsert into the vector store
    print(f"Upserting {len(records)} chunks into the vector store…")
    vector_store.upsert(records)
    print("Ingestion complete.")


if __name__ == "__main__":  # pragma: no cover
    main()
