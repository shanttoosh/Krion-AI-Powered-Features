# 🛠️ Technical Deep Dive: Krion AI Architecture

This document traces the exact execution flow of the two AI services, referencing specific files, classes, and methods.

---

## 🏗️ 1. Comment Rephraser (`text-generation-comments`)

### **The Stack**
*   **Router**: `app/routers/rephrase.py`
*   **Service**: `app/services/comment_rephraser.py` (Class: `CommentRephraser`)
*   **Data Models**: `app/models/rephrase_schemas.py`
*   **Knowledge Base**: `app/services/construction_terms.py`

### **Execution Trace**

#### **Step 1: Frontend Request**
*   **File**: `frontend/script.js` -> `triggerRephrase()`
*   The user clicks the wand. JS constructs a JSON payload:
    ```json
    { "input": "iim colum bad", "status": "reject", "num_suggestions": 3 }
    ```
*   Sends `POST` request to `http://localhost:8002/api/v1/rephrase-comment`.

#### **Step 2: API & Validation**
*   **File**: `app/routers/rephrase.py` -> `rephrase_comment()`
*   FastAPI validates the body against `CommentRephraseRequest` (Pydantic model).
*   Calls the singleton service: `comment_rephraser.rephrase(request)`.

#### **Step 3: Service Orchestration**
*   **File**: `app/services/comment_rephraser.py` -> `rephrase()`
*   **Phase A: Typos & Expansions**
    *   Calls `construction_terms.expand_abbreviations("iim colum bad")`.
    *   **Logic**: Iterates words. Checks `TYPO_MAPPINGS`.
    *   **Result**: "iim" -> "BIM", "colum" -> "column". Returns "BIM column bad".
*   **Phase B: RAG Search (Retrieval)**
    *   Calls `construction_terms.find_relevant_glossary_terms("iim colum")`.
    *   **Logic**: Uses `difflib.get_close_matches` against `GLOSSARY_CACHE` (loaded from `construction-terms.txt`).
    *   **Result**: Finds definitions for "Building Information Model" and "Column".

#### **Step 4: Prompt Engineering**
*   **File**: `app/services/comment_rephraser.py` -> `_build_prompt()`
*   Constructs a massive string prompt containing:
    1.  **Role**: "Professional comment writer for Krion 6D".
    2.  **Context**: The Definitions found in Phase B ("RELEVANT GLOSSARY TERMS").
    3.  **Strict Rules**: "CORRECT TYPOS AGGRESSIVELY".
    4.  **Few-Shot Examples**: `Input: "wall paint bd" -> Output: "The wall paint finish is unsatisfactory."`
    5.  **Output Format**: Forces `[FORMAL]`, `[FRIENDLY]`, `[CONCISE]` labels.

#### **Step 5: AI Generation & Parsing**
*   **File**: `app/services/comment_rephraser.py` -> `_generate_with_ai()`
*   Sends prompt to OpenAI/Groq/Gemini.
*   **Response**: Raw text with `[FORMAL] ... [CONCISE] ...` structure.
*   **Parsing**: `_parse_suggestions()` splits the text by these tags into a structured list.

---

## 📝 2. Description Generator (`text-generation-api`)

### **The Stack**
*   **Service**: `app/services/generator.py` (Class: `DescriptionGenerator`)
*   **Template Engine**: `app/services/template_generator.py`
*   **AI Engine**: `app/services/ai_generator.py`

### **Execution Trace**

#### **Step 1: The Request**
*   Endpoint: `POST /api/v1/generate-description`
*   Payload: `{"entity_type": "review", "subject": "Concrete Pour", "workflow": "QA/QC"}`

#### **Step 2: Strategy Pattern (The "Smart Switch")**
*   **File**: `app/services/generator.py` -> `generate()`
*   **Check 1**: calls `self.template_gen.generate()`.
    *   Scans `templates/entity_templates.json`.
    *   If a strictly matching template exists (e.g., `review.concrete_pour`), it fills fields using Jinja2.
    *   **Return**: Instant result.
*   **Check 2**: If template returns `None`, calls `self.ai_gen.generate()`.

#### **Step 3: AI Fallback**
*   **File**: `app/services/ai_generator.py`
*   Builds a dynamic prompt: *"Generate a description for a 'Concrete Pour' in the 'QA/QC' workflow..."*
*   Calls LLM and returns the generated text.

---

## 🔑 Key Differences
| Feature | Comment Rephraser (Port 8002) | Description Generator (Port 8000) |
| :--- | :--- | :--- |
| **Primary Goal** | Polish existing text | Create new text from scratch |
| **Architecture** | RAG (Glossary-based) | Hybrid (Templates + AI) |
| **Logic** | Fuzzy Matching + Typos | Jinja2 Templates |
| **Output** | 3 Distinct Variations | 1 Best Description |
