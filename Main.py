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
from Backend.RealtimeSearchEngine import RealtimeSearchEngine
try:
    from Backend.Automation import Automation
except Exception as e:
    print(f"[WARNING] Error importing Automation: {e}")
    Automation = None
from Backend.SpeechToText import SpeechRecognition
from Backend.Chatbot import ChatBot
from Backend.TextToSpeech import TextToSpeech
from Backend.PDFGenerator import open_notepad_and_wait, convert_text_to_pdf, open_pdf, get_content_type_from_voice, generate_dynamic_content
from Backend.Alarm import SetAlarm
from Backend.FileFolderCreator import create_folder, create_file
from Backend.EmailHandler import send_email, extract_email_info_from_query, send_email_manually
from dotenv import dotenv_values
import json
import os
import sys
import time
import threading
import subprocess
from datetime import datetime
import pygame
import asyncio
import logging
from time import sleep
from asyncio import run
import queue

gui_command_queue = queue.Queue()

# Configure logger
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Import email functions
from Backend.EmailHandler import (
    send_email,
    send_email_with_manual_input,
    extract_email_info_from_query,
    format_email_with_llm
)
from Backend.SignLanguageTranslator import SignLanguageTranslator

# ---------- Load Environment Variables ----------
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")

# Default welcome message when assistant starts
DefaultMessage = f'''{Username}: Hello {Assistantname}, How are you?
{Assistantname}: Welcome {Username}. I am doing well. How may I help you?'''

# ---------- Global Variables ----------
subprocesses = []
Functions = ["open", "close", "play", "system", "content", "google search", "youtube search", "pdf conversion", "alarm", "send_email", "sign language"]

# Initialize Sign Language Translator
sign_translator = SignLanguageTranslator()


def ShowDefaultChatIfNoChats():
    file = open(rf'Data\ChatLog.json', "r", encoding='utf-8')
    if len(file.read()) < 5:
        with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
            file.write("")
        with open(TempDirectoryPath('Responses.data'), 'w', encoding='utf-8') as file:
            file.write(DefaultMessage)


def ReadChatLogJson():
    with open(rf'Data\ChatLog.json', 'r', encoding='utf-8') as file:
        chatlog_data = json.load(file)
    return chatlog_data


def ChatLogIntegration():
    json_data = ReadChatLogJson()
    formatted_chatlog = ""

    for entry in json_data:
        if entry["role"] == "user":
            formatted_chatlog += f"User: {entry['content']}\n"
        elif entry["role"] == "assistant":
            formatted_chatlog += f"Assistant: {entry['content']}\n"

    formatted_chatlog = formatted_chatlog.replace("User", Username + " ")
    formatted_chatlog = formatted_chatlog.replace("Assistant", Assistantname + " ")

    with open(TempDirectoryPath('Database.data'), 'w', encoding='utf-8') as file:
        file.write(AnswerModifier(formatted_chatlog))


def ShowChatsOnGUI():
    with open(TempDirectoryPath('Database.data'), "r", encoding='utf-8') as file:
        Data = file.read()

    if len(Data) > 0:
        lines = Data.split('\n')
        result = '\n'.join(lines)

        with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
            file.write(result)


def InitialExecution():
    SetMicrophoneStatus("False")
    ShowTextToScreen("")
    ShowDefaultChatIfNoChats()
    ChatLogIntegration()
    ShowChatsOnGUI()


