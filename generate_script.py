import json
import random

with open("products.json", "r") as f:
    products = json.load(f)

product = random.choice(products)

hooks = [
    "Most people never escape this cycle.",
    "Nobody tells beginners this.",
    "This is why skills matter more than motivation."
]

script = f"""
{random.choice(hooks)}
Most people struggle with {product['pain']} because nobody teaches them the right system.
This isn’t hype. It’s a real framework designed for beginners.
If you want to see how it works, {product['cta'].lower()}.
"""

with open("script.txt", "w") as f:
    f.write(script.strip())

with open("meta.json", "w") as f:
    json.dump(product, f)
