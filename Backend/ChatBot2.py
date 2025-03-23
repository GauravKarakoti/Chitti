import google.generativeai as genai
from json import load, dump
import datetime
import os
from dotenv import dotenv_values

env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GEMINI_API_KEY = env_vars.get("GEMINI_API_KEY")

# Correct configuration
genai.configure(
    api_key=GEMINI_API_KEY,
    transport='rest',
    client_options={
        'api_endpoint': 'https://generativelanguage.googleapis.com/v1'  # Note v1 not v1beta
    }
)

CHAT_LOG_PATH = "Data/ChatLog.json"
MODEL_NAME = "gemini-1.5-pro-latest"
messages = []

system_message = f"""Hello, I am {Username}. You are a multilingual AI assistant named {Assistantname}.
- Always respond in the same language as the user's query
- Maintain natural conversational style in the target language
- Provide concise, accurate answers
- Use appropriate cultural context
- Never mention your language capabilities
- Avoid machine translation artifacts"""

def load_chat_log():
    os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)
    try:
        if os.path.exists(CHAT_LOG_PATH) and os.path.getsize(CHAT_LOG_PATH) > 0:
            with open(CHAT_LOG_PATH, "r", encoding='utf-8') as file:
                return load(file)
        return []
    except Exception as e:
        print(f"Load error: {e}")
        return []

def save_chat_log(messages):
    try:
        os.makedirs(os.path.dirname(CHAT_LOG_PATH), exist_ok=True)
        with open(CHAT_LOG_PATH, "w", encoding='utf-8') as file:
            dump(messages, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Save error: {e}")

def get_realtime_information():
    now = datetime.datetime.now()
    return f"""Current Context:
Day: {now.strftime('%A')}
Date: {now.strftime('%d')}
Month: {now.strftime('%B')}
Year: {now.strftime('%Y')}
Time: {now.strftime('%H:%M:%S')}
"""

def format_answer(answer):
    return "\n".join(line.strip() for line in answer.splitlines() if line.strip())

def chat_with_bot(query):
    global messages
    messages = load_chat_log()

    try:
        # Convert existing messages to Gemini format
        history = []
        for msg in messages:
            if msg['role'] == 'user':
                history.append({
                    'role': 'user',
                    'parts': [{'text': msg['content']}]
                })
            elif msg['role'] == 'assistant':
                history.append({
                    'role': 'model',
                    'parts': [{'text': msg['content']}]
                })

        # Create model instance
        model = genai.GenerativeModel(MODEL_NAME)
        chat = model.start_chat(history=history)

        # Combine system instructions with real-time info and query
        full_prompt = f"{system_message}\n{get_realtime_information()}\n{query}"
        
        # Send properly formatted message
        response = model.generate_content(
            f"{system_message}\n{get_realtime_information()}\n{query}",
            stream=True,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1024
            )
        )

        answer = ""
        for chunk in response:
            answer += chunk.text

        # Update chat log in original format
        messages.append({"role": "user", "content": query})
        messages.append({"role": "assistant", "content": answer})
        save_chat_log(messages)
        
        return format_answer(answer)

    except Exception as e:
        print(f"API Error: {e}")
        return "Service unavailable. Please try again."

if __name__ == "__main__":
    while True:
        user_query = input("Enter Your Question: ")
        print(chat_with_bot(user_query))