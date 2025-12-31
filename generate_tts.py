from TTS.api import TTS

tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")

with open("script.txt") as f:
    text = f.read()

tts.tts_to_file(text=text, file_path="voice.wav")
