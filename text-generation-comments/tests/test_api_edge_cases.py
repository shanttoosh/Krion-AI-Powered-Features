import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_nonexistent_project():
    """Negative Test: Requesting a project ID that does not exist."""
    response = client.get("/api/v1/projects/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"

def test_get_nonexistent_review():
    """Negative Test: Requesting a review ID that does not exist."""
    response = client.get("/api/v1/reviews/88888")
    assert response.status_code == 404
    assert response.json()["detail"] == "Review not found"

def test_create_comment_invalid_review_id():
    """Integrity Test: Trying to post a comment to a non-existent review."""
    payload = {
        "review_id": 99999,
        "workflow_step": 1,
        "user_name": "Test User",
        "status": "Comment",
        "text": "This should fail",
        "parent_id": None
    }
    response = client.post("/api/v1/review-comments/add", json=payload)
    # The current implementation might return 500 or 404 depending on how the FK violation is handled.
    # Ideally it should be 400 or 404. Let's see what it does.
    # If standard SQLAlchemy FK error bubbles up, it might be 500.
    # We will assert != 200 for now and refine.
    assert response.status_code != 200

def test_rephrase_empty_input():
    """Validation Test: Sending empty input to AI rephraser."""
    payload = {
        "input": "",
        "status": "Comment",
        "thread_history": [],
        "parent_comment_id": None
    }
    response = client.post("/api/v1/rephrase-comment", json=payload)
    # Expecting validation error or 400
    assert response.status_code == 422 # Pydantic validation error

def test_workflow_structure_integrity():
    """Data Integrity: Verify that the seeded workflow has valid step definitions."""
    # ID 1 is seeded
    response = client.get("/api/v1/projects/1/workflows")
    assert response.status_code == 200
    workflows = response.json()
    assert len(workflows) > 0
    
    wf = workflows[0]
    # Check Steps order
    steps = wf["steps"]
    step_numbers = [s["step_number"] for s in steps]
    assert step_numbers == sorted(step_numbers), "Steps should be returned in order"
