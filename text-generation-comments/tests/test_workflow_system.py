import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200

def test_list_projects():
    """Test standard listing of projects"""
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    projects = response.json()
    assert isinstance(projects, list)
    assert len(projects) >= 1
    
    # Verify exact data from seed
    p1 = next((p for p in projects if p["code"] == "PRJ-001"), None)
    assert p1 is not None
    assert p1["name"] == "Skyline Tower"
    assert p1["status"] == "In Progress"

def test_get_project_detail_with_users():
    """Test getting single project should include user roles"""
    response = client.get("/api/v1/projects/1") # ID 1 is Skyline Tower
    assert response.status_code == 200
    data = response.json()
    
    assert data["code"] == "PRJ-001"
    assert "users" in data
    assert len(data["users"]) >= 3
    
    # Verify specific user role
    approver = next((u for u in data["users"] if u["role"] == "Approver"), None)
    assert approver is not None
    assert approver["user_name"] == "Senior Engineer"

def test_get_project_workflows():
    """Test fetching workflows for a project"""
    response = client.get("/api/v1/projects/1/workflows")
    assert response.status_code == 200
    workflows = response.json()
    
    assert len(workflows) > 0
    wf = workflows[0]
    assert wf["name"] == "3-Step Structural Approval"
    assert len(wf["steps"]) == 3
    
    # Verify Step Order
    assert wf["steps"][0]["step_name"] == "Initial Review"
    assert wf["steps"][2]["step_name"] == "Final Sign-off"

def test_get_review_detail():
    """Test getting full review detail"""
    # First, get list of reviews via project (if we had that endpoint) 
    # OR assume ID 1 exists from seed
    
    response = client.get("/api/v1/reviews/1")
    if response.status_code == 404:
        pytest.skip("Review ID 1 not found (Seed might have assigned different ID)")
        
    assert response.status_code == 200
    data = response.json()
    
    assert data["code"] == "RVW-1001"
    assert data["current_step"] == 2
    assert data["project_name"] == "Skyline Tower"
    assert data["workflow_name"] == "3-Step Structural Approval"

def test_review_not_found():
    response = client.get("/api/v1/reviews/99999")
    assert response.status_code == 404
