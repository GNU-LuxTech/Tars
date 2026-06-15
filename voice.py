import pyttsx3
import speech_recognition as sr
from colorama import Fore, Style

class VoiceEngine:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        # Reverting to default microphone since the test worked with it
        self.microphone = sr.Microphone()
        
        print(Fore.CYAN + "Adjusting for ambient noise... Please stay silent.")
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
        print(Fore.CYAN + f"Microphone calibrated. Threshold: {self.recognizer.energy_threshold}")

    def speak(self, text):
        """Speak using a native English voice to ensure proper TARS accent."""
        if not text: return
        print(Fore.BLUE + Style.BRIGHT + f"TARS: (Speaking...)" + Style.RESET_ALL)
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            # Debug: List voices if you want to see what's available
            # for v in voices: print(f"Voice: {v.name} - ID: {v.id}")

            selected_voice = None
            
            # 1. Try to find Microsoft David (the most TARS-like standard Windows voice)
            for v in voices:
                if "david" in v.name.lower():
                    selected_voice = v.id
                    break
            
            # 2. Try to find any English Male voice
            if not selected_voice:
                for v in voices:
                    name = v.name.lower()
                    if ("english" in name or "en_us" in name) and "male" in name:
                        selected_voice = v.id
                        break
            
            # 3. Fallback to any English voice
            if not selected_voice:
                for v in voices:
                    name = v.name.lower()
                    if "english" in name or "en_us" in name or "en_gb" in name:
                        selected_voice = v.id
                        break
            
            # 3. Last resort: first voice in list
            if not selected_voice and voices:
                selected_voice = voices[0].id

            if selected_voice:
                engine.setProperty('voice', selected_voice)
            
            # TARS has a very specific, slightly mechanical cadence
            engine.setProperty('rate', 175) 
            engine.setProperty('volume', 1.0)
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            print(Fore.RED + f"(TTS Error: {e})")

    def start_background_listening(self, callback):
        return self.recognizer.listen_in_background(self.microphone, callback)

    def listen_active(self):
        with self.microphone as source:
            print(Fore.GREEN + Style.BRIGHT + "(Listening for command...)" + Style.RESET_ALL)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                return self.recognizer.recognize_google(audio).lower()
            except:
                return None
