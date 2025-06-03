import pyttsx3
import threading

class TTSEngine:
    """
    Text-to-speech engine for speaking decoded characters
    """
    def __init__(self):
        # Initialize TTS engine
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)
        self.lock = threading.Lock()
    
    def speak(self, text):
        """
        Speak the provided text asynchronously
        """
        # Run in a separate thread to avoid blocking
        threading.Thread(target=self._speak_async, args=(text,), daemon=True).start()
    
    def _speak_async(self, text):
        """
        Internal method to speak text with thread safety
        """
        with self.lock:
            self.engine.say(text)
            self.engine.runAndWait()