from app.core.config import settings


class RagService:
    """
    Retrieval-Augmented Generation (RAG) service that handles question
    embedding, document retrieval, and LLM invocation to answer queries.
    """

    def __init__(
        self, db_session, embedding_client, vector_store, llm_client
    ):
        # Initialize dependencies and threshold for out-of-scope checks
        self.db = db_session
        self.embedding_client = embedding_client
        self.vector_store = vector_store
        self.llm_client = llm_client
        self.max_distance_threshold = getattr(
            settings, "RAG_MAX_DISTANCE", 0.75
        )

    def ask(self, question: str) -> dict:
        """
        Process a question by embedding it, retrieving documents,
        performing scope checks, and generating an answer with citations.

        Returns a dict with 'answer' and 'source_docs' list.
        """
        # 1) Embed the question
        q_emb = self.embedding_client.embed(question)

        # 2) Retrieve top matching documents
        docs = self.vector_store.query(q_emb, top_k=5)

        # 3) Out-of-scope check based on distance score
        if not docs or docs[0]["score"] > self.max_distance_threshold:
            return {
                "answer": "I’m sorry, I don’t have information on that topic.",
                "source_docs": [],
            }

        # 4) Build prompt including document citations
        prompt = self._build_prompt(question, docs)

        # 5) Call the LLM with the constructed prompt
        answer = self.llm_client.generate(prompt)

        # 6) Prepare results for API response
        source_docs = [
            {"title": d["title"], "url": d.get("url", "")} for d in docs
        ]
        return {"answer": answer, "source_docs": source_docs}

    def _build_prompt(self, question: str, docs: list) -> str:
        """
        Construct a prompt by concatenating document texts and the question,
        numbering each document for citation in the answer.
        """
        prompt = (
            "Use the following documents to answer the question. "
            "Cite each document number.\n\n"
        )
        for i, doc in enumerate(docs, start=1):
            prompt += f"[Doc {i}] {doc['text']}\n\n"

        prompt += f"Question: {question}\nAnswer with citations like [Doc 1], [Doc 2], etc."
        return prompt
