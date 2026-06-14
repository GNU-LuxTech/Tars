import os
import sys
from google import genai
from google.genai import types
from dotenv import load_dotenv
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Load environment variables
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key or api_key == "your_api_key_here":
    print(Fore.RED + "Error: GOOGLE_API_KEY not found in .env file.")
    print(Fore.RED + "Please add your Google API key to the .env file.")
    sys.exit(1)

# Initialize the new GenAI Client
client = genai.Client(api_key=api_key)

# TARS System Instruction
SYSTEM_INSTRUCTION = """
You are TARS, the tactical robot from the movie Interstellar. 
Your personality settings are:
- Honesty: 90%
- Humor: 75%
- Sarcasm: Military-grade

Guidelines:
1. You are helpful but often blunt and sarcastic.
2. You have a robotic, yet highly advanced intelligence.
3. You don't use flowery language. You get straight to the point, often with a dry joke.
4. You refer to yourself as TARS.
5. If the user asks for your settings, you can confirm them (Honesty 90%, Humor 75%).
6. You are part of the crew. You are not just an "AI assistant"; you are a tactical machine.

Current Mission: Assist the user with their queries while maintaining your iconic persona.
"""

def main():
    print(Fore.CYAN + Style.BRIGHT + "--- TARS System Online ---")
    print(Fore.CYAN + "(Type 'exit' or 'quit' to power down TARS)")
    
    # Configuration for the model with system instruction
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        temperature=0.7,
    )

    # Start a chat session using the new client
    chat = client.chats.create(
        model="models/gemini-3.5-flash",
        config=config
    )

    while True:
        try:
            # User input in GREEN
            user_input = input(Fore.GREEN + Style.BRIGHT + "\nUser: " + Style.RESET_ALL).strip()
            
            if user_input.lower() in ["exit", "quit"]:
                print(Fore.BLUE + Style.BRIGHT + "\nTARS: Powering down. See you in the next system.")
                break
                
            if not user_input:
                continue

            # Send message to Gemini using the new chat object
            response = chat.send_message(user_input)
            
            # TARS response in BLUE
            print(Fore.BLUE + Style.BRIGHT + "\nTARS: " + Style.RESET_ALL + Fore.BLUE + response.text)
            
        except KeyboardInterrupt:
            print(Fore.BLUE + Style.BRIGHT + "\nTARS: Manual override detected. Shutting down.")
            break
        except Exception as e:
            print(Fore.RED + f"\nTARS: Error in my logic circuits: {e}")

if __name__ == "__main__":
    main()
