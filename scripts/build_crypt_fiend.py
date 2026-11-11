#!/usr/bin/env python3
"""
Generate graphics/forsaken/units/crypt_fiend.png (160x448, 32x32 frames),
drawn from scratch in the gritty WC1 style of the ghoul / abomination sheets.

Layout (frameNumbers_5_5_4_5, columns N, NE, E, SE, S):
  row 0: still; rows 3,6,9,12: move 0..3; rows 1,4,7,10: attack 0..3;
  rows 2,5,8,11,13: death 0..4.

Look: low spider body with a dark carapace and team-coloured plates, eight
bone-white segmented legs, a hunched raised head with glowing eyes. Attack:
rears up and spits web. Death: legs curl up like a dead spider.
"""

import math
import os
import sys

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_forsaken_art import GRAPHICS_DIR, rgba_to_indexed  # noqa: E402
from build_banshee import Canvas, PC, SHADOW, CANVAS  # noqa: E402

FRAME = 32
SHRINK = 30

SHELL = [(104, 98, 120, 255), (70, 64, 84, 255), (46, 42, 58, 255), (26, 24, 34, 255)]
BONE = (226, 220, 200, 255)
BONE_MID = (172, 164, 146, 255)
BONE_DK = (104, 98, 88, 255)
EYE = (150, 255, 90, 255)
GLOW = (190, 255, 150, 255)
WEB = (236, 236, 236, 255)
GOO = (90, 150, 40, 255)
GOO_DK = (50, 90, 24, 255)

FACING = [(0, -1), (0.72, -0.72), (1, 0), (0.72, 0.72), (0, 1)]


def leg(cv, ax, ay, kx, ky, fx_, fy_):
    """Segmented bone leg: attachment -> raised knee -> foot."""
    cv.line(ax, ay, kx, ky, BONE_DK, 1.6)
    cv.line(ax, ay - 0.6, kx, ky - 0.6, BONE_MID, 1)
    cv.line(kx, ky, fx_, fy_, BONE_MID, 1)
    cv.put(kx - 0.5, ky - 1, BONE)
    cv.put(kx, ky, BONE_DK)  # joint
    cv.put(fx_, fy_ + 1, BONE_DK)  # claw tip


def draw_frame(cv, col, anim, step):
    fx, fy = FACING[col]
    if anim == "death":
        draw_death(cv, col, step)
        return

    cx, cy = 24, 26
    rear = 0      # how far the front end lifts (attack)
    stride = 0
    bob = 0
    if anim == "move":
        # alternating tetrapod gait: one set of four legs swings while lifted
        stride = (-5, 0, 5, 0)[step]
        bob = (0, -1, 0, -1)[step]
    elif anim == "attack":
        rear = (2, 5, 4, 1)[step]

    # body axis (screen space; north/south views are foreshortened)
    ax, ay = fx, fy * 0.75
    side = (-fy, fx) if col not in (0, 4) else (1, 0)

    cy += bob
    abdomen = (cx - ax * 6, cy - ay * 6)
    thorax = (cx + ax * 1, cy + ay * 1 - rear * 0.5)
    head = (cx + ax * 6, cy + ay * 6 - 3 - rear)

    cv.ellipse(cx, cy + 6 - bob, 13, 4, [SHADOW])

    # legs: 4 per side, attached along the thorax
    legs = []
    for s in (-1, 1):
        for i, along in enumerate((2.5, 0.8, -0.8, -2.5)):
            group = (i + (s > 0)) % 2
            phase = stride if group else -stride
            lifted = anim == "move" and ((step == 1 and group) or (step == 3 and not group))
            bx = thorax[0] + ax * along + side[0] * s * 2
            by = thorax[1] + ay * along + side[1] * s * 1.5
            spread = 1.0 + 0.35 * abs(along)
            kx = bx + side[0] * s * 6.5 * spread + ax * along * 1.5 + ax * phase * 0.5
            ky = by + side[1] * s * 5 * spread + ay * along * 1.5 - 5
            tx = bx + side[0] * s * 9.5 * spread + ax * along * 3 + ax * phase
            ty = by + side[1] * s * 8 * spread + ay * along * 3 + 3 + ay * phase * 0.8
            if lifted:  # swinging legs come off the ground, knee high
                ky -= 3
                ty -= 3.5
            if anim == "attack" and i == 0:  # front legs lift up when rearing
                ky -= rear * 1.5
                ty -= rear * 2.5
                tx += ax * rear
            legs.append((ty, bx, by, kx, ky, tx, ty))
    legs.sort()
    far = [l for l in legs if l[0] < cy + 1]
    near = [l for l in legs if l[0] >= cy + 1]
    for _, bx, by, kx, ky, tx, ty in far + near:
        if (bx, by) in [(l[1], l[2]) for l in near] and anim == "attack":
            continue
        leg(cv, bx, by, kx, ky, tx, ty)

    # abdomen with team-coloured plates
    cv.ellipse(abdomen[0], abdomen[1], 9, 7, SHELL)
    for k in (-3, 0, 3):
        px_ = abdomen[0] + ax * k * 0.8
        py_ = abdomen[1] + ay * k * 0.8 - 1
        cv.ellipse(px_, py_, 3.6 if col in (0, 4) else 2.8, 1.8, [PC[1], PC[3], PC[5]])
    # spine ridge
    cv.line(abdomen[0] - ax * 6, abdomen[1] - ay * 6 - 2, thorax[0], thorax[1] - 3, BONE_DK, 1)

    # thorax and hunched head
    cv.ellipse(thorax[0], thorax[1], 5.5, 5, SHELL)
    cv.ellipse(head[0], head[1], 4.2, 4, [SHELL[0], SHELL[1], SHELL[2]])
    # mandibles and eyes
    if col != 0:
        mx, my = head[0] + ax * 3, head[1] + 2
        cv.line(mx - side[0] * 1.5, my, mx - side[0] * 1.5 + ax * 2, my + 2, BONE, 1)
        cv.line(mx + side[0] * 1.5, my, mx + side[0] * 1.5 + ax * 2, my + 2, BONE, 1)
        if col == 4:
            for ex in (-1.5, 1.5):
                cv.put(head[0] + ex, head[1], EYE)
                cv.put(head[0] + ex, head[1] - 1, GLOW)
        else:
            cv.put(head[0] + ax * 2, head[1] - 0.5, EYE)
            cv.put(head[0] + ax * 1, head[1] - 1, GLOW)
    # back spikes (bony crest)
    for k, h in ((-1, 3), (1, 2)):
        sx_ = thorax[0] - ax * k
        sy_ = thorax[1] - ay * k - 3
        cv.line(sx_, sy_, sx_ - ax * 1, sy_ - h, BONE, 1)

    if anim == "attack":  # raised front legs stay in front of the body
        for _, bx, by, kx, ky, tx, ty in near:
            leg(cv, bx, by, kx, ky, tx, ty)

    # web spit
    if anim == "attack" and step in (2, 3):
        dist = 6 if step == 2 else 11
        wx = head[0] + ax * dist
        wy = head[1] + ay * dist + 1
        cv.ellipse(wx, wy, 2.2, 1.8, [WEB, WEB, BONE_MID])
        cv.line(head[0] + ax * 3, head[1] + 1, wx, wy, WEB, 1)


