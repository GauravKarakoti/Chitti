from AppOpener import close, open as appopen # Import fun
from webbrowser import open as webopen
from pywhatkit import search, playonyt # Import functions
from bs4 import BeautifulSoup # Import BeautifulSoup for
from rich import print # Import rich for styled console o
from groq import Groq
import webbrowser
import subprocess
import requests
import keyboard
import asyncio
import os # Import os for operating system functionalitie
from dotenv import load_dotenv
# Load environment variables from the .env file.
load_dotenv()
# env_vars = dotenv_values(".env")
GROQ_API_KEY = os.getenv("GroqAPIKey")

classes = ["zCubwf", "hgKElc", "LTKOO sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf", "pclqee", "tw-Data-text tw-text-small tw-ta",
"IZ6rdc", "05uR6d LTKOO", "vlzY6d", "webanswers-webanswers_table_webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
"LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"]

# Define a user-agent for making web requests.
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
client = Groq(api_key=GROQ_API_KEY)

# Predefined professional responses for user interactions.
professional_responses = [
"Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
"I'm at your service for any additional questions or support you may need-don't hesitate to ask.",
]


messages = []

# System message to provide context to the chatbot.
SystemChatBot = [{"role": "system", "content": f"Hello, I am {os. environ['Username']}, You're a content writer. You have to write content like letters, codes, applications, essays, notes, songs, poems etc."}]

# Function to perform a Google search.
def GoogleSearch(Topic):
    search(Topic)
    return True # Indicate success.


def Content(Topic):

# Nested function to open a file in Notepad.
    def OpenNotepad(File):
        default_text_editor = 'notepad.exe' # Default text editor.
        subprocess. Popen([default_text_editor, File])

# Nested function to generate content using the AI chatbot.
    def ContentWriterAI(prompt):
        messages.append( {"role": "user", "content": f"{prompt}"})

        completion = client.chat.completions.create(
            model="mixtral-8x7b-32768", # Specify the AI model.
            messages=SystemChatBot + messages, # Include system instructions and chat Listory.
            max_tokens=2048, # Limit the maximum tokens in the response.
            temperature=0.7, # Adjust response randomness.
            top_p=1, # Use nucleus sampling for response diversity.
            stream=True, # Enable streaming response.
            stop=None # Allow the model to determine stopping conditions.
        )

        Answer =""


        for chunk in completion:
            if chunk. choices[0].delta.content: # Check for content in the current chunk.
                Answer += chunk.choices[0].delta.content # Append the content to the answer.

        Answer = Answer.replace("</s>", "") # Remove unwanted tokens from the response.
        messages.append({"role": "assistant", "content": Answer}) # Add the AI's response to mes
        return Answer

    Topic: str = Topic.replace("Content ", "")
    ContentByAI = ContentWriterAI(Topic) # Generate content using AI.
    # Save the generated content to a text file.
    with open(rf"Data\{Topic.lower().replace(' ','')}.txt", "w", encoding="utf-8") as file:
        file.write(ContentByAI) # Write the content to the file.
        file. close()

    OpenNotepad(rf"Data\{Topic.lower().replace(' ','')}.txt") # Open the file in Notepad.
    return True # Indicate success.
def YouTubeSearch(Topic):
    Url4Search = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(Url4Search)
    # Open the search URL in a web browser.
    return True # Indicate success.

# Function to play a video on YouTube.
def PlayYoutube(query):
    playonyt(query) # Use pywhatkit's playonyt function to play the video.
    return True # Indicate success.

# Function to open an application or a relevant webpage.
def OpenApp(app, sess=requests.session( )):

    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True # Indicate success.

    except :
    # Nested function to extract links from HTML content.
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser') # Parse the HTML content.
            links = soup. find_all('a', {'jsname': 'UWckNb' }) # Find relevant links.
            return [link.get('href') for link in links] # Return the link
        
        # Perform the Google search.

