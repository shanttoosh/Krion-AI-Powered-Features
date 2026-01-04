"""
Tests for template-based description generator.
"""
import pytest
from app.services.template_generator import template_generator


class TestTemplateGenerator:
    """Test cases for TemplateGenerator."""
    
    def test_review_basic_fields(self):
        """Test review generation with required fields only."""
        fields = {
            "name": "Phase 1 Inspection",
            "start_date": "2026-01-05",
            "due_date": "2026-01-15",
            "workflow": "Approval Workflow",
            "priority": "High"
        }
        
        result = template_generator.generate("review", fields)
        
        assert "Phase 1 Inspection" in result
        assert "High priority" in result
        assert "Approval Workflow" in result
    
    def test_review_with_optional_fields(self):
        """Test review generation with optional fields."""
        fields = {
            "name": "Quality Review",
            "start_date": "2026-01-05",
            "due_date": "2026-01-15",
            "workflow": "Standard",
            "priority": "Medium",
            "estimated_cost": 50000,
            "actual_cost": 45000,
            "checklist": ["Safety Check", "Quality Review"]
        }
        
        result = template_generator.generate("review", fields)
        
        assert "Quality Review" in result
        assert "50,000" in result
        assert "45,000" in result
        assert "Safety Check" in result
    
    def test_rfa_basic_fields(self):
        """Test RFA generation with required fields."""
        fields = {
            "name": "Safety Compliance",
            "request_date": "2026-01-10",
            "due_date": "2026-01-20",
            "workflow": "Review Process",
            "priority": "High"
        }
        
        result = template_generator.generate("rfa", fields)
        
        assert "Safety Compliance" in result
        assert "High priority" in result
        assert "Review Process" in result
    
    def test_rfa_with_checklist(self):
        """Test RFA generation with checklist."""
        fields = {
            "name": "Document Review",
            "request_date": "2026-01-10",
            "due_date": "2026-01-20",
            "workflow": "Approval",
            "priority": "Low",
            "checklist": ["Review docs", "Sign off"]
        }
        
        result = template_generator.generate("rfa", fields)
        
        assert "Review docs" in result
        assert "Sign off" in result
    
    def test_issue_basic_fields(self):
        """Test issue generation with required fields."""
        fields = {
            "name": "Window Issue",
            "issue_type": "Windows component",
            "placement": "main entrance",
            "location": "Chennai, Tamil Nadu",
            "root_cause": "large opening",
            "start_date": "2026-01-20",
            "due_date": "2026-01-28"
        }
        
        result = template_generator.generate("issue", fields)
        
        assert "Window Issue" in result
        assert "Windows component" in result
        assert "Chennai, Tamil Nadu" in result
        assert "large opening" in result
    
    def test_invalid_entity_type(self):
        """Test error handling for invalid entity type."""
        with pytest.raises(ValueError):
            template_generator.generate("invalid_type", {})
    
    def test_date_formatting(self):
        """Test date formatting works correctly."""
        fields = {
            "name": "Test Review",
            "start_date": "2026-01-05",
            "due_date": "2026-01-15",
            "workflow": "Standard",
            "priority": "Normal"
        }
        
        result = template_generator.generate("review", fields)
        
        # Should format as "Jan 05, 2026"
        assert "Jan" in result
        assert "2026" in result
