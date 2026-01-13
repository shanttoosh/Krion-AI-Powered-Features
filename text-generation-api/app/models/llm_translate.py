import time
from app.config import settings

PROMPT = """Translate the following text into natural, fluent English.
Preserve meaning, idioms, and tone.
Do not explain.
Output ONLY the translation.

Text:
{text}
"""

def translate(text: str):
    start = time.perf_counter()

    if settings.ai_provider == "groq":
        from groq import Groq
        client = Groq(api_key=settings.groq_api_key)
        r = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": PROMPT.format(text=text)}],
            temperature=0
        )
        output = r.choices[0].message.content.strip()

    elif settings.ai_provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=settings.openai_api_key)
        r = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": PROMPT.format(text=text)}],
            temperature=0
        )
        output = r.choices[0].message.content.strip()

    elif settings.ai_provider == "gemini":
        import google.generativeai as genai
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        r = model.generate_content(PROMPT.format(text=text))
        output = r.text.strip()

    else:
        raise ValueError("Invalid AI provider")

    return output, round(time.perf_counter() - start, 3)
