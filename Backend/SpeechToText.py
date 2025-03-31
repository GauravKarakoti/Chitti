from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import streamlit as st
import os
import mtranslate as mt
import time

InputLanguage = st.secrets["InputLanguage"]  # Default to English

# Define the HTML code for the speech recognition interface.
HtmlCode = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Speech Recognition</title>
</head>
<body>
    <button id="start" onclick="startRecognition()">Start Recognition</button>
    <button id="end" onclick="stopRecognition()">Stop Recognition</button>
    <p id="output"></p>
    <script>
        const output = document.getElementById('output');
        let recognition;

        function startRecognition() {
            recognition = new (window.webkitSpeechRecognition || window.SpeechRecognition)();
            recognition.lang = '';
            recognition.continuous = true;

            recognition.onresult = function(event) {
                const transcript = event.results[event.results.length - 1][0].transcript;
                output.textContent += transcript + " ";
            };

            recognition.onend = function() {
                recognition.start();
            };

            recognition.start();
        }

        function stopRecognition() {
            recognition.stop();
            output.textContent = "";
        }
    </script>
</body>
</html>'''

# Replace the language setting in the HTML code with the input language from the environment variables.
HtmlCode = HtmlCode.replace("recognition.lang = '';", f"recognition.lang = '{InputLanguage}';")

# Write the modified HTML code to a file.
data_dir = os.path.join(os.getcwd(), "Data")
os.makedirs(data_dir, exist_ok=True)  # Ensure the Data directory exists

html_file_path = os.path.join(data_dir, "Voice.html")
with open(html_file_path, "w", encoding="utf-8") as f:
    f.write(HtmlCode)

# Set Chrome options for the WebDriver.
chrome_options = Options()
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.142.86 Safari/537.36"
chrome_options.add_argument(f"user-agent={user_agent}")
chrome_options.add_argument("--use-fake-ui-for-media-stream")
chrome_options.add_argument("--use-fake-device-for-media-stream")
chrome_options.add_argument("--headless=new")

# Initialize the Chrome WebDriver using the ChromeDriverManager.
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Define the path for temporary files.
temp_dir_path = os.path.join(os.getcwd(), "Frontend", "Files")
os.makedirs(temp_dir_path, exist_ok=True)  # Ensure the directory exists

# Function to set the assistant's status by writing it to a file.
def SetAssistantStatus(status):
    status_file_path = os.path.join(temp_dir_path, "Status.data")
    with open(status_file_path, "w", encoding="utf-8") as file:
        file.write(status)

# Function to modify a query string (add punctuation, format correctly).
def QueryModifier(query):
    query = query.lower().strip()
    if not query:
        return query.capitalize()

    question_words = [
        "how", "what", "who", "where", "when", "why", "which", "whose", "whom",
        "can you", "what's", "where's", "how's"
    ]
    
    if any(query.startswith(word) for word in question_words):
        if query[-1] not in ['.', '?', '!']:
            query += "?"
    else:
        if query[-1] not in ['.', '?', '!']:
            query += "."
    return query.capitalize()

# Function to translate text to English.
def UniversalTranslator(text):
    english_translation = mt.translate(text, "en", "auto")
    return english_translation.capitalize()

# Function to perform speech recognition using the WebDriver.
def SpeechRecognition():
    # Open the HTML file in the browser.
    driver.get("file:///" + html_file_path.replace("\\", "/"))
    driver.find_element(By.ID, "start").click()
    
    while True:
        try:
            # Get the recognized text from the HTML output element.
            text = driver.find_element(By.ID, "output").text.strip()
            if text:
                driver.find_element(By.ID, "end").click()  # Stop recognition
                if "en" in InputLanguage.lower():
                    return QueryModifier(text)
                else:
                    SetAssistantStatus("Translating ...")
                    return QueryModifier(UniversalTranslator(text))
                    
        except Exception as e:
            time.sleep(0.5)  # Prevent high CPU usage on continuous retries

# Main loop to continuously recognize and process speech.
if __name__ == "__main__":
    try:
        while True:
            recognized_text = SpeechRecognition()
            print(recognized_text)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        driver.quit()
