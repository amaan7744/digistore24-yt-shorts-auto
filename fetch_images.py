import os
import requests
import random

API_KEY = os.environ["PEXELS_API_KEY"]
HEADERS = {"Authorization": API_KEY}

queries = [
    "nature landscape",
    "mountains sunrise",
    "forest fog",
    "ocean waves",
    "minimal abstract background"
]

os.makedirs("images", exist_ok=True)

query = random.choice(queries)
url = f"https://api.pexels.com/v1/search?query={query}&per_page=8"

res = requests.get(url, headers=HEADERS).json()

for i, photo in enumerate(res["photos"][:6]):
    img = requests.get(photo["src"]["portrait"]).content
    with open(f"images/{i}.jpg", "wb") as f:
        f.write(img)
