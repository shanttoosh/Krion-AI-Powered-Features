"""
Interactive AI Chat Terminal
Run: python ai_chat.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Your API Keys (Loaded from environment)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_groq_client():
    from openai import OpenAI
    return OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1"
    ), "llama-3.1-8b-instant"


def get_openai_client():
    from openai import OpenAI
    return OpenAI(api_key=OPENAI_API_KEY), "gpt-3.5-turbo"


def chat(client, model, messages):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content


def main():
    print("=" * 60)
    print("🤖 AI CHAT TERMINAL")
    print("=" * 60)
    print("\nSelect AI Provider:")
    print("1. Groq (Llama 3.1) - Fast!")
    print("2. OpenAI (GPT-3.5)")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        client, model = get_groq_client()
        provider = "Groq (Llama 3.1)"
    elif choice == "2":
        client, model = get_openai_client()
        provider = "OpenAI (GPT-3.5)"
    else:
        print("Invalid choice. Using Groq.")
        client, model = get_groq_client()
        provider = "Groq (Llama 3.1)"
    
    print(f"\n✅ Connected to {provider}")
    print("Type 'exit' to quit, 'clear' to reset conversation")
    print("-" * 60)
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
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
            
            print(f"\n🤖 {provider}: ", end="", flush=True)
            response = chat(client, model, messages)
            print(response)
            
            messages.append({"role": "assistant", "content": response})
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
