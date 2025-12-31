import torch
from TTS.api import TTS

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

tts = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    progress_bar=True
).to(DEVICE)

with open("script.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

tts.tts_to_file(
    text=text,
    speaker_wav="male.wav",
    language="en",
    file_path="output.wav"
)

print("✅ Voice cloned successfully → output.wav")
