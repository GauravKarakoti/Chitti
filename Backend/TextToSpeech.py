import pygame
import random
import asyncio
import edge_tts # Import edge_tts for text-to-sp
import os # Import os for file path handling
from dotenv import dotenv_values # Import dotenv

# Load environment variables from a .env file
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistantVoice")

# Asynchronous function to convert text to an aud
async def TextToAudioFile(text) -> None:
    file_path = r"Data\speech.mp3" # Define the
    if os.path.exists(file_path):
        os.remove(file_path)
# If it exists, remove it to avoid overwriting errors

# Create the communicate object to generate speech
    communicate = edge_tts. Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%' )
    await communicate.save(r'Data\speech.mp3')

# Function to manage Text-to-Speech (TTS) functionality
def TTS(Text, func=lambda r=None: True):
    while True:
        try:

            asyncio.run(TextToAudioFile(Text))
            pygame.mixer.init()

# Load the generated speech file into pygame
            pygame.mixer.music.load(r"Data\speech.mp3")
            pygame.mixer.music.play() # Play the audio

            # Loop until the audio is done playing or th
            while pygame.mixer.music.get_busy():
                if func() == False: # Check if the exte
                    break
                pygame.time.Clock().tick(10)
            return True

        except Exception as e:
            print(f"Error in TTS: {e}")

        finally:
            try:
                func(False)
                pygame.mixer.music.stop() # Stop the at
                pygame.mixer.quit() # Quit the pygame

            except Exception as e: # Handle any except
                print(f"Error in finally block: {e}")

def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".") # Split the text by periods into a list of sentences

    # List of predefined responses for cases where the text is too long
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]

        # If the text is very long (more than 4 sentences and 250 characters), add a response
    if len(Data) > 4 and len(Text) >= 250:
        TTS(" ".join(Text.split(".") [0:2]) + ". " + random. choice(responses), func)

    
    else:
        TTS(Text, func)


if __name__== "__main__":
    while True:
        TextToSpeech(input("enter:"))

