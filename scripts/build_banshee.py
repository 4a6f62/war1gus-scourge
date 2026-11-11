#!/usr/bin/env python3
"""
Generate graphics/forsaken/units/banshee.png (160x416, 32x32 frames), drawn
from scratch in the gritty WC1 style of the ghoul / abomination sheets.

Layout (frameNumbers_5_5_4_4, columns N, NE, E, SE, S):
  row 0: still; rows 3,6,9,12: move 0..3; rows 1,4,7,10: attack 0..3
  (also used for spell casting); rows 2,5,8,11: death 0..3.

Look: floating wraith without legs, wispy tail, hooded pale glowing face,
long dark hair streaming behind, robes in team colour (indices 200..207).
Frames are drawn on a 48px canvas and shrunk to 30px, like build_abomination.
"""

import math
import os
import random
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_forsaken_art import GRAPHICS_DIR, rgba_to_indexed  # noqa: E402

FRAME = 32
CANVAS = 48
SHRINK = 26

SKIN_HI = (236, 232, 248, 255)
SKIN = (188, 182, 210, 255)
SKIN_DK = (120, 112, 150, 255)
HAIR_HI = (150, 140, 180, 255)
HAIR = (84, 74, 108, 255)
HAIR_DK = (40, 34, 54, 255)
MOUTH = (20, 10, 30, 255)
EYE = (255, 255, 255, 255)
GLOW = (220, 230, 255, 255)
SHADOW = (0, 0, 0, 255)
# team colour drawn as a pure blue ramp, snapped to 200..207 after shrinking
PC = [(40, 40, 255 - i * 26, 255) for i in range(8)]

FACING = [(0, -1), (0.72, -0.72), (1, 0), (0.72, 0.72), (0, 1)]


class Canvas:
    def __init__(self):
        self.im = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
        self.px = self.im.load()

    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < CANVAS and 0 <= y < CANVAS:
            self.px[x, y] = c

    def ellipse(self, cx, cy, rx, ry, cols, keep=None):
        """cols: light..dark list; shaded with light from the upper left."""
        for dy in range(-int(ry) - 1, int(ry) + 2):
            for dx in range(-int(rx) - 1, int(rx) + 2):
                if rx <= 0 or ry <= 0:
                    continue
                if (dx / rx) ** 2 + (dy / ry) ** 2 > 1.0:
                    continue
                if keep is not None and not keep(dx, dy):
                    continue
                l = (-dx / rx) * 0.6 + (-dy / ry) * 0.8  # -1.4 .. 1.4
                i = int((1.4 - l) / 2.8 * len(cols))
                self.put(cx + dx, cy + dy, cols[max(0, min(len(cols) - 1, i))])

    def line(self, x0, y0, x1, y1, c, thick=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1) * 2)
        r = thick / 2.0
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            for dy in range(-int(r) - 1, int(r) + 2):
                for dx in range(-int(r) - 1, int(r) + 2):
                    if dx * dx + dy * dy <= r * r + 0.25:
                        self.put(x + dx, y + dy, c)


ROBE = [PC[0], PC[2], PC[4], PC[6], PC[7]]
ROBE_DARK = [PC[4], PC[6], PC[7]]


def draw_tail(cv, cx, top, length, width, sway, phase):
    """Wispy ghost tail tapering down from the robe."""
    for i in range(length):
        t = i / float(length)
        w = width * (1 - t) ** 1.2
        x = cx + math.sin(t * 3.2 + phase) * sway * t
        y = top + i
        cv.ellipse(x, y, max(0.6, w), 1.2, ROBE_DARK if i % 3 else ROBE)
    # loose wisps at the end
    end_x = cx + math.sin(3.2 + phase) * sway
    for k in (-2, 0, 2):
        cv.line(end_x + k * 0.6, top + length - 2, end_x + k * 1.5, top + length + 2, PC[6], 1)


