import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------
# LOAD SCRIPT
# --------------------------------------------------
with open("script.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

# --------------------------------------------------
# LOAD AUDIO
# --------------------------------------------------
audio = AudioFileClip("voice/male.wav")

# --------------------------------------------------
# SETTINGS
# --------------------------------------------------
WIDTH = 1080
HEIGHT = 1920
IMAGE_COUNT = 6
DURATION_PER_IMAGE = audio.duration / IMAGE_COUNT

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SIZE = 48

clips = []

# --------------------------------------------------
# BUILD FRAMES WITH PIL SUBTITLES
# --------------------------------------------------
for i in range(IMAGE_COUNT):
    img_path = f"images/{i}.jpg"

    base = Image.open(img_path).convert("RGB")
    base = base.resize((WIDTH, HEIGHT))

    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    text_w, text_h = draw.multiline_textsize(text, font=font)
    x = (WIDTH - text_w) // 2
    y = (HEIGHT - text_h) // 2

    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill="white",
        align="center"
    )

    frame_path = f"frame_{i}.png"
    base.save(frame_path)

    clip = (
        ImageClip(frame_path)
        .set_duration(DURATION_PER_IMAGE)
        .resize(lambda t: 1 + 0.05 * t / DURATION_PER_IMAGE)
    )

    clips.append(clip)

# --------------------------------------------------
# CONCAT + AUDIO
# --------------------------------------------------
video = concatenate_videoclips(clips, method="compose")
final = video.set_audio(audio)

# --------------------------------------------------
# EXPORT
# --------------------------------------------------
final.write_videofile(
    "output.mp4",
    fps=30,
    codec="libx264",
    audio_codec="aac",
    threads=4
)
