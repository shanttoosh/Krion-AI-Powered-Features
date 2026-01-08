"""
Comment rephraser service.
Provides Quillbot-style text expansion and rephrasing for review comments.
"""
from app.comments_db.models import CommentRequestDB, CommentSuggestionDB
from app.comments_db.session import AsyncSessionLocal
from typing import List, Tuple
import asyncio
from app.config import settings
from app.models.rephrase_schemas import (
    CommentRephraseRequest,
    CommentRephraseResponse,
    CommentSuggestion,
    CorrectionsInfo,
    ReviewStatus,
)
from app.services.construction_terms import (
    expand_abbreviations,
    get_tone_context,
    detect_issue_category,
    find_relevant_glossary_terms,
    TERM_EXPANSIONS,
)


class CommentRephraser:
    """
    Rephrases short comments into professional, grammatically correct sentences.
    Supports multiple AI providers (Groq, OpenAI, Gemini).
    """
    
    def __init__(self):
        """Initialize AI clients."""
        self.openai_client = None
        self.groq_client = None
        self.gemini_model = None
        self._initialized = False
    
    def _initialize_clients(self):
        """Initialize AI provider clients (lazy initialization)."""
        if self._initialized:
            return
        
        self._initialized = True
        
        if settings.ai_provider == "openai" and settings.openai_api_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=settings.openai_api_key)
                print("✅ Comment Rephraser: OpenAI client initialized")
            except Exception as e:
                print(f"❌ Comment Rephraser: Failed to initialize OpenAI: {e}")
        
        elif settings.ai_provider == "groq" and settings.groq_api_key:
            try:
                from openai import OpenAI
                self.groq_client = OpenAI(
                    api_key=settings.groq_api_key,
                    base_url="https://api.groq.com/openai/v1"
                )
                print("✅ Comment Rephraser: Groq client initialized")
            except Exception as e:
                print(f"❌ Comment Rephraser: Failed to initialize Groq: {e}")
        
        elif settings.ai_provider == "gemini" and settings.gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                print("✅ Comment Rephraser: Gemini client initialized")
            except Exception as e:
                print(f"❌ Comment Rephraser: Failed to initialize Gemini: {e}")
    
    def _detect_input_type(self, text: str) -> str:
        """
        Detect what type of processing the input needs.
        
        Returns:
            - "expand": Short input (2-5 words) needs expansion
            - "correct": Input has errors, needs correction
            - "polish": Input is good, just needs minor polishing
        """
        words = text.strip().split()
        word_count = len(words)
        
        if word_count <= 5:
            return "expand"
        elif word_count <= 15:
            return "correct"
        else:
            return "polish"
    
    def _build_prompt(
        self, 
        input_text: str, 
        status: ReviewStatus, 
        expanded_text: str,
        context: dict = None,
        glossary_terms: str = "",
        thread_history: list = None  # NEW: Previous comments in thread
    ) -> str:
        """Build the AI prompt for comment rephrasing."""
        
        tone_context = get_tone_context(status.value)
        issue_category = detect_issue_category(input_text)
        
        # Build context string
        context_str = ""
        if context:
            if context.get("workflow_name"):
                context_str += f"Workflow: {context['workflow_name']}\n"
            if context.get("step_name"):
                context_str += f"Review Step: {context['step_name']}\n"
            if context.get("entity_type"):
                context_str += f"Document Type: {context['entity_type']}\n"
        
        # NEW: Build thread history context for replies
        thread_context = ""
        if thread_history and len(thread_history) > 0:
            thread_context = "\n--- CONVERSATION THREAD (for context) ---\n"
            for i, comment in enumerate(thread_history, 1):
                user = comment.get("user_name", "Unknown")
                status_val = comment.get("status", "").upper()
                text = comment.get("text", "")
                thread_context += f"{i}. [{status_val}] {user}: \"{text}\"\n"
            thread_context += "--- END THREAD ---\n\nYou are writing a REPLY to the above conversation.\n"
        
        # Status-specific instructions
        status_instructions = {
            ReviewStatus.SUBMIT: """
- Use positive, confirming language
- Indicate approval or acceptance
- Keep it concise and professional""",
            ReviewStatus.REJECT: """
- Clearly state the rejection and reason
- Be firm but professional
- Provide actionable feedback
- End with a request to revise and resubmit""",
            ReviewStatus.REVISE: """
- Use constructive, helpful language
- Focus on what needs to be changed
- Be specific about required revisions
- Encourage resubmission after corrections"""
        }
        
        prompt = f"""You are a professional comment writer for Krion 6D, a construction project management system.

TASK: Write a professional REPLY to the conversation below, based on the USER INPUT.
{thread_context}
USER INPUT (Draft): "{input_text}"
EXPANDED TERMS: "{expanded_text}"
STATUS: {status.value.upper()}
ISSUE CATEGORY: {issue_category}
{f"CONTEXT:{chr(10)}{context_str}" if context_str else ""}
{f"RELEVANT GLOSSARY TERMS:{chr(10)}{glossary_terms}" if glossary_terms else ""}

CRITICAL DOMAIN RULES:
1. STRICTLY CONSTRUCTION DOMAIN ONLY.
2. The USER INPUT is the core message you must rephrase. The THREAD is just for context.
3. If USER INPUT is "noted" or "ok", use the context to say WHAT is noted (e.g. "Noted, the column width will be fixed.")
4. CORRECT TYPOS AGGRESSIVELY using the Glossary.
   - 'iim', 'im' -> BIM (Building Information Model)
   - 'colum', 'clm', 'col' -> Column
   - 'rebar' -> Reinforcement Bar
5. Interpreting messy inputs:
   - "iim colum bad" -> "The BIM column model is incorrect."
   - "rfa rnf wrong" -> "Request for Approval for reinforcement details contains errors."
   - (Reply) "ok done" -> "The requested changes have been implemented."
{f"6. Reference specific details from the thread (like dimensions or grid lines) if the user agrees to them." if thread_history else ""}

FEW-SHOT EXAMPLES:
Input: "wall paint bd" -> Output: "The wall paint finish is unsatisfactory."
Input: "iim colum wrong" -> Output: "The BIM column model contains errors."
Input: "site cleared ok" -> Output: "Site clearance has been verified and is acceptable."
Input: "rfa for rnf" -> Output: "Request for Approval regarding reinforcement details."
{f'Input (reply): "noted will fix" -> Output: "Acknowledged. The corrections will be made as per the feedback and resubmitted."' if thread_history else ""}

TONE REQUIREMENTS:
- The content must reflect the STATUS ({status.value.upper()}) but providing 3 distinct phrasing styles.
{status_instructions[status]}

OUTPUT FORMAT:
Generate exactly 3 alternatives, each on a new line, with these specific style labels:
[FORMAL] <Professional, corporate, standard construction language>
[FRIENDLY] <Polite, constructive, softer tone>
[CONCISE] <Direct, short, punchy (good for mobile)>

Rules:
- Fix any spelling or grammar errors
- Expand abbreviations naturally
- Each suggestion should be 1-2 sentences
- Do not include asterisks, bullet points, or special formatting
- Output ONLY the 3 labeled suggestions, nothing else"""

        return prompt
    
    async def rephrase(self, request: CommentRephraseRequest) -> CommentRephraseResponse:
        """
        Main method to rephrase a comment.
        
        Args:
            request: The rephrase request with input text and status
            
        Returns:
            CommentRephraseResponse with suggestions and corrections info
        """
        # Lazy initialization
        self._initialize_clients()
        
        try:
            # Detect input type
            input_type = self._detect_input_type(request.input)
            
            # Expand abbreviations
            expanded_text, expansions = expand_abbreviations(request.input)
            
            # Get context dict
            context = request.context.model_dump() if request.context else None
            
            # Get relevant glossary terms
            glossary_matches = find_relevant_glossary_terms(request.input)
            
            # Build prompt with thread history for context-aware replies
            prompt = self._build_prompt(
                request.input, 
                request.status, 
                expanded_text,
                context,
                glossary_matches,
                request.thread_history  # Pass thread history for context
            )
            
            # Generate suggestions using AI
            raw_response = await self._generate_with_ai(prompt)
            
            # Parse suggestions from response
            suggestions = self._parse_suggestions(raw_response)

            async with AsyncSessionLocal() as db:
               request_row = CommentRequestDB(
                    input_text=request.input,
                    status=request.status.value,
                    input_type=input_type
                )
            db.add(request_row)
            await db.flush()

            for s in suggestions:
                db.add(
                    CommentSuggestionDB(
                        request_id=request_row.id,
                        text=s.text,
                        style=s.style,
                        confidence=s.confidence,
                        provider=settings.ai_provider
                    )
                )          

            await db.commit()
            
            # Build corrections info
            corrections = CorrectionsInfo(
                spelling_corrections=0,  # AI handles this automatically
                grammar_corrections=0,
                terms_expanded=expansions
            )
            
            return CommentRephraseResponse(
                success=True,
                suggestions=suggestions,
                corrections=corrections,
                original_input=request.input,
                input_type=input_type
            )
            
        except Exception as e:
            print(f"❌ Comment rephrasing failed: {e}")
            # Return fallback response
            return CommentRephraseResponse(
                success=False,
                suggestions=[],
                corrections=CorrectionsInfo(),
                original_input=request.input,
                input_type="expand",
                error=str(e)
            )
    
    async def _generate_with_ai(self, prompt: str) -> str:
        """Generate response using configured AI provider."""
        
        if settings.ai_provider == "openai" and self.openai_client:
            return await self._generate_openai(prompt)
        elif settings.ai_provider == "groq" and self.groq_client:
            return await self._generate_groq(prompt)
        elif settings.ai_provider == "gemini" and self.gemini_model:
            return await self._generate_gemini(prompt)
        else:
            raise ValueError("No AI provider configured")
    
    async def _generate_openai(self, prompt: str) -> str:
        """Generate using OpenAI API."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional technical writer for construction projects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
        )
        return response.choices[0].message.content.strip()
    
    async def _generate_groq(self, prompt: str) -> str:
        """Generate using Groq API (OpenAI-compatible)."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a professional technical writer for construction projects."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
        )
        return response.choices[0].message.content.strip()
    
    async def _generate_gemini(self, prompt: str) -> str:
        """Generate using Google Gemini API."""
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self.gemini_model.generate_content(prompt)
        )
        return response.text.strip()
    
    def _parse_suggestions(self, raw_response: str) -> List[CommentSuggestion]:
        """Parse the AI response into structured suggestions using regex."""
        import re
        suggestions = []
        
        # Regex to find style tags like [FORMAL], [FRIENDLY], etc.
        # Captures the tag and the text following it until the next tag or end of string
        pattern = r'(\[(?:FORMAL|CONCISE|FRIENDLY)\])(.*?)(?=\[(?:FORMAL|CONCISE|FRIENDLY)\]|$)'
        
        # Find all matches (dotall flag to allow dot to match newlines)
        matches = re.finditer(pattern, raw_response, re.DOTALL | re.IGNORECASE)
        
        style_map = {
            "FORMAL": ("formal", 0.95),
            "CONCISE": ("concise", 0.90),
            "FRIENDLY": ("friendly", 0.85),
        }
        
        for match in matches:
            tag = match.group(1)
            text = match.group(2).strip()
            
            # Clean up tag brackets to get key
            key = tag.strip("[]").upper()
            
            if key in style_map and text:
                style, confidence = style_map[key]
                # Clean up any leading/trailing quotes or hyphens
                text = text.lstrip(" -:\"").rstrip(" \"")
                
                suggestions.append(CommentSuggestion(
                    text=text,
                    style=style,
                    confidence=confidence
                ))
        
        # Fallback: if regex failed (e.g. no tags found), try line splitting
        if not suggestions:
            lines = raw_response.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line: continue
                
                # Check if it starts with a tag manually
                found_tag = False
                for tag in style_map:
                    if line.upper().startswith(f"[{tag}]"):
                        text = line[len(tag)+2:].strip()
                        style, conf = style_map[tag]
                        suggestions.append(CommentSuggestion(text=text, style=style, confidence=conf))
                        found_tag = True
                        break
                
                if not found_tag:
                    # Treat valid text lines as suggestions if no tags found
                    if len(line) > 10: 
                        suggestions.append(CommentSuggestion(
                            text=line, 
                            style="formal", 
                            confidence=0.8
                        ))
        
        return suggestions[:3]  # Return max 3 suggestions


# Singleton instance
comment_rephraser = CommentRephraser()
