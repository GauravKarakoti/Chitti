from googlesearch import search
from groq import Groq
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from the .env file
env_vars = dotenv_values(".env")

Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")
GROQ_API_KEY = env_vars.get("GROQ_API_KEY")



client = Groq(api_key=GROQ_API_KEY)

# Chatbot instructions
system_message = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} with real-time up-to-date information from the internet.
*** Provide answers in a professional way. Ensure proper grammar, punctuation, and formatting.***
*** Just answer the question from the provided data professionally. ***"""

# Chat log file path
CHAT_LOG_PATH = "Data/ChatLog.json"


def load_chat_log():
    try:
        with open(CHAT_LOG_PATH, "r") as file:
            return load(file)
    except FileNotFoundError:
        return []


def save_chat_log(messages):
    with open(CHAT_LOG_PATH, "w") as file:
        dump(messages, file, indent=4)


def google_search(query):
    try:
        results = list(search(query, advanced=True, num_results=5))
        if not results:
            return "No search results found."
        answer = f"The search results for '{query}' are:\n[start]\n"
        for result in results:
            answer += f"Title: {result.title}\nDescription: {result.description}\n\n"
        answer += "[end]"
        return answer
    except Exception as e:
        return f"Error performing Google search: {e}"


def get_realtime_information():
    now = datetime.datetime.now()
    return f"""Use This Real-time Information if needed:
Day: {now.strftime('%A')}
Date: {now.strftime('%d')}
Month: {now.strftime('%B')}
Year: {now.strftime('%Y')}
Time: {now.strftime('%H')} hours, {now.strftime('%M')} minutes, {now.strftime('%S')} seconds.
"""


def clean_answer(answer):
    lines = [line.strip() for line in answer.splitlines() if line.strip()]
    return "\n".join(lines)


def realtime_search_engine(prompt):
    global system_message

    # Load existing chat messages
    messages = load_chat_log()
    messages.append({"role": "user", "content": prompt})

    # Perform a Google search
    search_results = google_search(prompt)

    # Construct chatbot messages
    chatbot_system = [{"role": "system", "content": system_message}]
    chatbot_system.append({"role": "system", "content": search_results})
    chatbot_system.append({"role": "system", "content": get_realtime_information()})

    # Generate a response using Groq
    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=chatbot_system + messages,
            temperature=0.7,
            max_tokens=2048,
            top_p=1,
            stream=True,
            stop=None,
        )
        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content
        answer = clean_answer(answer)

        # Append the assistant's response to the chat log
        messages.append({"role": "assistant", "content": answer})
        save_chat_log(messages)

        return answer
    except Exception as e:
        return f"An error occurred while generating a response: {e}"


if __name__ == "__main__":
    while True:
        query = input("Enter your query: ")
        response = realtime_search_engine(query)
        print(response)
