#!/usr/bin/env python3
"""Generate the 27x19 Scourge spell icons: icon-death-coil and icon-possession."""

import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_forsaken_art import CONTRIB_DIR, get_palette_matcher  # noqa: E402

W, H = 27, 19
ICON_DIR = os.path.join(CONTRIB_DIR, "ui", "forsaken")


def lerp(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def background(c_center, c_edge):
    im = Image.new("RGB", (W, H))
    px = im.load()
    for y in range(H):
        for x in range(W):
            d = math.hypot((x - 13) / 14.0, (y - 9) / 10.0)
            px[x, y] = lerp(c_center, c_edge, min(1.0, d))
    return im, px


def death_coil():
    im, px = background((26, 40, 30), (6, 10, 8))
    # glowing green spiral
    for i in range(170):
        t = i / 170.0
        a = t * math.pi * 3.2
        r = 1.5 + t * 8.5
        x = 12 - math.cos(a) * r * 1.0
        y = 10 + math.sin(a) * r * 0.85
        c = lerp((30, 100, 30), (110, 220, 80), t)
        for dx, dy in ((0, 0), (1, 0)):
            xi, yi = int(round(x + dx)), int(round(y + dy))
            if 0 <= xi < W and 0 <= yi < H:
                px[xi, yi] = c
    # skull riding the end of the coil
    a = math.pi * 3.2
    sx = int(round(12 - math.cos(a) * 10 * 1.0))
    sy = max(4, int(round(10 + math.sin(a) * 10 * 0.85)))
    for y in range(-3, 4):
        for x in range(-3, 4):
            if (x / 3.4) ** 2 + (y / 3.2) ** 2 <= 1:
                px[sx + x, sy + y] = (226, 226, 200) if x + y < 1 else (160, 160, 136)
    for x, y in ((-1, 0), (1, 0)):
        px[sx + x, sy + y] = (120, 255, 60)
    px[sx, sy + 2] = (40, 40, 30)
    px[sx - 1, sy + 3] = (200, 200, 180)
    px[sx + 1, sy + 3] = (200, 200, 180)
    return im


def possession():
    im, px = background((96, 52, 128), (22, 10, 34))
    # wispy banshee: pale face, flowing hair, tail curling down-right
    cx, cy = 10, 7
    for i in range(80):
        t = i / 80.0
        x = cx + 2 + t * 14 + math.sin(t * 9) * 1.5
        y = cy + 3 + t * 8
        c = lerp((200, 200, 230), (70, 50, 110), t)
        for w in range(-int(3 * (1 - t)), int(3 * (1 - t)) + 1):
            xi, yi = int(round(x)), int(round(y + w * 0.6))
            if 0 <= xi < W and 0 <= yi < H:
                px[xi, yi] = c
    for y in range(-4, 5):
        for x in range(-3, 4):
            if (x / 3.3) ** 2 + (y / 4.2) ** 2 <= 1:
                px[cx + x, cy + y] = (232, 232, 248) if x < 1 else (176, 176, 212)
    # hollow wailing face
    px[cx - 1, cy - 1] = (20, 10, 30)
    px[cx + 1, cy - 1] = (20, 10, 30)
    px[cx, cy + 2] = (20, 10, 30)
    px[cx, cy + 3] = (60, 30, 80)
    # hair streaming back
    for k in range(4):
        for j in range(7 - k):
            x, y = cx - 3 - j, cy - 3 + k * 2 + j // 3
            if 0 <= x < W and 0 <= y < H:
                px[x, y] = (200, 200, 236) if k % 2 == 0 else (150, 140, 200)
    # reaching claw toward a team-coloured victim marker (top right)
    for i in range(7):
        px[cx + 3 + i, cy - 1 - i // 2] = (200, 200, 230)
    for f in range(3):
        px[cx + 10 + f, cy - 5 + f] = (240, 240, 255)
    return im


def save(im, name, pal):
    find = get_palette_matcher(pal)
    out = Image.new("P", (W, H))
    out.putpalette(pal)
    src, dst = im.load(), out.load()
    for y in range(H):
        for x in range(W):
            dst[x, y] = find(src[x, y])
    path = os.path.join(ICON_DIR, name + ".png")
    out.save(path)
    print("wrote", path)


def main():
    pal = Image.open(os.path.join(ICON_DIR, "icon-banshee.png")).getpalette()
    save(death_coil(), "icon-death-coil", pal)
    save(possession(), "icon-possession", pal)


if __name__ == "__main__":
    main()
