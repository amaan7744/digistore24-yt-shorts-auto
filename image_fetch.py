#!/usr/bin/env python3
import os
import json
import hashlib
import random
import requests
from io import BytesIO
from PIL import Image

# ---------------- CONFIG ----------------
PEXELS_KEY = os.getenv("PEXELS_KEY")
if not PEXELS_KEY:
    raise SystemExit("❌ PEXELS_KEY missing")

FRAMES_DIR = "frames"
PROMPTS_FILE = "image_prompts.json"
USED_IMAGES_FILE = "used_images.json"

TARGET_W, TARGET_H = 1080, 1920
MIN_WIDTH = 1600  # relaxed: improves hit-rate without quality loss

os.makedirs(FRAMES_DIR, exist_ok=True)
HEADERS = {"Authorization": PEXELS_KEY}

# ---------------- FILTERS ----------------
BANNED_TERMS = [
    "woman", "women", "girl", "female",
    "man", "men", "person", "people",
    "couple", "romance", "portrait",
    "model", "face", "hands", "child",
    "knife", "gun", "weapon", "blood", "crime"
]

FALLBACK_PROMPTS = [
    "empty road at night, cinematic lighting",
    "dark room with window light, no people",
    "minimal desk with notebook, moody lighting",
    "city skyline at night, calm atmosphere",
    "gym equipment in empty room, dramatic shadows",
]

# ---------------------------------------

def log(msg):
    print(f"[IMG] {msg}", flush=True)

def load_used():
    if os.path.exists(USED_IMAGES_FILE):
        try:
            with open(USED_IMAGES_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_used(used):
    with open(USED_IMAGES_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(used)), f, indent=2)

def hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()

def sanitize_prompt(prompt: str) -> str:
    p = prompt.lower()
    if any(bad in p for bad in BANNED_TERMS):
        return random.choice(FALLBACK_PROMPTS)
    return prompt

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
    img = img.resize(
        (int(w * scale), int(h * scale)),
        Image.Resampling.LANCZOS
    )

    left = (img.width - TARGET_W) // 2
    top = (img.height - TARGET_H) // 2
    return img.crop((left, top, left + TARGET_W, top + TARGET_H))

def search_pexels(prompt: str):
    url = (
        "https://api.pexels.com/v1/search"
        f"?query={prompt}"
        "&orientation=portrait"
        "&per_page=40"
    )
    r = requests.get(url, headers=HEADERS, timeout=25)
    r.raise_for_status()
    return r.json().get("photos", [])

def try_fetch(prompt: str, filename: str, used_hashes: set) -> bool:
    photos = search_pexels(prompt)
    random.shuffle(photos)

    for p in photos:
        if not is_halal(p):
            continue

        src = p.get("src", {}).get("original") or p.get("src", {}).get("large2x")
        if not src:
            continue

        if p.get("width", 0) < MIN_WIDTH:
            continue

        h = hash_url(src)
        if h in used_hashes:
            continue

        try:
            img_data = requests.get(src, timeout=20).content
            img = Image.open(BytesIO(img_data)).convert("RGB")
            img = make_vertical(img)

            out_path = os.path.join(FRAMES_DIR, filename)
            img.save(out_path, quality=95, subsampling=0)

            used_hashes.add(h)
            log(f"Saved {filename} ← {prompt}")
            return True

        except Exception:
            continue

    return False

def fetch_for_prompt(prompt: str, filename: str, used_hashes: set):
    prompt = sanitize_prompt(prompt)

    if try_fetch(prompt, filename, used_hashes):
        return

    log(f"⚠️ No image for '{prompt}', using fallback")
    for fb in FALLBACK_PROMPTS:
        if try_fetch(fb, filename, used_hashes):
            return

    raise RuntimeError("❌ Image fetch failed after all fallbacks")

def main():
    if not os.path.isfile(PROMPTS_FILE):
        raise SystemExit("❌ image_prompts.json missing")

    with open(PROMPTS_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    if not isinstance(prompts, list) or len(prompts) < 3:
        raise SystemExit("❌ Invalid image prompts")

    used = load_used()

    for idx, prompt in enumerate(prompts, 1):
        fname = f"img_{idx:03d}.jpg"
        fetch_for_prompt(prompt, fname, used)

    save_used(used)
    log("✅ All images fetched successfully")

if __name__ == "__main__":
    main()
