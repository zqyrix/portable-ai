import re, os, subprocess, webbrowser, glob
import psutil
from datetime import datetime
from brain import Brain
from voice import Voice
import json

brain = Brain()
voice = Voice()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHORTCUTS_FILE = os.path.join(BASE_DIR, "shortcuts.json")

def load_shortcuts():
    if os.path.exists(SHORTCUTS_FILE):
        with open(SHORTCUTS_FILE) as f:
            return json.load(f)
    return {}

def save_shortcuts(sc):
    with open(SHORTCUTS_FILE, "w") as f:
        json.dump(sc, f, indent=2)

shortcuts = load_shortcuts()

APPS = {
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "notepad": "notepad.exe",
    "explorer": "explorer.exe",
    "calculator": "calc.exe",
    "vscode": os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe"),
    "spotify": os.path.expandvars(r"%APPDATA%\Spotify\Spotify.exe"),
    "task manager": "taskmgr.exe",
    "telegram": os.path.expandvars(r"%APPDATA%\Telegram Desktop\Telegram.exe"),
    "whatsapp": os.path.expandvars(r"%LOCALAPPDATA%\WhatsApp\WhatsApp.exe"),
    "word": os.path.expandvars(r"%PROGRAMFILES%\Microsoft Office\root\Office16\WINWORD.EXE"),
    "excel": os.path.expandvars(r"%PROGRAMFILES%\Microsoft Office\root\Office16\EXCEL.EXE"),
}

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "telegram": "https://web.telegram.org",
    "instagram": "https://www.instagram.com",
    "twitter": "https://www.twitter.com",
    "github": "https://www.github.com",
    "gmail": "https://mail.google.com",
    "google": "https://www.google.com",
    "netflix": "https://www.netflix.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "chatgpt": "https://chat.openai.com",
}

def edit_code_file(filepath, instruction):
    try:
        # Read the file
        with open(filepath, "r", encoding="utf-8") as f:
            original = f.read()

        # Ask brain to make the edit
        prompt = f"""You are a Python code editor. Here is a Python file:

```python
{original}
```

Instruction: {instruction}

Return ONLY the complete modified Python code with no explanation, no markdown, no backticks. Just raw Python code."""

        response = brain.think(prompt)

        # Clean the response — strip markdown if model added it
        code = response.strip()
        if code.startswith("```"):
            code = re.sub(r"^```[\w]*\n?", "", code)
            code = re.sub(r"\n?```$", "", code)
        code = code.strip()

        # Backup original
        backup_folder = os.path.join(BASE_DIR, "backup")
        os.makedirs(backup_folder, exist_ok=True)
        backup_name = os.path.basename(filepath) + f"_{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup"
        backup = os.path.join(backup_folder, backup_name)
        with open(backup, "w", encoding="utf-8") as f:
            f.write(original)

        # Write new version
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)

        return f"Done! I've edited {os.path.basename(filepath)}. A backup was saved as {os.path.basename(backup)}."

    except Exception as e:
        return f"Couldn't edit the file: {e}"

