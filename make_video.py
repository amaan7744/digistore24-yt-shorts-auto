from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    TextClip
)

# --------------------------------------------------
# LOAD SCRIPT
# --------------------------------------------------
with open("script.txt", "r", encoding="utf-8") as f:
    text = f.read().strip()

# --------------------------------------------------
# LOAD AUDIO (PRE-GENERATED VOICE)
# --------------------------------------------------
audio = AudioFileClip("voices/male.wav")

# --------------------------------------------------
# VIDEO SETTINGS
# --------------------------------------------------
WIDTH = 1080
HEIGHT = 1920
IMAGE_COUNT = 6
DURATION_PER_IMAGE = audio.duration / IMAGE_COUNT

clips = []

# --------------------------------------------------
# BUILD IMAGE SEQUENCE WITH SLOW ZOOM
# --------------------------------------------------
for i in range(IMAGE_COUNT):
    img = (
        ImageClip(f"images/{i}.jpg")
        .resize(height=HEIGHT)
        .crop(x_center=WIDTH // 2, width=WIDTH)
        .set_duration(DURATION_PER_IMAGE)
        .resize(lambda t: 1 + 0.05 * t / DURATION_PER_IMAGE)
    )
    clips.append(img)

# --------------------------------------------------
# CONCAT IMAGES
# --------------------------------------------------
background = concatenate_videoclips(clips, method="compose")

# --------------------------------------------------
# SUBTITLE (CENTERED, SMALL, READABLE)
# --------------------------------------------------
subtitle = (
    TextClip(
        text,
        fontsize=48,
        font="DejaVu-Sans-Bold",
        color="white",
        method="caption",
        size=(900, None),
        align="center"
    )
    .set_position(("center", "center"))
    .set_duration(audio.duration)
)

# --------------------------------------------------
# FINAL COMPOSITION
# --------------------------------------------------
final = CompositeVideoClip([background, subtitle]).set_audio(audio)

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
