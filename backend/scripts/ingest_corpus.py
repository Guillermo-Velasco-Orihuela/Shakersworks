import os
import glob
from dotenv import load_dotenv

import sys, os
# add the parent dir (…/backend) to the import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# import your clients
from app.utils.embeddings import EmbeddingClient
from app.utils.vector_store import VectorStoreClient

def load_markdown_files(path):
    files = glob.glob(os.path.join(path, "*.md"))
    docs = []
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
        title = os.path.splitext(os.path.basename(file))[0]
        docs.append({
            "id": title,
            "text": text,
            "title": title,
            # this URL pattern matches what your API will serve
            "url": f"/docs/{title}.md"
        })
    return docs

def chunk_text(text, max_words=200):
    """
    Naive paragraph-based chunking up to ~max_words per chunk.
    """
    paragraphs = text.split("\n\n")
    chunks = []
    current = ""
    for p in paragraphs:
        # count words if we added this paragraph
        combined = (current + "\n\n" + p).strip() if current else p
        if len(combined.split()) <= max_words:
            current = combined
        else:
            if current:
                chunks.append(current)
            current = p
    if current:
        chunks.append(current)
    return chunks

def main():
    # load .env from backend/.env
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

    # instantiate clients
    emb_client   = EmbeddingClient(api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = VectorStoreClient(url=os.getenv("VECTOR_STORE_URL"))

    corpus_dir = os.path.join(os.path.dirname(__file__), "../data/corpus")
    records = []

    # load & chunk all docs
    for doc in load_markdown_files(corpus_dir):
        for idx, chunk in enumerate(chunk_text(doc["text"])):
            emb = emb_client.embed(chunk)
            records.append({
                "id": f"{doc['id']}_{idx}",
                "embedding": emb,
                "metadata": {
                    "title": doc["title"],
                    "url": doc["url"],
                    "text": chunk
                }
            })

    print(f"Upserting {len(records)} chunks into the vector store…")
    vector_store.upsert(records)
    print("Ingestion complete.")

if __name__ == "__main__":
    main()
