import os
import sys
import time
import queue
import speech_recognition as sr
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv
from colorama import init, Fore, Style
from voice import VoiceEngine

# Initialize colorama
init(autoreset=True)
load_dotenv()

# Configure GenAI
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print(Fore.RED + "Error: GOOGLE_API_KEY not found.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

SYSTEM_INSTRUCTION = """
You are TARS from Interstellar. 
Personality: 90% Honesty, 75% Humor, Military-grade Sarcasm.
Blunt, robotic, and highly intelligent.
"""

# Thread-safe queue for voice events
voice_queue = queue.Queue()

def voice_callback(recognizer, audio):
    """Callback function for background listening with fuzzy matching."""
    try:
        text = recognizer.recognize_google(audio).lower()
        # Debug: Print what was heard
        print(Fore.BLACK + Style.BRIGHT + f"(Heard: {text})")
        
        # Fuzzy wake words expanded based on your latest tests
        wake_words = ["tars", "hey tars", "8 hours", "lotus", "a ta", "ta", "stars", "task", "hey da", "day", "hello t"]
        
        detected = False
        command = text
        
        for word in wake_words:
            if word in text:
                detected = True
                command = text.replace(word, "").strip()
                break
        
        if detected:
            if command or any(w in text for w in ["tars", "task", "lotus"]):
                voice_queue.put(command if command else "WAKE_ONLY")
            
    except sr.UnknownValueError:
        pass
    except Exception:
        pass

def process_command(user_command, chat, voice_engine):
    """Sends a message to Gemini and speaks the response."""
    if not user_command:
        return

    # Retry logic for 503/429 errors
    response = None
    for attempt in range(3):
        try:
            response = chat.send_message(user_command)
            break
        except errors.ClientError as e:
            if "429" in str(e):
                msg = "My apologies, but Google has capped my cognitive throughput for the day. (Quota exceeded). We'll have to continue once the sensors reset."
                print(Fore.RED + f"\nTARS: {msg}")
                voice_engine.speak(msg)
                return
            raise e
        except errors.ServerError as e:
            if "503" in str(e) and attempt < 2:
                print(Fore.YELLOW + f"(Server busy, retrying attempt {attempt+1}...)" + Style.RESET_ALL)
                time.sleep(2)
                continue
            else:
                raise e
    
    if response:
        tars_text = response.text
        print(Fore.BLUE + Style.BRIGHT + "\nTARS: " + Style.RESET_ALL + Fore.BLUE + tars_text)
        voice_engine.speak(tars_text)

def main():
    print(Fore.CYAN + Style.BRIGHT + "--- TARS Tactical Interface ---")
    print(Fore.CYAN + "Background listening active. Say 'Hey TARS' anytime.")
    
    config = types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION, temperature=0.7)
    chat = client.chats.create(model="models/gemini-3.5-flash", config=config)
    
    voice_engine = VoiceEngine()
    stop_listening = voice_engine.start_background_listening(voice_callback)

    try:
        active_conversation = False
        while True:
            # Standby Mode: Wait for wake word in the background queue
            if not active_conversation:
                if not voice_queue.empty():
                    voice_input = voice_queue.get()
                    
                    # STOP background listening to free the microphone context
                    if stop_listening:
                        stop_listening(wait_for_stop=False)
                    
                    print(Fore.CYAN + "\n--- Wake Word Detected ---")
                    
                    if voice_input == "WAKE_ONLY":
                        greeting = "I'm here. What's the plan?"
                        print(Fore.BLUE + f"TARS: {greeting}")
                        voice_engine.speak(greeting)
                        active_conversation = True
                    else:
                        # User said "Hey TARS [command]"
                        user_command = voice_input
                        active_conversation = True
                        # Process the command immediately
                        process_command(user_command, chat, voice_engine)
            
            # Active Conversation Mode: Persistent loop
            while active_conversation:
                user_command = voice_engine.listen_active()
                
                if not user_command:
                    continue
                
                print(Fore.GREEN + f"You: {user_command}")
                
                if any(word in user_command for word in ["exit", "quit", "power down"]):
                    farewell = "Powering down. See you in the next system."
                    print(Fore.BLUE + f"TARS: {farewell}")
                    voice_engine.speak(farewell)
                    return # Exit the entire program

                if any(word in user_command for word in ["standby", "stop listening", "go to sleep"]):
                    msg = "Returning to standby. Wake me if the mission parameters change."
                    print(Fore.CYAN + f"\n--- {msg} ---")
                    voice_engine.speak(msg)
                    active_conversation = False
                    
                    # Clear the queue
                    while not voice_queue.empty(): voice_queue.get()
                    
                    # RESTART background listening
                    print(Fore.CYAN + Style.DIM + "(Restarting background sensors...)")
                    stop_listening = voice_engine.start_background_listening(voice_callback)
                    break

                process_command(user_command, chat, voice_engine)

            time.sleep(0.1)

    except KeyboardInterrupt:
        print(Fore.BLUE + "\nTARS: Manual override. Shutting down.")
    finally:
        stop_listening(wait_for_stop=False)

if __name__ == "__main__":
    main()
