#!/usr/bin/env python3
"""
Generate graphics/forsaken/units/abomination.png (240x720, 48x48 frames).

Layout matches frameNumbers_5_5_5_5 (same as the ghoul sheet):
  columns: N, NE, E, SE, S (engine mirrors the west-facing ones)
  row 0: still; rows 3,6,9,12: move 0..3; rows 1,4,7,10,13: attack 0..4;
  rows 2,5,8,11,14: death 0..4.

Look: bloated stitched flesh golem, tiny tusked head sunk into the shoulders,
open gut with ribs, cleaver in one hand, meat hook in the other, team-coloured
harness and belt (palette indices 200..207).
"""

import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_forsaken_art import GRAPHICS_DIR, rgba_to_indexed  # noqa: E402

FW = FH = 48

# Muted, sickly undead flesh (darker than v1, closer to the WC1 palette).
FLESH_HI = (168, 162, 140, 255)
FLESH = (126, 120, 102, 255)
FLESH_DK = (86, 80, 70, 255)
FLESH_SH = (50, 46, 42, 255)
STITCH = (44, 30, 34, 255)
GORE = (172, 26, 30, 255)
GORE_DK = (96, 14, 20, 255)
BONE = (236, 232, 214, 255)
STEEL_HI = (214, 216, 224, 255)
STEEL = (150, 152, 164, 255)
STEEL_DK = (86, 88, 100, 255)
WOOD = (96, 64, 40, 255)
EYE = (120, 255, 80, 255)
OUTLINE = (24, 16, 20, 255)
# Team colour is drawn as a pure blue ramp and mapped to palette indices
# 200..207 after the frame has been shrunk (see shrink_and_map_team).
PC = [(40, 40, 255 - i * 26, 255) for i in range(8)]  # light -> dark
SHADOW = (0, 0, 0, 255)
SHRINK = 37  # frames are drawn at 48px and shrunk to this size

FACING = [(0, -1), (0.72, -0.72), (1, 0), (0.72, 0.72), (0, 1)]


class Canvas:
    def __init__(self, px, ox, oy):
        self.px, self.ox, self.oy = px, ox, oy

    def put(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < FW and 0 <= y < FH:
            self.px[self.ox + x, self.oy + y] = c

    def ellipse(self, cx, cy, rx, ry, hi, mid, dk, sh=None):
        for dy in range(-int(ry) - 1, int(ry) + 2):
            for dx in range(-int(rx) - 1, int(rx) + 2):
                d = (dx / rx) ** 2 + (dy / ry) ** 2
                if d > 1.0:
                    continue
                # light from upper-left
                l = (-dx / rx) * 0.6 + (-dy / ry) * 0.8
                if sh is not None and d > 0.78 and l < -0.2:
                    c = sh
                elif l > 0.45:
                    c = hi
                elif l > -0.25:
                    c = mid
                else:
                    c = sh if (sh is not None and l < -0.75) else dk
                self.put(cx + dx, cy + dy, c)

    def line(self, x0, y0, x1, y1, c, thick=1, c_edge=None):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1) * 2)
        for i in range(n + 1):
            t = i / n
            x = x0 + (x1 - x0) * t
            y = y0 + (y1 - y0) * t
            r = thick / 2.0
            for dy in range(-int(r) - 1, int(r) + 2):
                for dx in range(-int(r) - 1, int(r) + 2):
                    if dx * dx + dy * dy <= r * r + 0.25:
                        edge = c_edge is not None and dx + dy >= int(r)
                        self.put(x + dx, y + dy, c_edge if edge else c)


def limb(cv, x0, y0, x1, y1, thick):
    cv.line(x0, y0, x1, y1, FLESH, thick, FLESH_DK)
    cv.line(x0 - 1, y0 - 1, x1 - 1, y1 - 1, FLESH_HI, 1)


def cleaver(cv, hx, hy, ang, bloody=True):
    """Big butcher cleaver held at (hx, hy) pointing along angle ang."""
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx  # blade side
    cv.line(hx - dx * 2, hy - dy * 2, hx + dx * 3, hy + dy * 3, WOOD, 2)
    for i in range(3, 13):
        for j in range(0, 6):
            x = hx + dx * i + nx * j
            y = hy + dy * i + ny * j
            if j == 5:
                c = STEEL_HI
            elif j == 0:
                c = STEEL_DK
            else:
                c = STEEL
            if bloody and i >= 9 and j >= 3:
                c = GORE if (i + j) % 2 else GORE_DK
            cv.put(x, y, c)


