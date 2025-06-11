# backend/tests/test_query.py

import pytest
import sys
import os
from fastapi.testclient import TestClient

# Add the project root directory to the Python path
# This allows us to import the 'backend' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.app.main import app


client = TestClient(app)

def test_query_returns_answer_and_sources(monkeypatch):
    # Stub RagService.ask to return a known result
    # We import it here to ensure the path is already set
    from backend.app.services.rag_service import RagService
    def fake_ask(self, question):
        return {
            "answer": "Stubbed answer",
            "source_docs": [
                {"title": "intro", "url": "/docs/intro.md"}
            ]
        }
    monkeypatch.setattr(RagService, "ask", fake_ask)

    response = client.post(
        "/query",
        json={"question": "What is Shakers?"}
    )
    
    # Optional: print the response content for debugging
    print("\n" + "="*50)
    print("Response Content:")
    print(response.json())
    print("="*50 + "\n")
    
    
    assert response.status_code == 200 
    data = response.json()
    assert "answer" in data and data["answer"] == "Stubbed answer"
    assert "source_docs" in data and isinstance(data["source_docs"], list)
    assert data["source_docs"][0]["title"] == "intro"

def test_query_out_of_scope(monkeypatch):
    # Stub RagService.ask to simulate out-of-scope
    from backend.app.services.rag_service import RagService
    def fake_ask(self, question):
        return {"answer": "I’m sorry, I don’t have information on that topic.", "source_docs": []}
    monkeypatch.setattr(RagService, "ask", fake_ask)

    response = client.post("/query", json={"question": "What is the speed of light?"})
    assert response.status_code == 200
    data = response.json()
    assert data["answer"].startswith("I’m sorry")
    assert data["source_docs"] == []