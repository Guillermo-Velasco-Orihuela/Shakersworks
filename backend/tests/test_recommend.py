from fastapi.testclient import TestClient
import sys, os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app

client = TestClient(app)

def test_recommend_for_new_user():
    user_id = "pytest_user_1"
    # include context if required by the API (optional)
    payload = {"user_id": user_id, "context": ""}

    resp = client.post("/recommend", json=payload)
    assert resp.status_code == 200, resp.text

    recs = resp.json()
    # endpoint may return the list directly or wrap it in {"recommendations": [...]}
    if isinstance(recs, dict) and "recommendations" in recs:
        rec_list = recs["recommendations"]
    else:
        rec_list = recs

    # must return a list (can be empty)
    assert isinstance(rec_list, list), f"Expected list, got: {recs}"

    # if there are any recommendations, they must have the correct shape
    for r in rec_list:
        assert isinstance(r, dict), f"Bad rec shape: {r}"
        assert "title" in r and isinstance(r["title"], str), f"Missing title in {r}"
        assert \
            "explanation" in r and isinstance(r["explanation"], str), \
            f"Missing explanation in {r}"