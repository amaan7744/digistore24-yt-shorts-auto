from gtts import gTTS

with open("script.txt", "r", encoding="utf-8") as f:
    text = f.read()

tts = gTTS(text=text, lang="en", slow=False)
tts.save("voice.mp3")