def draw_hair(cv, hx, hy, fx, fy, flow, col):
    """Long hair streaming backwards / outwards from the head."""
    back_x, back_y = -fx, -fy
    if col in (0, 4):  # front / back view: a wild mane flaring to both sides
        dirs = [(-1, 0.1), (1, 0.1), (-0.85, -0.6), (0.85, -0.6), (-0.3, -1.0), (0.3, -1.0),
                (-0.9, 0.7), (0.9, 0.7)]
    else:
        dirs = [(back_x, back_y - 0.7), (back_x, back_y - 0.2), (back_x * 0.9, back_y + 0.5),
                (back_x * 0.5, -1.0), (back_x, back_y + 0.9), (back_x * 0.2, -1.0),
                (back_x * 0.9, back_y + 0.1)]
    for n, (dx, dy) in enumerate(dirs):
        ln = 12 + (n % 3) * 3
        x, y = hx, hy - 1
        for i in range(ln):
            t = i / float(ln)
            wav = math.sin(t * 5 + flow + n) * 1.4
            x += dx * 0.95 + (-dy) * wav * 0.3
            y += dy * 0.95 + dx * wav * 0.3
            thick = 3 if t < 0.45 else (2 if t < 0.8 else 1)
            for ox in range(thick):
                for oy in range(thick):
                    c = HAIR_HI if (ox + oy == 0 and i % 3 != 2) else (HAIR_DK if ox + oy >= 2 else HAIR)
                    cv.put(x + ox - thick // 2, y + oy - thick // 2, c)


def draw_head(cv, col, hx, hy, wail):
    # hood
    cv.ellipse(hx, hy - 0.5, 4.6, 4.8, [PC[2], PC[4], PC[6], PC[7]])
    if col == 0:
        return
    fx = FACING[col][0]
    face_x = hx + fx * 1.2
    cv.ellipse(face_x, hy + 0.5, 3.4, 3.8, [SKIN_HI, SKIN_HI, SKIN, SKIN_DK])
    # hollow glowing eyes and a wailing mouth
    if col == 4:
        cv.put(face_x - 1, hy, MOUTH)
        cv.put(face_x + 1, hy, MOUTH)
        cv.put(face_x - 1, hy - 1, EYE)
        cv.put(face_x + 1, hy - 1, EYE)
        cv.ellipse(face_x, hy + 2.3, 0.9, 0.6 + wail * 0.9, [MOUTH])
    else:
        cv.put(face_x + 1, hy - 1, EYE)
        cv.put(face_x + 1, hy, MOUTH)
        cv.ellipse(face_x + 1.2, hy + 2.2, 0.7, 0.5 + wail * 0.8, [MOUTH])


def draw_arm(cv, sx, sy, hx, hy):
    cv.line(sx, sy, hx, hy, PC[4], 3)
    cv.line(sx, sy - 1, hx, hy - 1, PC[2], 1)
    # long bony fingers
    cv.put(hx, hy, SKIN)
    cv.put(hx + 0.8, hy + 0.8, SKIN_HI)
    cv.put(hx - 0.8, hy + 0.8, SKIN_DK)


def draw_frame(cv, col, anim, step):
    fx, fy = FACING[col]
    if anim == "death":
        draw_death(cv, col, step)
        return

    bob = [0, -1, -2, -1][step % 4] if anim in ("still", "move") else [0, -1, -1, 0][step % 4]
    if anim == "still":
        bob = 0
    cx = 24 + fx * 1.0
    cy = 20 + bob
    flow = step * 1.3

    # faint ground shadow well below the floating body
    cv.ellipse(cx, 37, 5, 1.6, [SHADOW])

    sway = 3 + (step % 2)
    draw_tail(cv, cx - fx * 1.5, cy + 6, 13, 5.5, sway * (-1 if fx > 0 else 1), flow)

    hx = cx + fx * 2
    hy = cy - 8 + fy * 1

    side = (-fy, fx) if col not in (0, 4) else (1, 0)
    sh_l = (cx - side[0] * 5, cy - 4 - side[1] * 2)
    sh_r = (cx + side[0] * 5, cy - 4 + side[1] * 2)

    if anim == "attack":
        reach = [3, 7, 9, 5][step]
        lift = [2, 4, 3, 1][step]
        hand_l = (sh_l[0] + fx * reach - side[0], sh_l[1] - lift + fy * reach * 0.6)
        hand_r = (sh_r[0] + fx * reach + side[0], sh_r[1] - lift + fy * reach * 0.6)
        if col in (0, 4):
            hand_l = (sh_l[0] - 3, sh_l[1] - lift - (reach if col == 0 else -reach * 0.5))
            hand_r = (sh_r[0] + 3, sh_r[1] - lift - (reach if col == 0 else -reach * 0.5))
    else:
        drift = math.sin(flow) * 1.0
        hand_l = (sh_l[0] - side[0] * 3 + fx * 2, sh_l[1] + 7 + drift)
        hand_r = (sh_r[0] + side[0] * 3 + fx * 2, sh_r[1] + 7 - drift)

    far_first = col in (1, 2, 3)
    if far_first:
        draw_arm(cv, sh_l[0], sh_l[1], hand_l[0], hand_l[1])

    draw_hair(cv, hx, hy, fx, fy, flow, col)
    # robed torso
    cv.ellipse(cx, cy, 6, 7.5, ROBE)
    # ragged hem
    for dx in range(-6, 7):
        if (dx + step) % 3 == 0:
            cv.line(cx + dx, cy + 5, cx + dx * 1.1, cy + 8, PC[6], 1)
    draw_head(cv, col, hx, hy, 1 if anim == "attack" and step in (1, 2) else 0)
    if col == 0:
        draw_hair(cv, hx, hy, fx, fy, flow, col)

    if not far_first:
        draw_arm(cv, sh_l[0], sh_l[1], hand_l[0], hand_l[1])
    draw_arm(cv, sh_r[0], sh_r[1], hand_r[0], hand_r[1])

    if anim == "attack" and step in (1, 2):
        ox = (hand_l[0] + hand_r[0]) / 2 + fx * 3
        oy = (hand_l[1] + hand_r[1]) / 2 + fy * 2
        r = 2.2 + step * 0.6
        cv.ellipse(ox, oy, r, r, [GLOW, SKIN_HI, SKIN])


def draw_death(cv, col, step):
    """Dissolves upward into wisps."""
    rnd = random.Random(1000 + col * 10 + step)
    tmp = Canvas()
    draw_frame(tmp, col, "still", 0)
    keep = [0.85, 0.6, 0.35, 0.12][step]
    rise = step * 3
    for y in range(CANVAS):
        for x in range(CANVAS):
            c = tmp.px[x, y]
            if c[3] == 0 or c == SHADOW:
                continue
            if rnd.random() < keep:
                ny = y - rise - (rnd.random() * step * 2)
                nx = x + rnd.uniform(-step, step)
                cv.put(nx, ny, c if step < 2 else (SKIN if rnd.random() < 0.4 else c))
    if step < 2:
        cv.ellipse(24, 37, 5 - step * 2, 1.6, [SHADOW])


def shrink_and_map_team(frame_img):
    fr = frame_img.resize((SHRINK, SHRINK), Image.LANCZOS)
    px = fr.load()
    for y in range(SHRINK):
        for x in range(SHRINK):
            r, g, b, a = px[x, y]
            if a < 140:
                px[x, y] = (0, 0, 0, 0)
            elif b > r + 60 and b > g + 60:
                k = max(0, min(7, int((255 - b) / 26)))
                px[x, y] = (254, 0, 200 + k, 255)
            else:
                px[x, y] = (r, g, b, 255)
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    out.paste(fr, ((FRAME - SHRINK) // 2, FRAME - SHRINK - 1))
    return out


def main():
    pal = Image.open(os.path.join(GRAPHICS_DIR, "orc", "units", "grunt.png")).getpalette()
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GRAPHICS_DIR, "forsaken", "units", "banshee.png")
    sheet = Image.new("RGBA", (5 * FRAME, 13 * FRAME), (0, 0, 0, 0))
    move = {3: 0, 6: 1, 9: 2, 12: 3}
    attack = {1: 0, 4: 1, 7: 2, 10: 3}
    death = {2: 0, 5: 1, 8: 2, 11: 3}
    for r in range(13):
        if r == 0:
            anim, step = "still", 0
        elif r in move:
            anim, step = "move", move[r]
        elif r in attack:
            anim, step = "attack", attack[r]
        else:
            anim, step = "death", death[r]
        for c in range(5):
            cv = Canvas()
            draw_frame(cv, c, anim, step)
            sheet.paste(shrink_and_map_team(cv.im), (c * FRAME, r * FRAME))
    rgba_to_indexed(sheet, pal).save(dst)
    print("wrote", dst)


if __name__ == "__main__":
    main()
