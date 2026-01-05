"""
Interactive AI Chat Terminal
Run: python ai_chat.py
"""

import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


# ---------- CLIENT SETUPS ----------

def get_groq_client():
    from openai import OpenAI
    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    ), "llama-3.1-8b-instant", "groq"


def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY), "gpt-3.5-turbo", "openai"


def get_gemini_client():
    from google import genai

    client = genai.Client(api_key=GEMINI_API_KEY)
    model = "gemini-2.5-flash"

    return client, model, "gemini"


# ---------- CHAT HANDLER ----------

def chat(client, model, messages, provider):
    if provider in ["groq", "openai"]:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content

    elif provider == "gemini":
        prompt = "\n".join(
            f"{m['role']}: {m['content']}" for m in messages
        )

        response = client.models.generate_content(
            model=model,
            contents=prompt
        )
        return response.text


# ---------- MAIN LOOP ----------

def main():
    print("=" * 60)
    print("🤖 AI CHAT TERMINAL")
    print("=" * 60)

    print("\nSelect AI Provider:")
    print("1. Groq (Llama 3.1) – Fast")
    print("2. OpenAI (GPT-3.5)")
    print("3. Gemini (Google)")
    print()

    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        client, model, provider = get_groq_client()
        name = "Groq (Llama 3.1)"
    elif choice == "2":
        client, model, provider = get_openai_client()
        name = "OpenAI (GPT-3.5)"
    elif choice == "3":
        client, model, provider = get_gemini_client()
        name = "Gemini (2.5-flash)"
    else:
        print("Invalid choice. Defaulting to Groq.")
        client, model, provider = get_groq_client()
        name = "Groq (Llama 3.1)"

    print(f"\n✅ Connected to {name}")
    print("Type 'exit' to quit | 'clear' to reset")
    print("-" * 60)

    messages = [{"role": "system", "content": "You are a helpful assistant."}]

    while True:
        try:
            user_input = input("\n👤 You: ").strip()

            if not user_input:
                continue
            if user_input.lower() == "exit":
                print("\n👋 Goodbye!")
                break
            if user_input.lower() == "clear":
                messages = [{"role": "system", "content": "You are a helpful assistant."}]
                print("🔄 Conversation cleared!")
                continue

            messages.append({"role": "user", "content": user_input})
            print(f"\n🤖 {name}: ", end="", flush=True)

            response = chat(client, model, messages, provider)
            print(response)

            messages.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
