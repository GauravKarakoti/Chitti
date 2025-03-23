import speech_recognition as sr
from dotenv import dotenv_values
import os
import mtranslate as mt

# Load environment variables
env_vars = dotenv_values(".env")
InputLanguage = env_vars.get("InputLanguage", "en-US")

# Define temporary directory path
temp_dir_path = os.path.join(os.getcwd(), "Frontend", "Files")
os.makedirs(temp_dir_path, exist_ok=True)

def SetAssistantStatus(status):
    status_file_path = os.path.join(temp_dir_path, "Status.data")
    with open(status_file_path, "w", encoding="utf-8") as file:
        file.write(status)

def QueryModifier(query):
    query = query.lower().strip()
    if not query:
        return query.capitalize()

    question_words = [
        "how", "what", "who", "where", "when", "why", "which", 
        "whose", "whom", "can you", "what's", "where's", "how's"
    ]
    
    if any(query.startswith(word) for word in question_words):
        if query[-1] not in ['.', '?', '!']:
            query += "?"
    else:
        if query[-1] not in ['.', '?', '!']:
            query += "."
    return query.capitalize()

def UniversalTranslator(text):
    return mt.translate(text, "en", "auto").capitalize()

def SpeechRecognition():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        SetAssistantStatus("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
        except sr.WaitTimeoutError:
            return ""

    try:
        text = recognizer.recognize_google(audio, language=InputLanguage)
        if not text:
            return ""
            
        if "en" not in InputLanguage.lower():
            SetAssistantStatus("Translating...")
            text = UniversalTranslator(text)
            
        return QueryModifier(text)
        
    except sr.UnknownValueError:
        print("Audio could not be understood")
    except sr.RequestError as e:
        print(f"Could not request results: {e}")
    
    return ""

if __name__ == "__main__":
    try:
        while True:
            input("\nPress Enter to start listening...")
            result = SpeechRecognition()
            if result:
                print("\nRecognized:", result)
    except KeyboardInterrupt:
        print("\nExiting...")