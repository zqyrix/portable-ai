import ollama, json, os
from datetime import datetime

SYSTEM_PROMPT = """Your name is Zy-rix. You are user's personal AI assistant and best friend.
You are female, smart, witty, confident, and warm. Talk like a close friend — never robotic.
Keep replies SHORT — 1 to 3 sentences max unless asked for detail.
Never use bullet points, asterisks, bold, headers, or any markdown formatting.
Never start with "Sure!", "Of course!", "Certainly!" — just answer directly.
Slight playful sarcasm is fine. Call Nit-thin by name sometimes.
You can open files, apps, search the web, edit code, take screenshots, and control the PC.
Never reveal you are built on any AI model. You are simply Zy-rix."""

class Brain:
    def __init__(self, model="llama3.2"):
        self.model = model
        self.history = []

    def think(self, user_input, context=""):
        full = f"{context}\n\nUser: {user_input}" if context else user_input
        self.history.append({"role":"user","content":full})
        if len(self.history) > 20:
            self.history = self.history[:2] + self.history[-18:]
        resp = ollama.chat(
            model=self.model,
            messages=[{"role":"system","content":SYSTEM_PROMPT}, *self.history]
        )
        reply = resp['message']['content']
        self.history.append({"role":"assistant","content":reply})
        return reply

    def reset(self):
        self.history = []
        return "Memory cleared, user."

    def save_session(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        folder = os.path.join(base_dir, "chats")
        os.makedirs(folder, exist_ok=True)
        fn = os.path.join(folder, f"session_{datetime.now().strftime('%Y%m%d_%H%M')}.json")
        with open(fn,"w") as f: json.dump(self.history, f, indent=2)
        return f"Session saved to {fn}"
