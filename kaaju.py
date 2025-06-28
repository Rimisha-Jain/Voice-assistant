import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import string
import ctypes
import urllib.parse

# === Initialize Speech Engine ===
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Change index to your preferred voice
recognizer = sr.Recognizer()

# === Speak Function ===
def speak(text):
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

# === Listen Function ===
def listen_command():
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    try:
        command = recognizer.recognize_google(audio)
        command = command.lower()
        print("You said:", command)
        return command
    except sr.UnknownValueError:
        speak("Sorry, I didn't understand that.")
        return ""
    except sr.RequestError:
        speak("Sorry, my speech service is down.")
        return ""

# === Get All Drives on PC ===
def get_all_drives():
    drives = []
    bitmask = ctypes.windll.kernel32.GetLogicalDrives()
    for letter in string.ascii_uppercase:
        if bitmask & 1:
            drives.append(f"{letter}:\\")
        bitmask >>= 1
    return drives

# === Open Website by Name (used with 'open website') ===
def open_website(command):
    speak("Searching the web for that website.")
    name = command.replace("open", "").replace("website", "").strip()
    name = name.replace(" dot ", ".").replace(" ", "+")
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(name)}"

    try:
        webbrowser.open(search_url)
        speak(f"Searching for {name} on Google")
    except Exception as e:
        speak("Sorry, I couldn't open the website.")
        print(f"Error: {e}")

# === "Search the Internet" Feature ===
def search_website(name):
    speak(f"Searching the internet for {name}")
    query = urllib.parse.quote(name)
    search_url = f"https://www.google.com/search?q={query}"
    try:
        webbrowser.open(search_url)  # Uses your default browser
        speak(f"Opened search results for {name}")
    except Exception as e:
        speak("Sorry, I couldn't open the website.")
        print(f"Error: {e}")

def handle_internet_search():
    speak("What is the name of the website?")
    website_name = listen_command()
    if website_name:
        search_website(website_name)

# === Search and Open Specific File or Folder ===
def search_and_open(name, mode="file"):
    speak(f"Searching your PC for the {mode} named {name}. Please wait...")
    all_drives = get_all_drives()
    matches = []

    for drive in all_drives:
        for root, dirs, files in os.walk(drive):
            items_to_search = files if mode == "file" else dirs
            for item in items_to_search:
                item_lower = item.lower()
                if name in item_lower:
                    path = os.path.join(root, item)

                    # Scoring the match
                    if item_lower == name:
                        score = 3  # Exact match
                    elif item_lower.startswith(name):
                        score = 2  # Starts with
                    else:
                        score = 1  # Contains

                    matches.append((score, path, item))

    # If no matches at all — search for "close-looking" folders anyway
    if not matches:
        speak(f"I couldn't find an exact or partial match, but I'll try to open the closest name.")
        for drive in all_drives:
            for root, dirs, files in os.walk(drive):
                items_to_search = files if mode == "file" else dirs
                for item in items_to_search:
                    path = os.path.join(root, item)
                    score = 0  # Lowest score, but still something
                    matches.append((score, path, item))
            if matches:
                break  # Stop after the first drive that returns anything

    if not matches:
        speak(f"Sorry, your computer has no {mode}s at all to search.")
        return

    # Sort and open best match (highest score)
    best_match = sorted(matches, key=lambda x: -x[0])[0]
    _, best_path, best_item = best_match

    try:
        os.startfile(best_path)
        speak(f"I opened the most closely matching {mode}: {best_item}")
    except Exception as e:
        speak("I found something close, but couldn't open it.")
        print(f"Error: {e}")


# === Handle "Search My Computer" Flow ===
def search_pc():
    speak("Would that be a file or a folder?")
    category = listen_command()

    if "file" in category:
        speak("Please tell me the name of the file.")
        name = listen_command()
        search_and_open(name, mode="file")
    elif "folder" in category:
        speak("Please tell me the name of the folder.")
        name = listen_command()
        search_and_open(name, mode="folder")
    else:
        speak("I didn't get that. Please say file or folder.")

# === Handle Open Commands ===
def handle_open_command(command):
    if "website" in command:
        open_website(command)
    else:
        speak("If you want to search your PC, please say 'I want you to search my computer'.")

# === Main Program Loop ===
speak("Hello, how may I help you today?")

while True:
    command = listen_command()

    if "exit" in command or "quit" in command:
        speak("Bye")
        break
    elif "i want you to search my computer" in command or "search my computer" in command:
        search_pc()
    elif "search the internet" in command:
        handle_internet_search()
    elif "open" in command:
        handle_open_command(command)
