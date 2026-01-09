# Krion 6D – Review Workflow & Comment Intelligence

**Contributor:** Shanttoosh V  
**Assigned by:** CTO – Kirubakaran  
**Module:** Review Workflow & AI Comment Intelligence

---

## 1. Objective (Assigned Responsibility)

| Aspect | Description |
| :--- | :--- |
| **Goal** | Design and implement a workflow-based, multi-user review comment system |
| **Key Features** | Commenting, replies, user identity tracking, workflow-step mapping |
| **AI Role** | Understand conversation context (who said what, when, and why) |
| **AI Output** | Provide professional, context-aware rephrasing for construction reviews |
| **Business Value** | Reduce conflicts, improve clarity, and standardize review communication |

---

## 2. Task Overview & Timeline (My Scope)

| Task | Timeline | Status |
| :--- | :--- | :--- |
| Review Comments Rephraser – Phase 1 | 03/01/2026 – 05/01/2026 | **Completed** |
| Review Comments System – Phase 2 | 06/01/2026 – 09/01/2026 | **Completed** |
| Append Comments & User Recognition | 07/01/2026 – 09/01/2026 | **Completed** |
| Voice Recognition (Speech to Text) | 10/01/2026 | **In Progress** |

---

## 3. Phase 1 – Review Comments Rephraser (03 Jan – 05 Jan)

### Design & Logic Implementation

| Date | Hours | Work Done |
| :--- | :--- | :--- |
| **03 Jan** | 8 hrs | Designed comment rephrasing workflow, defined status-aware behavior (submit, revise, reject), planned AI flow |
| **05 Jan** | 8 hrs | Implemented AI prompt logic, integrated OpenAI / Groq / Gemini, built abbreviation expansion (BIM, RFA, NCR), enabled multi-style outputs (formal, friendly, concise) |

### Phase 1 Outcome
*   ✅ Comment rephraser logic finalized
*   ✅ Status-aware AI rewriting completed
*   ✅ Construction-domain intelligence embedded
*   ✅ Ready for persistence and threading integration

---

## 4. Phase 2 – Architecture, Persistence & Testing (06 Jan – 09 Jan)

### Backend Architecture & Validation

| Date | Hours | Work Done |
| :--- | :--- | :--- |
| **06 Jan** | 8 hrs | Designed database schema for comments, replies, AI suggestions, feedback storage |
| **07 Jan** | 8 hrs | Defined workflow-based comment rules, parent–child thread design, finalized API contracts |
| **08 Jan** | 8 hrs | Implemented threaded comment APIs, connected comment threads to AI context |
| **09 Jan** | 8 hrs | Edge case handling, prompt refinement, multi-user testing, Swagger validation |

### Phase 2 Outcome
*   ✅ Threaded, multi-user comment system implemented
*   ✅ User identity, workflow step, and status fully integrated
*   ✅ AI understands conversation flow and participants
*   ✅ Backend and AI integration stabilized

---

## 5. Append Comments & User Recognition (07 Jan – 09 Jan)

| Day | Focus Area | Key Deliverables |
| :--- | :--- | :--- |
| **Day 1 (07 Jan)** | Design & Planning | Comment hierarchy, API contracts, AI context rules finalized |
| **Day 2 (08 Jan)** | Backend Implementation | Add, reply, fetch thread APIs implemented |
| **Day 3 (09 Jan)** | Validation & Polish | Prompt tuning, multi-user scenarios, final cleanup |

---

## 6. Voice Recognition Feature – Speech to Text (10 Jan)

### API & UI Implementation

| Date | Hours | Work Done |
| :--- | :--- | :--- |
| **10 Jan** | 2 hrs | Designed `/speech-to-text` API (audio input to text output) |
| **10 Jan** | 2 hrs | Integrated speech output with Review/RFA description generator |
| **10 Jan** | 2 hrs | Designed UI for audio upload and recording |
| **10 Jan** | 2 hrs | End-to-end testing (Audio → Text → Description) |

### Output
*   ✅ Speech-to-text API exposed
*   ✅ Voice input supported in UI
*   ✅ Generated English text auto-filled into description fields
*   ✅ Ready for further refinement and scaling

---

## 7. Current Work & Strategy

### Current Focus

| Area | Description |
| :--- | :--- |
| **UI–API Integration** | Making UI fully functional beyond Swagger |
| **AI Context** | Improving rephrasing using full thread history |
| **Workflow Accuracy** | Ensuring comments align with correct review steps |
| **Foundation** | Preparing base for audit trails, analytics, and learning datasets |

### Strategy Followed
*   Keep backend logic clean and extensible
*   Store both raw and AI-enhanced comments
*   Use conversation history instead of isolated text for AI input
*   Avoid hard-coded hierarchies and follow real workflow behavior

---

## 8. Tools & Technologies Used

### Backend

| Tool | Purpose |
| :--- | :--- |
| **FastAPI** | API framework |
| **SQLAlchemy (Async + Sync)** | ORM |
| **SQLite** | Development DB (extensible to Postgres) |
| **Pydantic** | Schema validation |

### AI

| Tool | Purpose |
| :--- | :--- |
| **Groq (LLaMA 3.1)** | AI rephrasing |
| **OpenAI** | LLM-based rewriting |
| **Gemini** | Alternative LLM |
| **Custom Prompts** | Construction-domain intelligence |

### Frontend & Dev

| Tool | Purpose |
| :--- | :--- |
| **HTML / CSS / JavaScript** | UI |
| **Swagger / OpenAPI** | API testing and validation |
| **Git & GitHub** | Version control |

---

## 9. Completed Work Summary

| Feature | Status |
| :--- | :--- |
| Review comment rephraser | **Completed** |
| Status-aware AI rewriting | **Completed** |
| Comment and reply DB schema | **Completed** |
| Threaded comment APIs | **Completed** |
| AI context integration | **Completed** |
| Swagger-tested APIs | **Completed** |
| Speech-to-text API | **In Progress** |
