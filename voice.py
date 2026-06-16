import os
import io
import time
import pyttsx3
import speech_recognition as sr
import numpy as np
import sounddevice as sd
from pedalboard import Pedalboard, Bitcrush, HighpassFilter, Reverb, Compressor
from pedalboard.io import AudioFile
from elevenlabs.client import ElevenLabs
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

        # Define the TARS DSP chain for local fallback
        self.board = Pedalboard([
            HighpassFilter(cutoff_frequency_hz=250),
            Bitcrush(bit_depth=12),
            Compressor(threshold_db=-12, ratio=4),
            Reverb(room_size=0.05, wet_level=0.15, dry_level=0.85)
        ])

        # ElevenLabs Configuration
        self.el_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.el_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "q1UaN10vD9lUfZW8F8QL") # Default to Cove
        self.el_client = None
        
        if self.el_api_key:
            try:
                self.el_client = ElevenLabs(api_key=self.el_api_key)
                print(Fore.CYAN + "ElevenLabs AI Voice engine initialized.")
            except Exception as e:
                print(Fore.YELLOW + f"Warning: ElevenLabs failed to init: {e}. Using local fallback.")

    def speak(self, text):
        """Speak using ElevenLabs AI Voice with automatic local fallback."""
        if not text: return
        
        # Try ElevenLabs first
        if self.el_client:
            try:
                print(Fore.BLUE + Style.BRIGHT + f"TARS: (AI Speaking...)" + Style.RESET_ALL)
                audio_generator = self.el_client.text_to_speech.convert(
                    text=text,
                    voice_id=self.el_voice_id,
                    model_id="eleven_turbo_v2_5", # Turbo for lower latency
                    output_format="mp3_44100_128"
                )
                
                # Convert generator to bytes
                audio_bytes = b"".join(list(audio_generator))
                
                # Play using sounddevice (needs to be converted from MP3 bytes)
                # Since we want to avoid extra complex dependencies like pydub's playback 
                # or system mpv, we'll use pydub to convert bytes to numpy array
                from pydub import AudioSegment
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format="mp3")
                samples = np.array(audio_segment.get_array_of_samples()).astype(np.float32) / 32768.0
                
                # Handle stereo/mono
                if audio_segment.channels == 2:
                    samples = samples.reshape((-1, 2))
                
                sd.play(samples, audio_segment.frame_rate)
                sd.wait()
                return
            except Exception as e:
                print(Fore.YELLOW + f"(ElevenLabs Error: {e}. Switching to tactical fallback...)")

        # Fallback to Local DSP Filter
        self._speak_local(text)

    def _speak_local(self, text):
        """Fallback local TTS with mechanical filter."""
        print(Fore.BLUE + Style.BRIGHT + f"TARS: (Speaking...)" + Style.RESET_ALL)
        temp_file = "tars_speech_raw.wav"
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            selected_voice = None
            for v in voices:
                if "david" in v.name.lower():
                    selected_voice = v.id; break
            if not selected_voice:
                for v in voices:
                    v_name = v.name.lower()
                    if ("english" in v_name or "en_us" in v_name) and "male" in v_name:
                        selected_voice = v.id; break
            if not selected_voice and voices:
                selected_voice = voices[0].id
            if selected_voice:
                engine.setProperty('voice', selected_voice)
            
            engine.setProperty('rate', 155)
            engine.setProperty('volume', 1.0)
            engine.save_to_file(text, temp_file)
            engine.runAndWait()
            engine.stop()

            with AudioFile(temp_file) as f:
                audio = f.read(f.frames)
                samplerate = f.samplerate

            processed_audio = self.board(audio, samplerate)
            sd.play(processed_audio.T, samplerate)
            sd.wait()
        except Exception as e:
            print(Fore.RED + f"(Vocal Filter Error: {e})")
        finally:
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except: pass

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