def MainExecution():
    TaskExecution = False
    ImageExecution = False
    ImageGenerationQuery = ""

    latest_content = ""
    Answer = ""

    SetAssistantStatus("Listening...")

    Query = SpeechRecognition()
    print(f"[DEBUG] You said: {Query}")
    ShowTextToScreen(f"{Username}: {Query}")

    # --- PRIORITY: Sign Language Translator ---
    if "sign language" in Query.lower() or "translate to sign" in Query.lower():
        try:
            print("\n[DIRECT] Starting sign language translation...")
            TextToSpeech("Sign language starting now.")
            
            # Import and run the translator directly
            import tkinter as tk
            from Backend.SignLanguageTranslator import SignLanguageTranslator
            
            # Create and hide root window
            root = tk.Tk()
            root.withdraw()
            
            # Initialize and run translator
            translator = SignLanguageTranslator()
            translator.listen_and_translate()
            
            # Clean up
            try:
                root.destroy()
            except:
                pass
                
            return True
            
        except Exception as e:
            print(f"[SIGN ERROR] {str(e)}")
            TextToSpeech("Sorry, couldn't start sign language.")
            return True

    # --- Feature: Create Folder or File by Voice Command ---
    lower_query = Query.lower()
    import re
    folder_match = re.search(r"create (?:a )?folder(?: named| called)? ([\w\- \\/.]+)", lower_query)
    file_match = re.search(r"create (?:a )?file(?: named| called)? ([\w\- \\/.]+)", lower_query)
    if folder_match:
        folder_name = folder_match.group(1).strip().replace(" ", "_")
        success, message = create_folder(folder_name)
        ShowTextToScreen(f"{Assistantname}: {message}")
        TextToSpeech(message)
        return True
    elif file_match:
        file_name = file_match.group(1).strip().replace(" ", "_")
        success, message = create_file(file_name)
        ShowTextToScreen(f"{Assistantname}: {message}")
        TextToSpeech(message)
        return True

    SetAssistantStatus("Thinking...")
    Decision = FirstLayerDMM(Query)
    print("[DEBUG] Decision:", Decision)

    content_keywords = ['story', 'letter', 'article', 'essay']
    is_content_task = any(any(kw in task.lower() for kw in content_keywords) for task in Decision)

    if is_content_task:
        content_type = get_content_type_from_voice(Query)
        base_path = rf'C:\Users\vihar\OneDrive\Desktop\Jarvis AI\Data'
        os.makedirs(base_path, exist_ok=True)

        input_txt_path = os.path.join(base_path, f"{content_type}.txt")
        output_pdf_path = os.path.join(base_path, f"{content_type}.pdf")

        try:
            ai_generated_content = generate_dynamic_content(Query)
            open_notepad_and_wait(input_txt_path, initial_content=ai_generated_content)
            convert_text_to_pdf(input_txt_path, output_pdf_path)
            open_pdf(output_pdf_path)
            TextToSpeech(f"The content has been saved as a PDF at {output_pdf_path}")
        except Exception as e:
            print(f"[ERROR] PDF generation failed: {e}")
            TextToSpeech("Sorry, I faced an error while saving your PDF.")
            return True

    G = any([i for i in Decision if i.startswith("general")])
    R = any([i for i in Decision if i.startswith("realtime")])
    Mearged_query = " and ".join(
        [" ".join(i.split()[1:]) for i in Decision if i.startswith("general") or i.startswith("realtime")]
    )

    import re
    for queries in Decision:
        if "generate" in queries and "image" in queries:
            # Extract subject (e.g., 'cow' from 'generate image of cow' or 'generate image cow')
            match = re.search(r"generate image(?: of)? (.+)", queries, re.IGNORECASE)
            if match:
                subject = match.group(1).strip(" .")
                ImageGenerationQuery = subject
                ImageExecution = True

    for queries in Decision:
        if not TaskExecution:
            if any(queries.startswith(func) for func in Functions):
                if queries.strip() in ("email", "send_email") or queries.startswith("email") or queries.startswith("send_email"):
                    # Handle all email commands with the manual input flow
                    try:
                        # Extract any available subject/body from the query
                        _, subject, body = extract_email_info_from_query(queries)
                        
                        # Use the manual input flow which will show GUI dialogs
                        success = send_email_with_manual_input(body)
                        
                        if success:
                            TextToSpeech("Email sent successfully.")
                            ShowTextToScreen(f"{Assistantname}: Email sent successfully.")
                        else:
                            TextToSpeech("Failed to send email. Please try again.")
                            ShowTextToScreen(f"{Assistantname}: Failed to send email.")
                    except Exception as e:
                        logger.error(f"Email error: {e}", exc_info=True)
                        TextToSpeech("Sorry, there was an error sending the email.")
                        ShowTextToScreen(f"{Assistantname}: Error sending email.")
                else:
                    run(Automation(list(Decision)))
                TaskExecution = True

    if ImageExecution:
        with open(rf'Frontend\Files\ImageGeneration.data', "w") as file:
            file.write(f"{ImageGenerationQuery}, True")

        try:
            p1 = subprocess.Popen(
                ['python', rf'Backend\ImageGeneration.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE,
                shell=False
            )
            subprocesses.append(p1)
        except Exception as e:
            print(f"[ERROR] Starting ImageGeneration.py: {e}")

    for Queries in Decision:
        # Check for sign language command first - DIRECT EXECUTION
        if any(cmd in Queries.lower() for cmd in ["sign language", "translate to sign"]):
            try:
                print("\n[DEBUG] DIRECT SIGN LANGUAGE ACTIVATION")
                
                # Import required modules
                import tkinter as tk
                from Backend.SignLanguageTranslator import SignLanguageTranslator
                
                # Update status and notify user
                SetAssistantStatus("Sign Language Mode")
                TextToSpeech("Sign language ready. Speak now.")
                
                # Initialize and run translator
                translator = SignLanguageTranslator()
                
                # Create and hide root window
                root = tk.Tk()
                root.withdraw()
                
                # Run the translator directly
                try:
                    translator.listen_and_translate()
                finally:
                    try:
                        root.destroy()
                    except:
                        pass
                
                return True
                
            except Exception as e:
                print(f"[DIRECT SIGN ERROR] {str(e)}")
                TextToSpeech("Sign language translation failed.")
                return True

        # Original command processing continues...
        elif "general" in Queries:
            SetAssistantStatus("Thinking...")
            QueryFinal = Queries.replace("general", "")
            Answer = ChatBot(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif "realtime" in Queries:
            SetAssistantStatus("Searching...")
            QueryFinal = Queries.replace("realtime", "")
            Answer = RealtimeSearchEngine(QueryModifier(QueryFinal))
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            return True

        elif "alarm" in Queries or "reminder" in Queries:
            alarm_time = Queries.lower().replace("alarm", "").replace("reminder", "").strip()
            print(f"[DEBUG] Alarm time extracted for SetAlarm: '{alarm_time}'")
            SetAlarm(alarm_time)
            ShowTextToScreen(f"Alarm set for {alarm_time}")
            TextToSpeech(f"Alarm set successfully for {alarm_time}")
            return True

        elif "send email" in Query.lower():
            # Simple parsing: extract recipient name after 'send email to'
            try:
                # Example: "send email to nandan about meeting tomorrow"
                query_lower = Query.lower()
                # Extract recipient name
                recipient = None
                if "send email to" in query_lower:
                    recipient = query_lower.split("send email to")[1].strip().split()[0]  # first word after phrase
                
                # Define a subject and content for simplicity or ask user further (here hardcoded example)
                subject = "Message from Jarvis Assistant"
                content = "This is a test email sent by Jarvis AI."
                
                if recipient:
                    success = send_email(recipient, subject, content)
                    if success:
                        TextToSpeech(f"Email sent successfully to {recipient}")
                    else:
                        TextToSpeech(f"Sorry, I could not find the email for {recipient}")
                else:
                    TextToSpeech("Please specify whom to send the email to.")
            except Exception as e:
                print(f"[ERROR] Email sending failed: {e}")
                TextToSpeech("Sorry, I encountered an error sending the email.")

            return True

        # This block has been moved to the beginning of the decision loop

        elif "exit" in Queries:
            Answer = ChatBot("Okay, Bye!")
            ShowTextToScreen(f"{Assistantname}: {Answer}")
            SetAssistantStatus("Answering...")
            TextToSpeech(Answer)
            os._exit(1)



def FirstThread():
    while True:
        CurrentStatus = GetMicrophoneStatus()
        if CurrentStatus == "True":
            MainExecution()
        else:
            AIStatus = GetAssistantStatus()
            if "Available..." not in AIStatus:
                SetAssistantStatus("Available...")
            sleep(0.1)


def SecondThread():
    GraphicalUserInterface()


if __name__ == "__main__":
    InitialExecution()
    thread2 = threading.Thread(target=FirstThread, daemon=True)
    thread2.start()
    SecondThread()
