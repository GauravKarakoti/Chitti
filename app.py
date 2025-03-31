import streamlit as st
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import realtime_search_engine
from Backend.SpeechToText import SpeechRecognition
from Backend.ChatBot import chat_with_bot
from Backend.TextToSpeech import TextToSpeech

Username = st.secrets["Username"]
Assistantname = st.secrets["Assistantname"]

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        f"{Username} : Hello {Assistantname}, How are you?",
        f"{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"
    ]

if 'listening' not in st.session_state:
    st.session_state.listening = False

# Streamlit UI
st.title(f"{Assistantname} AI Assistant")

# Chat container
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        st.markdown(f"**{message.split(':')[0]}**: {message.split(':')[1]}")

# Controls
col1, col2 = st.columns([1, 6])
with col1:
    if st.button("🎤 Start Listening"):
        st.session_state.listening = True

with col2:
    user_input = st.text_input("Type your message:", disabled=st.session_state.listening)

# Status area
status_area = st.empty()

def update_chat(user_msg, assistant_msg):
    st.session_state.chat_history.append(f"{Username} : {user_msg}")
    st.session_state.chat_history.append(f"{Assistantname} : {assistant_msg}")
    chat_container.empty()
    with chat_container:
        for message in st.session_state.chat_history:
            st.markdown(f"**{message.split(':')[0]}**: {message.split(':')[1]}")

def process_query(query):
    status_area.info("Processing...")
    
    # Your existing processing logic
    Decision = FirstLayerDMM(query)
    merged_query = " and ".join([" ".join(i.split()[1:]) for i in Decision])
    
    if any("realtime" in q for q in Decision):
        response = realtime_search_engine(query)
    else:
        response = chat_with_bot(query)
    
    update_chat(query, response)
    TextToSpeech(response)
    
    status_area.empty()

# Main loop
if st.session_state.listening:
    status_area.info("Listening...")
    query = SpeechRecognition()
    if query:
        st.session_state.listening = False
        process_query(query)

if user_input:
    process_query(user_input)