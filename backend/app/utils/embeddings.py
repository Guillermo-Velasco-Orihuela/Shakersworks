# backend/app/utils/embeddings.py

from openai import OpenAI
from app.config import settings

class EmbeddingClient:
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        # instantiate the new OpenAI client
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = model

    def embed(self, text: str):
        # use the v1 Embeddings API via the client
        resp = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        # the returned structure is the same: resp.data[0].embedding
        return resp.data[0].embedding
