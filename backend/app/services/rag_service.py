# backend/app/services/rag_service.py

from app.config import settings

class RagService:
    def __init__(self, db_session, embedding_client, vector_store, llm_client):
        self.db             = db_session
        self.embedding_client = embedding_client
        self.vector_store     = vector_store
        self.llm_client       = llm_client
        # maximum distance (dissimilarity) before we consider it out-of-scope
        # you can tune this value in settings if you expose it there
        self.max_distance_threshold = getattr(settings, "RAG_MAX_DISTANCE", 0.75)

    def ask(self, question: str):
        # 1) Embed the question
        q_emb = self.embedding_client.embed(question)

        # 2) Retrieve top documents
        docs = self.vector_store.query(q_emb, top_k=5)

        # 3) Out-of-scope check
        if not docs or docs[0]["score"] > self.max_distance_threshold:
            return {
                "answer": "I’m sorry, I don’t have information on that topic.",
                "source_docs": []
            }

        # 4) Build a prompt including citations
        prompt = self._build_prompt(question, docs)

        # 5) Call the LLM
        answer = self.llm_client.generate(prompt)

        # 6) Format for API
        source_docs = [{"title": d["title"], "url": d.get("url", "")} for d in docs]
        return {"answer": answer, "source_docs": source_docs}

    def _build_prompt(self, question: str, docs: list):
        prompt = "Use the following documents to answer the question. Cite each document number.\n\n"
        for i, doc in enumerate(docs, 1):
            prompt += f"[Doc {i}] {doc['text']}\n\n"
        prompt += f"Question: {question}\nAnswer with citations like [Doc 1], [Doc 2], etc."
        return prompt
