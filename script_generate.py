#!/usr/bin/env python3
import os
import sys
import json
import time
import hashlib
import random

from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
MODEL_NAME = "openai/gpt-4o-mini"
ENDPOINT = "https://models.github.ai/inference"

SCRIPT_FILE = "script.txt"
IMAGE_PROMPTS_FILE = "image_prompts.json"
USED_SCRIPTS_FILE = "used_scripts.json"

MAX_RETRIES = 3

DOMAINS = [
    "gym discipline and physical transformation",
    "business growth and execution mindset",
    "self-improvement and personal responsibility",
    "long-term investing and wealth psychology",
    "health, routine, and mental clarity",
    "relationships, boundaries, and self-respect"
]

# --------------------------------------------------
# ENV
# --------------------------------------------------
TOKEN = os.getenv("GH_MODELS_TOKEN")
if not TOKEN:
    print("❌ GH_MODELS_TOKEN missing", file=sys.stderr)
    sys.exit(1)

client = ChatCompletionsClient(
    endpoint=ENDPOINT,
    credential=AzureKeyCredential(TOKEN),
)

# --------------------------------------------------
# UTIL
# --------------------------------------------------
def load_used():
    if not os.path.exists(USED_SCRIPTS_FILE):
        return set()
    with open(USED_SCRIPTS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_used(used):
    with open(USED_SCRIPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(used), f, indent=2)

def clean(text: str) -> str:
    return text.replace("```", "").strip()

def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# --------------------------------------------------
# PROMPT
# --------------------------------------------------
def build_prompt(domain: str) -> str:
    return f"""
You are an elite motivational writer for viral YouTube Shorts.

DOMAIN:
{domain}

TASK:
Write a 30–40 second motivational narration.

STRICT RULES:
- Short, punchy sentences
- No questions
- No clichés
- No emojis
- No quotes from real people
- Direct, disciplined, grounded tone
- Action-oriented and slightly uncomfortable
- Must feel NEW and non-repetitive
- No storytelling about specific individuals
- No hype words like "legendary", "alpha", or "grind"

END STYLE:
End with a hard truth or personal responsibility statement.

After the script, output IMAGE PROMPTS as JSON.

IMAGE RULES:
- NO people
- Symbolic objects only
- Cinematic lighting
- Realistic
- 4 beats: focus, struggle, clarity, resolve

OUTPUT FORMAT (EXACT):

SCRIPT:
<text>

IMAGES_JSON:
[
  "prompt 1",
  "prompt 2",
  "prompt 3",
  "prompt 4"
]
"""

# --------------------------------------------------
# MAIN
# --------------------------------------------------
def main():
    used_hashes = load_used()
    domain = random.choice(DOMAINS)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🧠 Generating motivation script ({domain}) — attempt {attempt}")

            response = client.complete(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You write original motivational narration."},
                    {"role": "user", "content": build_prompt(domain)},
                ],
                temperature=0.9,
                max_tokens=700,
            )

            text = clean(response.choices[0].message.content)

            if "SCRIPT:" not in text or "IMAGES_JSON:" not in text:
                raise ValueError("Missing required sections")

            script_part, images_part = text.split("IMAGES_JSON:")
            script = script_part.replace("SCRIPT:", "").strip()
            images = json.loads(images_part.strip())

            if len(script) < 220:
                raise ValueError("Script too short")

            script_hash = hash_text(script)
            if script_hash in used_hashes:
                raise ValueError("Repeated script detected")

            if len(images) < 4:
                raise ValueError("Not enough image prompts")

            used_hashes.add(script_hash)
            save_used(used_hashes)

            with open(SCRIPT_FILE, "w", encoding="utf-8") as f:
                f.write(script)

            with open(IMAGE_PROMPTS_FILE, "w", encoding="utf-8") as f:
                json.dump(images, f, indent=2)

            print("✅ Unique motivational script + image prompts generated")
            return

        except (HttpResponseError, ValueError, json.JSONDecodeError) as e:
            print(f"⚠️ Retry {attempt}: {e}", file=sys.stderr)
            time.sleep(2)

    print("❌ Failed to generate unique motivational script", file=sys.stderr)
    sys.exit(1)

# --------------------------------------------------
if __name__ == "__main__":
    main()
