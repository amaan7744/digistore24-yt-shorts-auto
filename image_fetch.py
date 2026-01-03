#!/usr/bin/env python3
import os
import json
import hashlib
import random
import requests
from io import BytesIO
from PIL import Image

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
PEXELS_KEY = os.getenv("PEXELS_API_KEY") or os.getenv("PEXELS_KEY")
if not PEXELS_KEY:
    raise SystemExit("❌ PEXELS_API_KEY / PEXELS_KEY missing")

FRAMES_DIR = "frames"
PROMPTS_FILE = "image_prompts.json"
USED_IMAGES_FILE = "used_images.json"

TARGET_W, TARGET_H = 1080, 1920
MIN_WIDTH = 1600

os.makedirs(FRAMES_DIR, exist_ok=True)
HEADERS = {"Authorization": PEXELS_KEY}

BANNED_TERMS = [
    "woman", "women", "girl", "female",
    "man", "men", "person", "people",
    "face", "portrait", "model",
    "knife", "gun", "weapon", "blood", "crime"
]

FALLBACK_PROMPTS = [
    "empty road at night, cinematic lighting",
    "dark room with window light, no people",
    "minimal desk with notebook, moody light",
    "city skyline at night, calm atmosphere",
    "empty gym equipment, dramatic shadows"
]

# --------------------------------------------------

def log(msg):
    print(f"[IMG] {msg}", flush=True)

def load_used():
    if os.path.exists(USED_IMAGES_FILE):
        try:
            with open(USED_IMAGES_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            pass
    return set()

def save_used(used):
    with open(USED_IMAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(used)), f, indent=2)

def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def is_halal(photo) -> bool:
    text = " ".join([
        photo.get("alt", ""),
        photo.get("url", ""),
        photo.get("photographer", "")
    ]).lower()
    return not any(b in text for b in BANNED_TERMS)

def make_vertical(img: Image.Image) -> Image.Image:
    w, h = img.size
    scale = max(TARGET_W / w, TARGET_H / h)
    img = img.resize((int(w * scale), int(h * scale)), Image.Resampling.LANCZOS)
    left = (img.width - TARGET_W) // 2
    top = (img.height - TARGET_H) // 2
    return img.crop((left, top, left + TARGET_W, top + TARGET_H))

def search(prompt: str):
    url = (
        "https://api.pexels.com/v1/search"
        f"?query={prompt}&orientation=portrait&per_page=40"
    )
    r = requests.get(url, headers=HEADERS, timeout=20)
    r.raise_for_status()
    return r.json().get("photos", [])

def try_fetch(prompt, filename, used):
    photos = search(prompt)
    random.shuffle(photos)

    for p in photos:
        if not is_halal(p):
            continue

        src = p["src"].get("original") or p["src"].get("large2x")
        if not src or p.get("width", 0) < MIN_WIDTH:
            continue

        h = hash_url(src)
        if h in used:
            continue

        try:
            img = Image.open(BytesIO(requests.get(src, timeout=15).content)).convert("RGB")
            img = make_vertical(img)
            img.save(os.path.join(FRAMES_DIR, filename), quality=95, subsampling=0)
            used.add(h)
            log(f"Saved {filename} ← {prompt}")
            return True
        except Exception:
            continue

    return False

def main():
    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    used = load_used()

    for i, prompt in enumerate(prompts, 1):
        fname = f"img_{i:03d}.jpg"
        if try_fetch(prompt, fname, used):
            continue

        for fb in FALLBACK_PROMPTS:
            if try_fetch(fb, fname, used):
                break
        else:
            raise RuntimeError("Image fetch failed completely")

    save_used(used)
    log("✅ Images fetched")

if __name__ == "__main__":
    main()