def draw_death(cv, col, step):
    fx, fy = FACING[col]
    ax, ay = fx, fy * 0.75
    cx, cy = 24, 27
    curl = (0.15, 0.4, 0.65, 0.85, 1.0)[step]
    # goo spreading
    if step >= 1:
        cv.ellipse(cx, cy + 3, 4 + step * 2, 1.5 + step * 0.6, [GOO, GOO, GOO_DK])
    # legs folding up over the body, like a dead spider
    for s in (-1, 1):
        for i, along in enumerate((2.5, 0.8, -0.8, -2.5)):
            bx = cx + ax * along + s * 3
            by = cy + ay * along
            out = 10 * (1 - curl) + 3
            kx = bx + s * out * 0.6
            ky = by - 4 - curl * 4
            tx = bx + s * out * (1 - curl) * 0.9 - s * curl * 3
            ty = by - 2 - curl * 6 + along
            leg(cv, bx, by, kx, ky, tx, ty)
    cv.ellipse(cx - ax * 3, cy - ay * 3, 8 - step * 0.5, 5 - step * 0.4, SHELL)
    cv.ellipse(cx - ax * 3, cy - ay * 3 - 1, 3, 1.6, [PC[2], PC[4]])
    cv.ellipse(cx + ax * 4, cy + ay * 4, 4, 3.5, SHELL)
    if step >= 3:
        cv.ellipse(cx + 5, cy + 4, 2, 1, [GOO_DK])


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
                px[x, y] = (254, 0, 207 - k, 255)  # 200 = darkest, 207 = brightest in game
            else:
                px[x, y] = (r, g, b, 255)
    out = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    out.paste(fr, ((FRAME - SHRINK) // 2, (FRAME - SHRINK) // 2))
    return out


def main():
    pal = Image.open(os.path.join(GRAPHICS_DIR, "orc", "units", "grunt.png")).getpalette()
    dst = sys.argv[1] if len(sys.argv) > 1 else os.path.join(GRAPHICS_DIR, "forsaken", "units", "crypt_fiend.png")
    sheet = Image.new("RGBA", (5 * FRAME, 14 * FRAME), (0, 0, 0, 0))
    move = {3: 0, 6: 1, 9: 2, 12: 3}
    attack = {1: 0, 4: 1, 7: 2, 10: 3}
    death = {2: 0, 5: 1, 8: 2, 11: 3, 13: 4}
    for r in range(14):
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
