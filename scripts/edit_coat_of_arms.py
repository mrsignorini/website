#!/usr/bin/env python3
"""
Replace the blue heraldic shield in signoriniorigens.png with a vintage
ship's steering wheel using OpenAI image inpainting.

Usage:
    OPENAI_API_KEY=sk-... python3 scripts/edit_coat_of_arms.py

Adjust MASK_BOX if the shield boundary needs tuning after first run.
"""

import io
import os
import shutil
import sys
from pathlib import Path

from PIL import Image

ASSETS = Path(__file__).parent.parent / "assets"
ORIGINAL = ASSETS / "signoriniorigens.png"
BACKUP = ASSETS / "signoriniorigens_original.png"
OUTPUT = ASSETS / "signoriniorigens.png"

# Approximate bounding box of the blue shield (x1, y1, x2, y2) in 896×944 px
MASK_BOX = (270, 200, 620, 720)

PROMPT = (
    "A large antique wooden ship's steering wheel (helm) with eight spokes "
    "radiating from a central brass hub, rendered in a classic heraldic "
    "engraving style, warm wood tones and gold fittings, on a neutral "
    "parchment-white background, centered and perfectly symmetrical, "
    "no text, no border"
)


def make_mask(original_size: tuple[int, int]) -> Image.Image:
    """RGBA mask: transparent (alpha=0) where we want AI to paint, opaque elsewhere."""
    w, h = original_size
    mask = Image.new("RGBA", (w, h), (0, 0, 0, 255))  # fully opaque black = keep
    x1, y1, x2, y2 = MASK_BOX
    # Transparent region = area to fill
    for y in range(y1, y2):
        for x in range(x1, x2):
            mask.putpixel((x, y), (0, 0, 0, 0))
    return mask


def png_bytes(img: Image.Image) -> bytes:
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    print(f"Loading {ORIGINAL} …")
    img = Image.open(ORIGINAL).convert("RGBA")
    orig_size = img.size  # (896, 944)
    print(f"  size: {orig_size}")

    # Back up original before overwriting
    if not BACKUP.exists():
        shutil.copy(ORIGINAL, BACKUP)
        print(f"  backup saved → {BACKUP.name}")

    print("Building mask …")
    mask = make_mask(orig_size)

    # OpenAI edit API requires 1024×1024 square RGBA PNGs
    target = 1024
    img_sq = img.resize((target, target), Image.LANCZOS)
    mask_sq = mask.resize((target, target), Image.NEAREST)

    print("Calling OpenAI image edit API …")
    try:
        response = client.images.edit(
            model="dall-e-2",
            image=("image.png", png_bytes(img_sq), "image/png"),
            mask=("mask.png", png_bytes(mask_sq), "image/png"),
            prompt=PROMPT,
            n=1,
            size="1024x1024",
            response_format="url",
        )
    except Exception as exc:
        print(f"API call failed: {exc}", file=sys.stderr)
        sys.exit(1)

    url = response.data[0].url
    print(f"  result URL: {url}")

    import urllib.request
    print("Downloading result …")
    with urllib.request.urlopen(url) as resp:
        result_bytes = resp.read()

    result = Image.open(io.BytesIO(result_bytes)).convert("RGBA")
    # Resize back to original dimensions
    result = result.resize(orig_size, Image.LANCZOS)

    result.convert("RGB").save(OUTPUT, format="PNG")
    print(f"Saved → {OUTPUT}")
    print("Done. Review the image and re-run after adjusting MASK_BOX if needed.")


if __name__ == "__main__":
    main()
