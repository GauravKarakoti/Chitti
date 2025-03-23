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
from Backend.Model import FirstLayerDMM
from Backend.SpeechToText2 import SpeechRecognition
from Backend.ChatBot import chat_with_bot
from Backend.TextToSpeech import TextToSpeech
from dotenv import dotenv_values
from asyncio import run
from time import sleep
import subprocess
import threading
import json
import logging
import os
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
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()

InitialExecution()

def safe_speech_recognition():
    try:
        return SpeechRecognition()
    except Exception as e:
        logging.error(f"Speech recognition error: {e}")
        return "I couldn't understand that."

def MainExecution():
    SetAssistantStatus("Listening ... ")
    Query = safe_speech_recognition()
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