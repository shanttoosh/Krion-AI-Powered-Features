"""
Test script to verify AI API keys are working.
Run: python test_ai_keys.py
"""
import os

# Your API Keys (Loaded from environment)
from dotenv import load_dotenv
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def test_groq():
    """Test Groq API"""
    print("\n🔄 Testing GROQ...")
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1"
        )
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": "Say 'Hello from Groq!' in one line"}],
            max_tokens=20,
            timeout=30
        )
        print(f"✅ GROQ WORKS! Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ GROQ FAILED: {e}")
        return False


def test_openai():
    """Test OpenAI API"""
    print("\n🔄 Testing OPENAI...")
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say 'Hello from OpenAI!' in one line"}],
            max_tokens=20,
            timeout=30
        )
        print(f"✅ OPENAI WORKS! Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OPENAI FAILED: {e}")
        return False


def test_gemini():
    """Test Google Gemini API"""
    print("\n🔄 Testing GEMINI...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content("Say 'Hello from Gemini!' in one line")
        print(f"✅ GEMINI WORKS! Response: {response.text}")
        return True
    except Exception as e:
        print(f"❌ GEMINI FAILED: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🧪 AI API KEY TESTER")
    print("=" * 50)
    
    results = {
        "Groq": test_groq(),
        "OpenAI": test_openai(),
        "Gemini": test_gemini()
    }
    
    print("\n" + "=" * 50)
    print("📊 RESULTS SUMMARY")
    print("=" * 50)
    for name, status in results.items():
        emoji = "✅" if status else "❌"
        print(f"{emoji} {name}: {'WORKING' if status else 'FAILED'}")
    print("=" * 50)