# Nested function to perform a Google search and retrie
        def search_google(query):
            url = f"https://www.google.com/search?q={query}"#
            headers = {"User-Agent": useragent} # Use the pred
            response = sess.get(url, headers=headers) # Perfor

            if response.status_code == 200:
                return response.text # Return the HTML content
            else:
                print("Failed to retrieve search results.")
                return None

        html = search_google(app)

        if html:
            link = extract_links(html)[0] # Extract the first
            webopen(link) # Open the link in a web browser.

        return True # Indicate success.
    
def CloseApp(app):

    if "chrome" in app:
        pass # Skip if the app is Chrome.
    else:
        try:

            close(app, match_closest=True, output=True, throw_error=True)
            return True
        except:
            return False # Indicate failure.

# Function to execute system-level commands.
def System(command):

# Nested function to mute the system volume.
    def mute():
        keyboard. press_and_release("volume mute")

    # Nested function to unmute the system volume.
    def unmute():
        keyboard. press_and_release("volume mute")

    # Nested function to increase the system volume.
    def volume_up( ):
        keyboard. press_and_release("volume up")

    # Nested function to decrease the system volume.
    def volume_down( ):
        keyboard.press_and_release("volume down") # Simulate the volume dow

    if command == "mute":
        mute()
    elif command == "unmute":
        unmute()
    elif command == "volume up":
        volume_up( )
    elif command == "volume down":
        volume_down( )

    return True # Indicate success.


async def TranslateAndExecute(commands: list[str]):

    funcs = []

    for command in commands:

        if command.startswith("open "): # Handle "open" commands.

            if "open it" in command: # Ignore "open it" commands.
                pass

            if "open file" == command: # Ignore "open file" commands.
                pass

            else:
                fun = asyncio.to_thread(OpenApp, command.removeprefix("open "))
                funcs. append(fun)

        elif command.startswith("general "): # Placeholder for general commands.
            pass

        elif command.startswith("realtime "): # Placeholder for real-time commands.
            pass

        elif command.startswith("close "): # Handle "close" commands.
            fun = asyncio. to_thread(CloseApp, command. removeprefix("close "))
            funcs.append(fun)

        elif command. startswith("play "): # Handle "play" commands.
            fun = asyncio. to_thread(PlayYoutube, command.removeprefix("play "))
            funcs.append(fun)

        elif command. startswith("content "): # Handle "content" commands.
            fun = asyncio. to_thread(Content, command. removeprefix("content "))
            funcs. append(fun)

        elif command.startswith("google search "): # Handle Google search commands.
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search "))
            funcs.append(fun)

        elif command.startswith("youtube search "): # Handle YouTube search commands.
            fun = asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search"))
            funcs.append(fun)

        elif command.startswith("system "): # Handle system commands.
            fun = asyncio.to_thread(System, command. removeprefix("system "))
            funcs.append(fun)

        elif command.startswith("content "): # Handle "content" commands.
            fun = asyncio. to_thread(Content, command. removeprefix("content"))
            funcs.append(fun)

        elif command.startswith("google search "): # Handle Google search commands.
            fun = asyncio.to_thread(GoogleSearch, command.removeprefix("google search"))
            funcs.append(fun)

        elif command.startswith("youtube search "): # Handle YouTube search commands.
            fun = asyncio. to_thread(YouTubeSearch, command. removeprefix("youtube search "))
            funcs.append(fun)

        elif command.startswith("system "): # Handle system commands.
            fun = asyncio. to_thread(System, command. removeprefix("system "))
            funcs.append(fun)

        else:
            print(f"No Function Found. For {command}")

# Execute all tasks concurrently
    results = await asyncio.gather(*funcs)


    for result in results: # Process the results.
        if isinstance(result, str):
            yield result
    else:
        yield result

# Asynchronous function to automate command execution.
async def Automation(commands: list[str]):

    async for result in TranslateAndExecute(commands):
        pass

    return True