from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920

img = Image.new("RGB", (W, H), "black")
draw = ImageDraw.Draw(img)
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)

with open("script.txt") as f:
    text = f.read()

draw.multiline_text((100, 500), text, fill="white", font=font, spacing=20)

img.save("frame.png")

audio = AudioFileClip("voice.wav")
video = ImageClip("frame.png").set_duration(audio.duration)
video = video.set_audio(audio)

video.write_videofile(
    "output.mp4",
    fps=30,
    codec="libx264",
    audio_codec="aac"
)
