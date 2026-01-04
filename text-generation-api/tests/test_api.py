"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestGenerationAPI:
    """Test cases for the generation API."""
    
    def test_health_check(self):
        """Test health check endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "Text Generation API" in response.json()["service"]
    
    def test_generate_review_template(self):
        """Test review generation with template mode."""
        request_data = {
            "entity_type": "review",
            "generation_mode": "template",
            "fields": {
                "name": "Phase 1 Inspection",
                "start_date": "2026-01-05",
                "due_date": "2026-01-15",
                "workflow": "Approval Workflow",
                "priority": "High"
            }
        }
        
        response = client.post("/api/v1/generate-description", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Phase 1 Inspection" in data["generated_description"]
        assert data["editable"] is True
        assert data["generation_mode"] == "template"
    
    def test_generate_rfa_template(self):
        """Test RFA generation with template mode."""
        request_data = {
            "entity_type": "rfa",
            "generation_mode": "template",
            "fields": {
                "name": "Safety Compliance",
                "request_date": "2026-01-10",
                "due_date": "2026-01-20",
                "workflow": "Review Process",
                "priority": "Medium"
            }
        }
        
        response = client.post("/api/v1/generate-description", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Safety Compliance" in data["generated_description"]
    
    def test_generate_issue_template(self):
        """Test issue generation with template mode."""
        request_data = {
            "entity_type": "issue",
            "generation_mode": "template",
            "fields": {
                "name": "Window Problem",
                "issue_type": "Windows component",
                "placement": "main entrance",
                "location": "Chennai",
                "root_cause": "large opening",
                "start_date": "2026-01-20",
                "due_date": "2026-01-28"
            }
        }
        
        response = client.post("/api/v1/generate-description", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Window Problem" in data["generated_description"]
    
    def test_generate_with_optional_fields(self):
        """Test generation with optional fields included."""
        request_data = {
            "entity_type": "review",
            "generation_mode": "template",
            "fields": {
                "name": "Full Review",
                "start_date": "2026-01-05",
                "due_date": "2026-01-15",
                "workflow": "Standard",
                "priority": "High",
                "estimated_cost": 100000,
                "actual_cost": 95000,
                "checklist": ["Item 1", "Item 2"]
            }
        }
        
        response = client.post("/api/v1/generate-description", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "100,000" in data["generated_description"]
        assert "Item 1" in data["generated_description"]
    
    def test_missing_required_fields(self):
        """Test error handling for missing fields."""
        request_data = {
            "entity_type": "review",
            "generation_mode": "template",
            "fields": {}  # Empty fields
        }
        
        response = client.post("/api/v1/generate-description", json=request_data)
        
        # Should still return 200 with default values
        assert response.status_code == 200
