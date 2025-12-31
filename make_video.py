import os
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/bin/ffmpeg"

from moviepy.editor import *
from PIL import ImageFont

with open("script.txt") as f:
    text = f.read()

audio = AudioFileClip("voices/male.wav")
clips = []
duration_per_image = audio.duration / 6

img = (
    ImageClip(f"images/{i}.jpg")
    .resize(height=1920)
    .crop(x_center=540, width=1080)
    .set_duration(duration_per_image)
    .resize(lambda t: 1 + 0.05 * t / duration_per_image)
)

    clips.append(img)

video = concatenate_videoclips(clips, method="compose")

subtitle = (
    TextClip(
        text,
        fontsize=48,
        color="white",
        font="DejaVu-Sans-Bold",
        method="caption",
        size=(900, None),
        align="center"
    )
    .set_position(("center", "center"))
    .set_duration(audio.duration)
)

final = CompositeVideoClip([video, subtitle]).set_audio(audio)

final.write_videofile(
    "output.mp4",
    fps=30,
    codec="libx264",
    audio_codec="aac"
)
