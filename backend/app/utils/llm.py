from openai import OpenAI


class LLMClient:
    """
    Client for interacting with an LLM via OpenAI's Chat Completions API.

    Attributes:
        client: Initialized OpenAI client instance.
        model: Identifier of the chat model to use.
    """

    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the OpenAI client and set the chat model.

        Args:
            api_key: OpenAI API key for authentication.
            model: Identifier of the chat model (e.g., "gpt-4").
        """
        # Instantiate the OpenAI client with the provided API key
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.0,
    ) -> str:
        """
        Send a prompt to the LLM and return the generated response.

        Args:
            prompt: The text prompt to send to the model.
            max_tokens: Maximum number of tokens in the generated completion.
            temperature: Sampling temperature for response randomness.

        Returns:
            The assistant's reply as a string.
        """
        # Call the chat completions endpoint with a single user message
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # Extract and return the assistant's reply content
        return resp.choices[0].message.content
