from fastapi.testclient import TestClient
import sys, os

# ensure the backend/ folder is on sys.path so we can import our app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_query_invite_collaborators():
    # Use a question to hit the collaborators doc (may return empty if no exact match)
    question = (
        "What types of roles and permissions are there when inviting collaborators?"
    )
    resp = client.post("/query", json={"question": question})
    assert resp.status_code == 200, resp.text

    data = resp.json()
    # must return an answer string
    assert "answer" in data and isinstance(data["answer"], str)

    # must return source_docs as a list (can be empty)
    assert "source_docs" in data and isinstance(data["source_docs"], list)
    
    # if there are any source_docs, they should have a title
    for doc in data["source_docs"]:
        assert "title" in doc and isinstance(doc["title"], str)
        assert "url" in doc and isinstance(doc["url"], str)
        assert "text" in doc and isinstance(doc["text"], str)