import cohere
from rich import print
import streamlit as st

# Load environment variables
CohereAPIKey = st.secrets["CohereAPIKey"]

# Ensure API key is available
if not CohereAPIKey:
    raise ValueError("Cohere API key not found. Please check your .env file.")

# Initialize Cohere Client
co = cohere.Client(api_key=CohereAPIKey)

# Recognized function types
funcs = ["general", "realtime", "career"]

# Correct chat history format
ChatHistory = [
    {"role": "User", "message": "how are you?"},
    {"role": "Chatbot", "message": "general how are you?"},
]

# Instruction preamble
preamble = """
You are a very accurate Decision-Making Model that classifies queries into:
- 'general' (for chatbot queries)
- 'realtime' (for up-to-date information)
DO NOT answer queries, only classify them.
"""

def FirstLayerDMM(prompt: str, recursion_depth=0):
    if recursion_depth > 3:  # Prevent infinite recursion
        return ["general (error handling)"]

    # Call Cohere API
    stream = co.chat_stream(
        model='command-r-plus',
        message=prompt,
        temperature=0.7,
        chat_history=ChatHistory,  # Ensure correct role names
        prompt_truncation='OFF',
        connectors=[],
        preamble=preamble
    )

    # Extract response
    response_text = ""
    for event in stream:
        if event.event_type == "text-generation":
            response_text += event.text 

    #print(f"Raw Response: {response_text}")  # Debugging step

    # Process response
    response = [task.strip() for task in response_text.replace("\n", "").split(",")]

    # Filter recognized categories
    filtered_response = [task for task in response if any(task.startswith(f) for f in funcs)]

    if not filtered_response:  # Retry if the response is invalid
        return FirstLayerDMM(prompt, recursion_depth + 1)

    return filtered_response

# Run interactive loop
if __name__ == "__main__":
    while True:
        user_input = input(">>> ")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Goodbye!")
            break
        print(FirstLayerDMM(user_input))