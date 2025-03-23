import whisper
import speech_recognition as sr
from dotenv import dotenv_values
import os
import mtranslate as mt
import tempfile
import warnings
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")

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
    print(sr.Microphone.list_microphone_names())  # Add this to see available devices
    with sr.Microphone(device_index=0) as source:
        SetAssistantStatus("Listening...")
        print("\n[Listening...]")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=7, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            print("[Timeout]")
            return ""

    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio.get_wav_data())
            temp_path = temp_audio.name
        
        # Transcribe with Whisper
        model = whisper.load_model("base")
        result = model.transcribe(temp_path, fp16=False)  # Force FP32
        os.remove(temp_path)
        text = result["text"]
        
        return QueryModifier(text.strip())
        
    except Exception as e:
        print(f"Speech recognition error: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
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