from openai import OpenAI
from app.core.config import settings


class EmbeddingClient:
    """
    Client for generating text embeddings using OpenAI's Embeddings API.

    Attributes:
        client: Initialized OpenAI client instance.
        model: Name of the embedding model to use.
    """

    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        """
        Initialize the OpenAI client and set the embedding model.

        Args:
            api_key: OpenAI API key for authentication.
            model: Identifier of the embedding model.
        """
        # Instantiate the OpenAI client with the provided API key
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> list[float]:  # pragma: no cover
        """
        Generate an embedding vector for the given text.

        Args:
            text: Input string to embed.

        Returns:
            A list of floats representing the embedding.
        """
        # Call the embeddings API endpoint
        resp = self.client.embeddings.create(
            model=self.model,
            input=text,
        )
        # Extract embedding from the response
        return resp.data[0].embedding