def route(text):
    t = text.lower().strip()
    # ── Code editing — MUST BE FIRST ────────────────────────
    if any(w in t for w in ["edit","modify","update","change","add to","fix"]) and ".py" in t:
        file_match = re.search(r"([\w]+\.py)", t)
        filepath = os.path.join(BASE_DIR, file_match.group(1)) if file_match else os.path.join(BASE_DIR, "zqyrix.py")
        instruction = re.sub(r"(edit|modify|update|change|fix|add to)\s+[\w]+\.py\s*(and|to|-)?", "", t).strip()
        voice.speak(f"Editing {os.path.basename(filepath)}, give me a moment.")
        return edit_code_file(filepath, instruction or t)

    # ── Code editing ─────────────────────────────────────────
    edit_match = re.search(
        r"(edit|modify|update|change|add to|remove from|fix)\s+(.+?\.py)\s+(?:and|to|-)?\s*(.+)",
        t
    )
    if edit_match or any(w in t for w in ["edit the code", "modify the code", "edit zqyrix", "add to the file", "edit the file"]):
        # Figure out which file
        file_match = re.search(r"([\w]+\.py)", t)
        if file_match:
            fname = file_match.group(1)
            filepath = os.path.join(BASE_DIR, fname)
        else:
            filepath = os.path.join(BASE_DIR, "zqyrix.py")  # default to self

        # Get the instruction (everything after the filename)
        instruction = re.sub(r"(edit|modify|update|change|fix|add to|remove from)\s+[\w]+\.py\s*(and|to|-)?", "", t).strip()
        if not instruction:
            instruction = t  # fallback to full text

        voice.speak(f"Editing {os.path.basename(filepath)}. Give me a moment.")
        return edit_code_file(filepath, instruction)

    # ── YouTube search ───────────────────────────────────────
    if "youtube" in t and any(w in t for w in ["search","play","find","look up","watch"]):
        query = re.sub(r"(search|play|find|look up|watch|on youtube|youtube)", "", t).strip()
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}."

    # ── System info ──────────────────────────────────────────
    if "battery" in t:
        b = psutil.sensors_battery()
        if b:
            status = "charging" if b.power_plugged else "on battery"
            return f"Battery is at {int(b.percent)} percent, {status}."
        return "Couldn't read battery info."

    if "what time" in t or "current time" in t:
        return datetime.now().strftime("It's %I:%M %p")

    if "what date" in t or "today's date" in t or "what's the date" in t:
        return datetime.now().strftime("Today is %A, %d %B %Y")

    if "cpu" in t or "processor" in t:
        return f"CPU usage is at {psutil.cpu_percent(interval=1)} percent."

    if ("ram" in t or "memory usage" in t) and "open" not in t:
        r = psutil.virtual_memory()
        return f"RAM usage is {r.percent} percent. {round(r.available/1e9, 1)} GB available."

    if "disk" in t or "storage" in t:
        drive = os.path.splitdrive(BASE_DIR)[0] or "C:"
        if os.name == 'nt' and not drive.endswith('\\'):
            drive += '\\'
        try:
            d = psutil.disk_usage(drive)
            return f"{drive} drive has {round(d.free/1e9, 1)} GB free out of {round(d.total/1e9, 1)} GB."
        except Exception:
            d = psutil.disk_usage("/")
            return f"System storage has {round(d.free/1e9, 1)} GB free out of {round(d.total/1e9, 1)} GB."

    # ── Screenshot ───────────────────────────────────────────
    if "screenshot" in t:
        import pyautogui
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshots_dir = os.path.join(BASE_DIR, "Screenshots")
        path = os.path.join(screenshots_dir, f"snap_{ts}.png")
        os.makedirs(screenshots_dir, exist_ok=True)
        pyautogui.screenshot(path)
        return "Screenshot saved."

    # ── Remember shortcuts ───────────────────────────────────
    m = re.search(r"remember (.+?) (?:is at|is in|as) (.+)", t)
    if m:
        name = m.group(1).strip()
        path = m.group(2).strip()
        shortcuts[name] = path
        save_shortcuts(shortcuts)
        return f"Got it! I'll remember {name}."

    # ── Open websites and apps ───────────────────────────────
    if "open" in t:
        # Saved shortcuts first
        for name, path in shortcuts.items():
            if name in t:
                os.startfile(path)
                return f"Opening {name}."

        # Known websites
        for site, url in WEBSITES.items():
            if site in t:
                webbrowser.open(url)
                return f"Opening {site}."

        # Installed apps
        for app, path in APPS.items():
            if app in t:
                try:
                    os.startfile(path)
                    return f"Opened {app}."
                except:
                    # Fallback to web version
                    if app in WEBSITES:
                        webbrowser.open(WEBSITES[app])
                        return f"Opened {app} in browser."

        # Generic URL
        url = re.search(r'([\w]+\.[\w]+)', t.replace("open ", ""))
        if url and "." in url.group():
            webbrowser.open("https://" + url.group())
            return f"Opening {url.group()} in browser."

    # ── Find file ────────────────────────────────────────────
    if "find" in t and "file" in t:
        name = re.sub(r"(find|the|file|my|a)", "", t).strip()
        results = glob.glob(os.path.join(os.path.expanduser("~"), "**", f"*{name}*"), recursive=True)[:3]
        if results:
            return "Found: " + ", ".join(results)
        return f"Couldn't find any file matching {name}."

    # ── Web search ───────────────────────────────────────────
    if any(w in t for w in ["search for","look up","google","what is","who is","latest","news","search the web"]):
        try:
            from ddgs import DDGS
            q = re.sub(r"(search for|look up|google|find info about|search the web for)", "", text, flags=re.I).strip()
            with DDGS() as d:
                results = list(d.text(q, max_results=4))
            if results:
                ctx = "Web results:\n" + "\n".join([f"- {r['title']}: {r['body'][:150]}" for r in results])
                return brain.think(text, context=ctx)
        except Exception as e:
            pass
        return brain.think(text)

    # ── Notes ────────────────────────────────────────────────
    if t.startswith("note ") or "make a note" in t:
        note = re.sub(r"^(note|make a note that?|make a note)", "", t).strip()
        notes_file = os.path.join(BASE_DIR, "notes.txt")
        with open(notes_file, "a") as f:
            f.write(f"{datetime.now().strftime('%d %b %H:%M')} — {note}\n")
        return "Noted."

    if "show my notes" in t or "read my notes" in t:
        notes_file = os.path.join(BASE_DIR, "notes.txt")
        if os.path.exists(notes_file):
            with open(notes_file) as f:
                lines = f.readlines()[-5:]
            return "Your last notes: " + " | ".join(lines)
        return "No notes saved yet."

    # ── Session ──────────────────────────────────────────────
    if "save" in t and any(w in t for w in ["session","conversation","chat"]):
        return brain.save_session()

    if "clear memory" in t or "forget everything" in t:
        return brain.reset()

    # ── Default ──────────────────────────────────────────────
    return brain.think(text)

def main():
    print("\n" + "="*45)
    print("  Z Q Y R I X  —  Online")
    print("="*45)
    mode = input("\n  Mode: (1) Voice  (2) Text → ").strip()
    voice.speak("Hey Nithin! Zqyrix online and ready.")

    while True:
        try:
            if mode == "1":
                user_input = voice.listen()
            else:
                user_input = input("\n  You: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit","quit","bye","goodbye","shutdown"]:
                voice.speak("Going offline. Catch you later Nithin!")
                break

            response = route(user_input)
            voice.speak(str(response))

        except KeyboardInterrupt:
            voice.speak("Shutting down. See you Nithin!")
            break
        except Exception as e:
            print(f"  Error: {e}")
            voice.speak("Small error but still here.")

if __name__ == "__main__":
    main()