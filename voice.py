import pyttsx3
import threading
import re

class CoachVoice:
    def __init__(self):
        self.rate = 180
        self.volume = 1.0

    def _clean_text_for_speech(self, text):
        """Formats 'E2' to 'E 2' so the AI pronounces coordinates clearly."""
        cleaned = re.sub(r'([A-Ha-h])([1-8])', r'\1 \2', text)
        return cleaned

    def speak(self, text):
        """Runs a fresh engine instance in a thread to prevent GUI hanging."""
        if not text:
            return

        speech_content = self._clean_text_for_speech(text)

        def _run_engine():
            try:
                engine = pyttsx3.init()
                voices = engine.getProperty('voices')
                if len(voices) > 1:
                    engine.setProperty('voice', voices[1].id)
                
                engine.setProperty('rate', self.rate)
                engine.setProperty('volume', self.volume)
                
                engine.say(speech_content)
                engine.runAndWait()
                engine.stop()
                del engine
            except Exception as e:
                print(f"Voice System Error: {e}")

        threading.Thread(target=_run_engine, daemon=True).start()

coach_voice = CoachVoice()