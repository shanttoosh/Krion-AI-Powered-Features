# Krion AI-Powered Features

This repository contains two independent microservices designed to enhance the Krion 6D construction project management platform with AI capabilities.

---

## 🏗️ Architecture Overview

The project is structured as a mono-repo containing two distinct FastAPI microservices:

1.  **`text-generation-api`** (Port 8000): Handles automated description generation for construction entities (RFIs, Reviews).
2.  **`text-generation-comments`** (Port 8002): Provides "Quillbot-style" comment rephrasing and expansion with specific domain knowledge.

---

## 1. Comment Rephraser Service
**Folder:** `/text-generation-comments`  
**Port:** `8002`

A specialized service that helps engineers write professional, tone-appropriate review comments. It inputs short, messy text and outputs polished, formal alternatives.

### 🛠️ Tech Stack
*   **Backend:** Python, FastAPI, Uvicorn
*   **AI Logic:** OpenAI / Groq / Google Gemini
*   **Domain Knowledge:** Custom "RAG-lite" (Retrieval Augmented Generation) using fuzzy matching on a construction glossary.
*   **Frontend:** HTML5, CSS3 (Krion Styles), Vanilla JavaScript.

### ✨ Key Features
*   **Manual Magic Wand:** Users type freely and click the ✨ icon to polish text instantly.
*   **3-Style Output:** Always generates **[FORMAL]**, **[FRIENDLY]**, and **[CONCISE]** variations.
*   **Domain Accuracy:**
    *   Auto-corrects typos: *'iim'* → *'BIM'*, *'colum'* → *'Column'*.
    *   Expands abbreviations: *'rebar'* → *'Reinforcement bar'*.
*   **Glossary Integration:** Dynamically loads terms from `construction-terms.txt`.

### 🔄 Workflow
1.  **User Input:** Engineer types "rebar spacing wrong" into the frontend.
2.  **Glossary Lookup:** Backend fuzzy-matches terms (finds "Reinforcement Bar").
3.  **Prompt Engineering:** Constructs a strict prompt with the context "Status: REJECT" and injected glossary terms.
4.  **AI Generation:** LLM generates 3 professional versions.
5.  **Response:** Frontend displays options; user clicks to replace their text.

---

## 2. Description Generator Service
**Folder:** `/text-generation-api`  
**Port:** `8000`

A service for generating full, context-aware descriptions for construction entities based on structured JSON data.

### 🛠️ Tech Stack
*   **Backend:** Python, FastAPI
*   **Templating:** Jinja2 (for structured text generation)
*   **AI Logic:** Hybrid approach (Template-based fallback + AI generation)

### 🔄 Workflow
1.  **Data Input:** System sends a JSON object (e.g., `{"rfa_id": "123", "subject": "Concrete Pour"}`).
2.  **Template Matching:** specific templates are checked first for speed and consistency.
3.  **AI Fallback:** If no template matches, the AI generates a detailed description based on the fields.

---

## 🚀 How to Run

### Prerequisites
*   Python 3.10+
*   `pip`
*   `.env` files configured in both directories with API keys (`OPENAI_API_KEY`, etc.)

### Running Comment Rephraser (Recommended)
```powershell
cd text-generation-comments
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8002 --reload
```
> Access UI at: **http://localhost:8002**

### Running Description Generator
```powershell
cd text-generation-api
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000 --reload
```
