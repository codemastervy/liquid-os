#!/usr/bin/env python3
"""Procedurally paint a 'liquid glass' wallpaper: soft, blurred, translucent
colour blobs over a deep gradient background -- the glassmorphism look used
throughout the Liquid OS theme. Regenerated on every build so the desktop,
GRUB background, and Plymouth splash all share the same artwork.
"""
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 3840, 2160

TOP_COLOR = (10, 12, 26)
BOTTOM_COLOR = (28, 16, 48)

BLOB_PALETTE = [
    (120, 170, 255, 130),
    (255, 140, 200, 110),
    (140, 255, 220, 100),
    (200, 150, 255, 120),
    (255, 200, 140, 90),
]


def lerp(a, b, t):
    return a + (b - a) * t


def make_gradient_background():
    column = Image.new("RGB", (1, HEIGHT))
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        column.putpixel(
            (0, y),
            tuple(int(lerp(TOP_COLOR[i], BOTTOM_COLOR[i], t)) for i in range(3)),
        )
    return column.resize((WIDTH, HEIGHT), Image.BILINEAR).convert("RGBA")


def add_blob(layer, cx, cy, r, color):
    # Give the circle generous transparent padding before blurring it, so the
    # blur has room to feather off into nothing instead of flattening into a
    # uniform-alpha square the moment the blur radius approaches the canvas
    # size.
    canvas = int(r * 2.6)
    margin = canvas * 0.32
    blob = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(blob)
    draw.ellipse((margin, margin, canvas - margin, canvas - margin), fill=color)
    blob = blob.filter(ImageFilter.GaussianBlur(r * 0.22))
    layer.alpha_composite(blob, (int(cx - canvas / 2), int(cy - canvas / 2)))


def main(out_path):
    random.seed(7)
    background = make_gradient_background()
    blobs = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

    for _ in range(9):
        color = random.choice(BLOB_PALETTE)
        radius = random.randint(int(WIDTH * 0.12), int(WIDTH * 0.22))
        cx = random.randint(0, WIDTH)
        cy = random.randint(0, HEIGHT)
        add_blob(blobs, cx, cy, radius, color)

    combined = Image.alpha_composite(background, blobs)
    combined = combined.filter(ImageFilter.GaussianBlur(2))
    combined.convert("RGB").save(out_path, "PNG")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "wallpaper.png")
