import speech_recognition as sr

# Change this number to test different microphones
MIC_INDEX = 2

r = sr.Recognizer()

try:
    with sr.Microphone(device_index=MIC_INDEX) as source:
        print(f"Opened microphone {MIC_INDEX}: {sr.Microphone.list_microphone_names()[MIC_INDEX]}")
        print("Say something...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, timeout=5)
        print("You said:", r.recognize_google(audio))
except Exception as e:
    print(type(e).__name__, e)