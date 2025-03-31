from Frontend.GUI import (
GraphicalUserInterface,
SetAssistantStatus,
ShowTextToScreen,
TempDirectoryPath,
SetMicrophoneStatus,
AnswerModifier,
QueryModifier,
GetMicrophoneStatus,
GetAssistantStatus )
from Backend.Model import FirstLayerDMM
from Backend.RealtimeSearchEngine import realtime_search_engine
from Backend.Automation import Automation
from Backend.SpeechToText import SpeechRecognition
from Backend.ChatBot import chat_with_bot
from Backend.TextToSpeech import TextToSpeech
import streamlit as st
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

Username = st.secrets["Username"]
Assistantname = st.secrets["Assistantname"]
DefaultMessage = f'''{Username} : Hello {Assistantname}, How are you?
{Assistantname} : Welcome {Username}. I am doing well. How may i help you?'''
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search","name of application"]


def ShowDefaultChatIfNoChats():
    File = open(r'Data\ChatLog.json',"r", encoding='utf-8')
    if len(File.read())<5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
             file.write("")

        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)

def ReadChatLogJson():
    with open(r'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data

def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""
    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content' ]}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content' ]}\n"
    formatted_chatlog = formatted_chatlog.replace("User",Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant",Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))

def ShowChatsOnGUI():
    File = open(TempDirectoryPath('Database.data'),"r", encoding='utf-8')
    Data = File.read()
    if len(str(Data))>0:
        lines = Data.split('\n')
        result = '\n'.join(lines)
        File.close()
        File = open(TempDirectoryPath('Responses.data'),"w", encoding='utf-8')
        File.write(result)
        File.close()

def InitialExecution():
        SetMicrophoneStatus("False")
        ShowTextToScreen("")
        ShowDefaultChatIfNoChats()
        ChatLogIntegration()
        ShowChatsOnGUI()

InitialExecution()

def Dateconverter(Query):       
    Date = Query.replace(" and ","-")
    Date = Date.replace(" and ","-")
    Date = Date.replace("and","-")
    Date = Date.replace("and","-")
    Date = Date.replace(" ","")

    return str(Date)

def MainExecution():

        TaskExecution = True
        ImageExecution = False
        ImageGenerationQuery = ""

        SetAssistantStatus("Listening ... ")
        Query = SpeechRecognition()
        ShowTextToScreen(f"{Username} : {Query}")
        SetAssistantStatus("Thinking ... ")
        Decision = FirstLayerDMM(Query)

        print("")
        print(f"Decision : {Decision}")
        print("")

        G = any([i for i in Decision if i.startswith( "general" ) ])
        R = any([i for i in Decision if i.startswith("realtime")])
        

        Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime") or i.startswith("FUNCTION")]
        )

        for queries in Decision:
            if "generate " in queries:
                ImageGenerationQuery = str(queries)
                ImageExecution = True

        for queries in Decision:
            if TaskExecution==False:
                continue
            print("Decision is : ", Decision)
            
            try:
                if any(queries.startswith(func) for func in Functions):
                        
                    run(Automation(list(Decision)))  # Ensure Automation is properly handled
                    TaskExecution = True
                        
            except FileNotFoundError as e:
                logging.error(f"File not found in Automation: {e}")
                ShowTextToScreen(f"{Assistantname} : Error processing automation request.")
            except AttributeError as e:
                logging.error(f"Attribute error in Automation: {e}")
                ShowTextToScreen(f"{Assistantname} : Internal error. Please try again.")
            except Exception as e:
                logging.error(f"Unexpected error in Automation: {e}")
                ShowTextToScreen(f"{Assistantname} : An unexpected error occurred.")
                    
        if ImageExecution == True:

            with open(r"Files\ImageGeneration.data", "w") as file:
                file.write(f"{ImageGenerationQuery},True")

            try:

                p1 = subprocess. Popen(['python', r'ImageGeneration.py' ],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                stdin=subprocess. PIPE, shell=False)
                subprocesses.append(p1)

            except Exception as e:
                print(f"Error starting ImageGeneration.py: {e}")

        if G and R or R:

            SetAssistantStatus("Searching ... ")
            Answer = realtime_search_engine(QueryModifier(Mearged_query))
            ShowTextToScreen(f"{Assistantname} : {Answer}")
            SetAssistantStatus("Answering ... ")
            TextToSpeech(Answer)
            return True
        
            

        else:

            for Queries in Decision:

                if "general" in Queries:
                    SetAssistantStatus("Thinking ... ")
                    
                    QueryFinal = Queries. replace("general ", "")
                    Answer = chat_with_bot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    TextToSpeech(Answer)
                    return True
                
                

                elif "realtime" in Queries:
                    SetAssistantStatus("Searching ... ")
                    QueryFinal = Queries.replace("realtime ", "")
                    Answer = realtime_search_engine(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    TextToSpeech(Answer)
                    return True

                elif "exit" in Queries:
                    QueryFinal = "Okay, Bye!"
                    Answer = chat_with_bot(QueryModifier(QueryFinal))
                    ShowTextToScreen(f"{Assistantname} : {Answer}")
                    SetAssistantStatus("Answering ... ")
                    TextToSpeech(Answer)
                    SetAssistantStatus("Answering ... ")
                    comm.exit_signal.emit()  # Emit the signal to exit
                    return True

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

if __name__== "__main__":
    comm.exit_signal.connect(lambda: os._exit(1))  # Connect the signal to the exit function
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
