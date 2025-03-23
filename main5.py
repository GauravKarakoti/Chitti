from Frontend.GUI import (
    GraphicalUserInterface,
    SetAssistantStatus,
    ShowTextToScreen,
    TempDirectoryPath,
    SetMicrophoneStatus,
    AnswerModifier,
    QueryModifier,
    GetMicrophoneStatus,
    GetAssistantStatus
)
from Backend.Model2 import FirstLayerDMM
from Backend.SpeechToText3 import SpeechRecognition
from Backend.ChatBot2 import chat_with_bot
from Backend.TextToSpeech2 import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import logging
import os
import pygame
from PyQt5.QtCore import pyqtSignal, QObject

class Communicate(QObject):
    exit_signal = pyqtSignal()

comm = Communicate()

env_vars = dotenv_values(".env")
Username = env_vars.get("Username", "User")
Assistantname = env_vars.get("Assistantname", "Assistant")

DefaultMessage = f"""{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may I help you?"""

subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "name of application"]

def check_hardware_acceleration():
    try:
        import torch
        print(f"GPU Available: {torch.cuda.is_available()}")
        print(f"Using device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CPU'}")
    except ImportError:
        print("PyTorch not installed")

def ShowDefaultChatIfNoChats():
    try:
        with open(r'Data\ChatLog.json', "r", encoding='utf-8') as file:
            if len(file.read()) < 5:
                with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
                    f.write("")
                with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
                    f.write(DefaultMessage)
    except FileNotFoundError:
        logging.error("ChatLog.json not found. Creating new default logs.")
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as f:
            f.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as f:
            f.write(DefaultMessage)

def ReadChatLogJson():
    try:
        with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        logging.error("Error reading ChatLog.json")
        return []

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        role = Username if entry["role"] == "user" else Assistantname
        formatted_chatlog += f"{role}: {entry['content']}\n"

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    try:
        with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
            Data = file.read()

        if Data:
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(Data)
    except FileNotFoundError:
        logging.error("Database.data not found.")

def InitialExecution():
    check_hardware_acceleration()
    pygame.mixer.init()
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()
    pygame.mixer.quit()

InitialExecution()

def safe_speech_recognition():
    try:
        return SpeechRecognition()
    except Exception as e:
        logging.error(f"Speech recognition error: {e}")
        return "I couldn't understand that."

def MainExecution():
    try:
        pygame.mixer.quit()
        SetAssistantStatus("Listening ... ")
        Query = safe_speech_recognition()
        if not any([lang in Query for lang in ['ा','ी','ू','े','ो','ं','Hindi','english']]):
            ShowTextToScreen(f"{Assistantname}: Please ask in Hindi or English")
            TextToSpeech("कृपया हिंदी या अंग्रेज़ी में पूछें। Please ask in Hindi or English.")
            return
        ShowTextToScreen(f"{Username}: {Query}")
        SetAssistantStatus("Thinking ... ")

        response = chat_with_bot(QueryModifier(Query))
        final=''
        for i in response:
            if i=='*':
                pass
            else:
                final+=i
        ShowTextToScreen(f"{Assistantname}: {final}")
        SetAssistantStatus("Answering ... ")
        TextToSpeech(final)
    except Exception as e:
        logging.error(f"MainExecution error: {e}")
        SetAssistantStatus("Available ... ")

def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()

        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()

        if "Available ... " in AIStatus:
            sleep(0.1)
        else:
            SetAssistantStatus("Available ... ")
def SecondThread():
    GraphicalUserInterface()

if __name__ == "__main__":
    comm.exit_signal.connect(lambda: os._exit(1))
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()