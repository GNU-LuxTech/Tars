import pyttsx3
import speech_recognition as sr
from colorama import Fore, Style

class VoiceEngine:
    def __init__(self):
        # Initialize TTS
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        
        # Initialize STT
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

    def setup_tts(self):
        """Configure TTS for a TARS-like robotic voice."""
        voices = self.tts_engine.getProperty('voices')
        
        # Priority: 1. English Male, 2. Any Male, 3. English Female, 4. First available
        selected_voice = voices[0].id
        
        # Try to find David (standard Windows male) or any male English voice
        for voice in voices:
            name = voice.name.lower()
            if "english" in name or "united states" in name or "united kingdom" in name:
                if "david" in name or "male" in name:
                    selected_voice = voice.id
                    break
                selected_voice = voice.id # fallback to any english voice (like Zira)
        
        self.tts_engine.setProperty('voice', selected_voice)
        
        # TARS speaks at a steady, slightly slower than average pace
        self.tts_engine.setProperty('rate', 165)
        self.tts_engine.setProperty('volume', 1.0)

    def speak(self, text):
        """Speak the given text."""
        print(Fore.BLUE + Style.BRIGHT + "\n(Speaking...)" + Style.RESET_ALL)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def listen(self):
        """Listen for audio input and convert to text."""
        with self.microphone as source:
            print(Fore.GREEN + Style.BRIGHT + "\n(Listening...)" + Style.RESET_ALL)
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                print(Fore.GREEN + "(Processing voice...)" + Style.RESET_ALL)
                text = self.recognizer.recognize_google(audio)
                print(Fore.GREEN + f"You said: {text}" + Style.RESET_ALL)
                return text
            except sr.WaitTimeoutError:
                print(Fore.YELLOW + "(No audio detected)" + Style.RESET_ALL)
                return None
            except sr.UnknownValueError:
                print(Fore.YELLOW + "(Could not understand audio)" + Style.RESET_ALL)
                return None
            except sr.RequestError as e:
                print(Fore.RED + f"(STT Error: {e})" + Style.RESET_ALL)
                return None
            except Exception as e:
                print(Fore.RED + f"(Unexpected voice error: {e})" + Style.RESET_ALL)
                return None
