import edge_tts, asyncio, pygame, tempfile, os, re
import speech_recognition as sr

PRONUNCIATION = {
    "Nithin": "Nit-thin",
    "nithin": "Nit-thin",
    "Zqyrix": "Zy-rix",
    "zqyrix": "Zy-rix",
    "ZQYRIX": "Zy-rix",
}

def clean(text):
    # Fix pronunciation
    for word, phonetic in PRONUNCIATION.items():
        text = text.replace(word, phonetic)
    # Strip markdown
    text = re.sub(r'\*+', '', text)
    text = re.sub(r'#+\s?', '', text)
    text = re.sub(r'[-•]\s+', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
class Voice:
    def __init__(self):
        self.voice = "en-IN-NeerjaNeural"
        pygame.mixer.init()
        self.recognizer = sr.Recognizer()
        print("Zqyrix voice ready.")

    def speak(self, text):
        text = clean(str(text))
        print(f"\n  Zqyrix: {text}\n")
        asyncio.run(self._speak(text))

    async def _speak(self, text):
        tmp = tempfile.mktemp(suffix=".mp3")
        comm = edge_tts.Communicate(text, self.voice)
        await comm.save(tmp)
        pygame.mixer.music.load(tmp)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
        pygame.mixer.music.unload()
        os.unlink(tmp)

    def listen(self):
        mic = None
        # Try device_index=1 first, then fall back to system default (None)
        for index in [1, None]:
            try:
                mic = sr.Microphone(device_index=index)
                with mic as src:
                    pass
                break
            except Exception:
                mic = None

        if mic is None:
            print("  No working microphone found.")
            return ""

        with mic as src:
            print("  Listening...")
            self.recognizer.adjust_for_ambient_noise(src, duration=0.3)
            try:
                audio = self.recognizer.listen(src, timeout=8, phrase_time_limit=20)
            except sr.WaitTimeoutError:
                return ""
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"  You: {text}")
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""