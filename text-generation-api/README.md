# Text Generation API

A FastAPI service for generating descriptions for Review, RFA, and Issue entities based on user-provided fields.

## Features

- **Template-based generation**: Fast, predictable descriptions
- **AI-powered generation**: Natural descriptions using OpenAI/Gemini
- **Smart field detection**: Auto-includes optional fields when provided
- **Fallback mechanism**: AI falls back to template if API fails

## Quick Start

### 1. Install dependencies

```bash
cd text-generation-api
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and add your API keys if using AI mode
```

### 3. Run the server

```bash
uvicorn app.main:app --reload
```

### 4. Open API docs

Visit: http://localhost:8000/docs

## API Usage

### Generate Description

**Endpoint:** `POST /api/v1/generate-description`

**Request:**
```json
{
  "entity_type": "review",
  "generation_mode": "template",
  "fields": {
    "name": "Phase 1 Inspection",
    "start_date": "2026-01-05",
    "due_date": "2026-01-15",
    "workflow": "Approval Workflow",
    "priority": "High",
    "estimated_cost": 50000,
    "actual_cost": 45000,
    "checklist": ["Safety Check", "Quality Review"]
  }
}
```

**Response:**
```json
{
  "success": true,
  "generated_description": "The High priority review 'Phase 1 Inspection' is scheduled from Jan 05, 2026 to Jan 15, 2026, following the Approval Workflow. Estimated cost: ₹50,000, Actual cost: ₹45,000. Checklist items: Safety Check, Quality Review.",
  "generation_mode": "template",
  "editable": true
}
```

## Supported Entities

| Entity | Required Fields | Optional Fields |
|--------|-----------------|-----------------|
| Review | name, start_date, due_date, workflow, priority | parent_review, estimated_cost, actual_cost, checklist |
| RFA | name, request_date, due_date, workflow, priority | checklist |
| Issue | name, issue_type, placement, location, root_cause, start_date, due_date | workflow, estimated_cost, actual_cost |

## Generation Modes

- **template**: Fast, no API key needed, predictable output
- **ai**: Uses OpenAI/Gemini for natural language (requires API key)

## Testing

```bash
pytest tests/ -v
```