def hook(cv, hx, hy, side):
    cv.line(hx, hy, hx, hy + 5, STEEL, 1)
    for k in range(6):
        a = math.pi * k / 5.0
        cv.put(hx + side * (2 - 2 * math.cos(a)), hy + 5 + 2 * math.sin(a), STEEL_HI if k < 3 else STEEL)
    cv.put(hx + side * 4, hy + 4, STEEL_HI)


def body_details(cv, col, cx, cy, rx, ry):
    fx, fy = FACING[col]
    front = fy >= 0 or col == 2
    # stitched seams
    seams = [(-0.55, -0.7, -0.1, 0.8), (0.35, -0.85, 0.65, 0.5)]
    if not front:
        seams.append((-0.8, 0.05, 0.8, 0.05))
    for sx0, sy0, sx1, sy1 in seams:
        x0, y0 = cx + sx0 * rx, cy + sy0 * ry
        x1, y1 = cx + sx1 * rx, cy + sy1 * ry
        n = int(max(abs(x1 - x0), abs(y1 - y0)))
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = y0 + (y1 - y0) * i / n
            cv.put(x, y, STITCH)
            if i % 2 == 0:
                cv.put(x - 1, y, STITCH)
                cv.put(x + 1, y, STITCH)
    # team-coloured belt
    for dx in range(-int(rx) + 1, int(rx)):
        t = abs(dx) / rx
        y = cy + ry * 0.55 + t * t * 1.5
        cv.put(cx + dx, y, PC[2] if dx < 0 else PC[4])
        cv.put(cx + dx, y + 1, PC[5] if dx < 0 else PC[7])
    # ragged team-coloured loincloth hanging from the belt
    for dx in range(-5, 6):
        for dy in range(2, 6 - abs(dx) // 3):
            if (dx + dy) % 3:
                cv.put(cx + dx, cy + ry * 0.55 + dy, PC[3 + (dy + dx) % 4])
    # harness strap over one shoulder
    for i in range(-int(ry * 0.9), int(ry * 0.5)):
        x = cx - i * 0.75 * (1 if front else -1)
        cv.put(x, cy + i, PC[1])
        cv.put(x + 1, cy + i, PC[3])
        cv.put(x + 2, cy + i, PC[6])
    if front:
        # open gut with ribs
        gx = cx + fx * rx * 0.35
        gy = cy + ry * 0.15
        cv.ellipse(gx, gy, 4.2, 3.2, GORE, GORE, GORE_DK)
        for k in (-2, 0, 2):
            cv.put(gx + k, gy - 2, BONE)
            cv.put(gx + k, gy - 1, BONE)
            cv.put(gx + k + 1, gy + 1, GORE_DK)
        cv.put(gx - 1, gy + 3, FLESH_SH)
        cv.put(gx + 2, gy + 3, GORE_DK)


def head(cv, col, hx, hy):
    cv.ellipse(hx, hy + 0.5, 4.6, 4.2, STITCH, STITCH, STITCH)
    cv.ellipse(hx, hy, 3.7, 3.4, FLESH_HI, FLESH, FLESH_DK)
    if col == 0:
        cv.line(hx - 2, hy - 1, hx + 2, hy - 1, STITCH, 1)
        return
    if col == 4:
        cv.put(hx - 1, hy - 1, EYE)
        cv.put(hx + 1, hy - 1, EYE)
        cv.line(hx - 2, hy + 1, hx + 2, hy + 1, GORE_DK, 1)
        cv.put(hx - 2, hy + 2, BONE)
        cv.put(hx + 2, hy + 2, BONE)
    else:
        cv.put(hx + 1, hy - 1, EYE)
        cv.line(hx, hy + 1, hx + 3, hy + 1, GORE_DK, 1)
        cv.put(hx + 3, hy + 2, BONE)
        cv.put(hx + 3, hy + 3, BONE)
    cv.put(hx - 1, hy - 3, STITCH)
    cv.put(hx, hy - 3, STITCH)


def draw_frame(cv, col, anim, step):
    fx, fy = FACING[col]
    if anim == "death":
        draw_death(cv, col, step)
        return

    bob = 0
    stride = 0
    if anim == "move":
        stride = (-2, 0, 2, 0)[step]
        bob = (0, -1, 0, -1)[step]
    elif anim == "attack":
        bob = (0, -1, 0, 1, 0)[step]

    cx, cy = 24 + fx * 1, 25 + bob
    rx, ry = 12, 11

    # side axis in screen space (the unit's left/right)
    sx, sy = -fy, fx
    # weapon arm is the screen-right/near one for side views
    if col == 0:
        near, far = (1, 0), (-1, 0)
    elif col == 4:
        near, far = (-1, 0), (1, 0)
    else:
        near, far = (sx, sy), (-sx, -sy)

    def shoulder(side):
        return cx + side[0] * 10, cy - 5 + side[1] * 4

    # dark ground shadow (WC1 units have no outline, just a shadow blob)
    cv.ellipse(cx + 2, cy + 16, 11, 3, SHADOW, SHADOW, SHADOW)

    # legs
    for k, side in enumerate((far, near)):
        lx = cx + side[0] * 5 - fx * 1
        ly = cy + 8 + side[1] * 2
        off = stride if k else -stride
        foot = (lx + fx * off, ly + 7 + fy * off * 0.5)
        cv.line(lx, ly, foot[0], foot[1], FLESH_DK, 5, FLESH_SH)
        cv.line(foot[0] - 2, foot[1] + 1, foot[0] + 2 + fx, foot[1] + 1, FLESH_SH, 2)

    # far arm with meat hook (behind the body for side views)
    fsx, fsy = shoulder(far)
    swing = -stride if anim == "move" else 0
    fhx = fsx + far[0] * 3 + fx * (3 + swing)
    fhy = fsy + 11 + fy * 2
    far_behind = col in (1, 2, 3) or col == 0
    if far_behind:
        limb(cv, fsx, fsy, fhx, fhy, 4)
        hook(cv, fhx, fhy + 1, 1 if far[0] >= 0 else -1)

    # body
    cv.ellipse(cx, cy, rx, ry, FLESH_HI, FLESH, FLESH_DK, FLESH_SH)
    body_details(cv, col, cx, cy, rx, ry)

    # head sits low between the shoulders, pushed toward the facing
    hx = cx + fx * 6
    hy = cy - 9 + fy * 3
    if col == 0:
        hy = cy - 10
    head(cv, col, hx, hy)

    if not far_behind:
        limb(cv, fsx, fsy, fhx, fhy, 4)
        hook(cv, fhx, fhy + 1, 1 if far[0] >= 0 else -1)

    # near arm with cleaver
    nsx, nsy = shoulder(near)
    base_ang = math.atan2(fy, fx) if col != 0 else -math.pi / 2
    if anim == "attack":
        lift = (0.2, 1.0, 0.1, -0.5, -0.2)[step]
        reach = (3, 1, 6, 9, 5)[step]
        hxn = nsx + fx * reach + near[0] * 2
        hyn = nsy + 9 - lift * 15 + fy * reach * 0.6
        ang = base_ang - math.pi / 2 * lift - (0.6 if step == 3 else 0)
        if col == 4 or col == 0:
            ang = -math.pi / 2 * lift + (math.pi / 2 if col == 4 else -math.pi / 2)
    else:
        hxn = nsx + near[0] * 3 + fx * (3 + stride)
        hyn = nsy + 11 + fy * 2
        ang = math.pi / 2 + (0.35 * (1 if near[0] >= 0 else -1))
    if col == 0 and anim != "attack":
        # seen from behind: blade hangs mostly hidden by the arm
        cleaver(cv, hxn, hyn, ang, bloody=False)
        limb(cv, nsx, nsy, hxn, hyn, 4)
    else:
        limb(cv, nsx, nsy, hxn, hyn, 4)
        cleaver(cv, hxn, hyn, ang)
    # slash trail
    if anim == "attack" and step == 3:
        for i in range(-5, 6):
            cv.put(hxn + fx * 10 - abs(i) * 0.3 * (1 if fx >= 0 else -1) + (i if fx == 0 else 0),
                   hyn + fy * 6 + (i if fx != 0 else 0), STEEL_HI)


def draw_death(cv, col, step):
    fx, fy = FACING[col]
    cx, cy = 24, 28
    if step == 0:
        cv.ellipse(cx - fx * 2, cy - 2, 12, 10, FLESH_HI, FLESH, FLESH_DK, FLESH_SH)
        body_details(cv, col, cx - fx * 2, cy - 2, 12, 10)
        head(cv, col, cx + fx * 3, cy - 10)
        cleaver(cv, cx + 12, cy + 4, 0.4)
        return
    flat = min(step, 3)
    rx = 11 + flat
    ry = 8 - flat * 1.5
    # small blood pool seeping out from under the body
    cv.ellipse(cx + 2, cy + 4, 6 + step * 1.5, 2 + step * 0.5, GORE_DK, GORE, GORE_DK)
    if step <= 3:
        cv.ellipse(cx, cy, rx, ry, FLESH_HI, FLESH, FLESH_DK, FLESH_SH)
        for i in range(-int(rx) + 3, int(rx) - 2, 3):
            cv.put(cx + i, cy - 1, STITCH)
            cv.put(cx + i, cy, STITCH)
        cv.ellipse(cx + 2, cy, 4, max(1.5, ry * 0.5), GORE, GORE, GORE_DK)
        for k in (-2, 0, 2):
            cv.put(cx + 2 + k, cy - 1, BONE)
        for dx in range(-int(rx) + 2, int(rx) - 1):
            cv.put(cx + dx, cy + ry * 0.6, PC[4])
    else:
        # bones and scraps left in the blood
        for bx, by in ((-6, -1), (-2, 1), (3, -2), (7, 1), (0, 3)):
            cv.line(cx + bx - 2, cy + by, cx + bx + 2, cy + by + 1, BONE, 1)
        cv.ellipse(cx - 1, cy, 4, 2, FLESH, FLESH_DK, FLESH_SH)
    cleaver(cv, cx + rx - 1, cy + 3, 0.2, bloody=True)
    hook(cv, cx - rx, cy, -1)


def outline(rgba):
    w, h = rgba.size
    src = rgba.copy().load()
    px = rgba.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] >= 128:
                continue
            fx0, fy0 = (x // FW) * FW, (y // FH) * FH
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if fx0 <= nx < fx0 + FW and fy0 <= ny < fy0 + FH and src[nx, ny][3] >= 128:
                    px[x, y] = OUTLINE
                    break


def shrink_and_map_team(rgba):
    """Shrink every frame with resampling (gives the gritty, mixed-pixel look
    of the WC1 sprites), then snap blue pixels back onto the team ramp."""
    out = Image.new("RGBA", rgba.size, (0, 0, 0, 0))
    off_x = (FW - SHRINK) // 2
    off_y = FH - SHRINK - 3
    for fy in range(0, rgba.height, FH):
        for fx in range(0, rgba.width, FW):
            fr = rgba.crop((fx, fy, fx + FW, fy + FH)).resize((SHRINK, SHRINK), Image.LANCZOS)
            px = fr.load()
            for y in range(SHRINK):
                for x in range(SHRINK):
                    r, g, b, a = px[x, y]
                    if a < 140:
                        px[x, y] = (0, 0, 0, 0)
                        continue
                    if b > r + 60 and b > g + 60:
                        k = max(0, min(7, int((255 - b) / 26)))
                        px[x, y] = (254, 0, 200 + k, 255)
                    else:
                        px[x, y] = (r, g, b, 255)
            out.paste(fr, (fx + off_x, fy + off_y))
    return out


def main():
    pal = Image.open(os.path.join(GRAPHICS_DIR, "orc", "units", "grunt.png")).getpalette()
    dst = os.path.join(GRAPHICS_DIR, "forsaken", "units", "abomination.png")
    rgba = Image.new("RGBA", (5 * FW, 15 * FH), (0, 0, 0, 0))
    px = rgba.load()
    move = {3: 0, 6: 1, 9: 2, 12: 3}
    attack = {1: 0, 4: 1, 7: 2, 10: 3, 13: 4}
    for r in range(15):
        if r == 0:
            anim, step = "still", 0
        elif r in move:
            anim, step = "move", move[r]
        elif r in attack:
            anim, step = "attack", attack[r]
        else:
            anim, step = "death", (r - 2) // 3
        for c in range(5):
            draw_frame(Canvas(px, c * FW, r * FH), c, anim, step)
    rgba = shrink_and_map_team(rgba)
    out = rgba_to_indexed(rgba, pal)
    out.save(dst if len(sys.argv) < 2 else sys.argv[1])
    print("wrote", dst if len(sys.argv) < 2 else sys.argv[1])


if __name__ == "__main__":
    main()
