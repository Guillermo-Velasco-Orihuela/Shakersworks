# backend/app/utils/llm.py

from openai import OpenAI

class LLMClient:
    def __init__(self, api_key: str, model: str = "gpt-4"):
        # new client instantiation
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.0):
        # use the Chat Completions endpoint on the client
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # extract the assistant’s reply
        return resp.choices[0].message.content
