"""
Template-based description generator.
Generates descriptions using predefined templates with field interpolation.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class TemplateGenerator:
    """Generates descriptions using templates for each entity type."""
    
    def __init__(self):
        """Initialize with entity-specific templates."""
        self.templates = {
            "review": self._generate_review_description,
            "rfa": self._generate_rfa_description,
            "issue": self._generate_issue_description,
        }
    
    def generate(self, entity_type: str, fields: Dict[str, Any]) -> str:
        """
        Generate a description for the given entity type.
        
        Args:
            entity_type: Type of entity (review, rfa, issue)
            fields: Dictionary of field values
            
        Returns:
            Generated description string
        """
        generator_func = self.templates.get(entity_type.lower())
        if not generator_func:
            raise ValueError(f"Unsupported entity type: {entity_type}")
        
        return generator_func(fields)
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display."""
        try:
            # Try parsing ISO format
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime("%b %d, %Y")
        except (ValueError, AttributeError):
            # Return as-is if parsing fails
            return date_str
    
    def _format_cost(self, cost: Optional[float]) -> str:
        """Format cost with currency symbol."""
        if cost is None:
            return ""
        return f"₹{cost:,.0f}"
    
    def _format_checklist(self, items: Optional[List[str]]) -> str:
        """Format checklist items as comma-separated string."""
        if not items:
            return ""
        return ", ".join(items)
    
    def _generate_review_description(self, fields: Dict[str, Any]) -> str:
        """Generate description for Review entity."""
        name = fields.get("name", "Unnamed Review")
        start_date = self._format_date(fields.get("start_date", ""))
        due_date = self._format_date(fields.get("due_date", ""))
        workflow = fields.get("workflow", "Standard")
        priority = fields.get("priority", "Normal")
        
        # Build base description
        description = (
            f"The {priority} priority review '{name}' is scheduled from {start_date} "
            f"to {due_date}, following the {workflow} workflow."
        )
        
        # Add optional fields if present
        optional_parts = []
        
        # Cost information
        estimated_cost = fields.get("estimated_cost")
        actual_cost = fields.get("actual_cost")
        if estimated_cost is not None and actual_cost is not None:
            optional_parts.append(
                f"Estimated cost: {self._format_cost(estimated_cost)}, "
                f"Actual cost: {self._format_cost(actual_cost)}."
            )
        elif estimated_cost is not None:
            optional_parts.append(f"Estimated cost: {self._format_cost(estimated_cost)}.")
        elif actual_cost is not None:
            optional_parts.append(f"Actual cost: {self._format_cost(actual_cost)}.")
        
        # Parent review
        parent_review = fields.get("parent_review")
        if parent_review:
            optional_parts.append(f"This review is part of '{parent_review}'.")
        
        # Checklist
        checklist = fields.get("checklist")
        if checklist:
            checklist_str = self._format_checklist(checklist)
            optional_parts.append(f"Checklist items: {checklist_str}.")
        
        # Combine all parts
        if optional_parts:
            description += " " + " ".join(optional_parts)
        
        return description
    
    def _generate_rfa_description(self, fields: Dict[str, Any]) -> str:
        """Generate description for RFA entity."""
        name = fields.get("name", "Unnamed RFA")
        request_date = self._format_date(fields.get("request_date", ""))
        due_date = self._format_date(fields.get("due_date", ""))
        workflow = fields.get("workflow", "Standard")
        priority = fields.get("priority", "Normal")
        
        # Build base description
        description = (
            f"Request for Approval '{name}' has been initiated with a request date of "
            f"{request_date} and due date of {due_date}. This {priority} priority request "
            f"follows the {workflow} workflow and requires attention within the specified timeline."
        )
        
        # Add checklist if present
        checklist = fields.get("checklist")
        if checklist:
            checklist_str = self._format_checklist(checklist)
            description += f" Checklist items: {checklist_str}."
        
        return description
    
    def _generate_issue_description(self, fields: Dict[str, Any]) -> str:
        """Generate description for Issue entity."""
        name = fields.get("name", "Unnamed Issue")
        issue_type = fields.get("issue_type", fields.get("type", "General"))
        placement = fields.get("placement", "unspecified location")
        location = fields.get("location", "")
        root_cause = fields.get("root_cause", "unknown cause")
        start_date = self._format_date(fields.get("start_date", ""))
        due_date = self._format_date(fields.get("due_date", ""))
        
        # Build base description
        description = (
            f"The issue '{name}' concerns a {issue_type} at the {placement}"
        )
        
        if location:
            description += f" in {location}"
        
        description += f". The root cause is {root_cause}."
        
        # Add dates
        description += f" This issue is scheduled from {start_date} to {due_date}."
        
        # Add optional cost information
        optional_parts = []
        estimated_cost = fields.get("estimated_cost")
        actual_cost = fields.get("actual_cost")
        
        if estimated_cost is not None and actual_cost is not None:
            optional_parts.append(
                f"Estimated cost: {self._format_cost(estimated_cost)}, "
                f"Actual cost: {self._format_cost(actual_cost)}."
            )
        elif estimated_cost is not None:
            optional_parts.append(f"Estimated cost: {self._format_cost(estimated_cost)}.")
        elif actual_cost is not None:
            optional_parts.append(f"Actual cost: {self._format_cost(actual_cost)}.")
        
        # Add workflow if present
        workflow = fields.get("workflow")
        if workflow:
            optional_parts.append(f"Following the {workflow} workflow.")
        
        if optional_parts:
            description += " " + " ".join(optional_parts)
        
        return description


# Singleton instance
template_generator = TemplateGenerator()
