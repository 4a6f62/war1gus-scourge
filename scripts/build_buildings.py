#!/usr/bin/env python3
"""
Draw the Scourge buildings from scratch (no Blizzard art), loosely after their
Warcraft III Undead counterparts, in the gritty WC1 look of the unit sprites:

  barracks       -> Crypt                (64x64)
  blacksmith     -> Slaughterhouse       (48x48)
  church         -> Temple of the Damned (64x64)
  farm           -> Ziggurat             (48x48)
  lumber_mill    -> Graveyard            (64x64)
  stable         -> Sacrificial Pit      (64x64)
  tower          -> Spirit Tower         (48x48)
  town_hall      -> Necropolis           (64x64)
  stormwind_keep -> Black Citadel        (80x80)

Every building gets a patch of purple Blight under it. Each one is drawn at
SS times the size, shrunk with LANCZOS (mixed, rough pixels), roughened with a
little noise and quantised to the tileset palette. Pure blue is team colour and
is snapped to palette indices 200..207 (200 = darkest).

<name>_construction.png holds three frames (0%, 33%, 67%): the Blight with a
few foundation stones, then the bottom ~45% and ~75% of the building with bone
scaffolding.

Usage: python3 scripts/build_buildings.py [name ...]
"""

import math
import os
import random
import sys
import zlib

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_forsaken_art import GRAPHICS_DIR, rgba_to_indexed  # noqa: E402

SS = 4  # supersampling factor

# ---------------------------------------------------------------- colours
STONE = [(126, 120, 136), (96, 90, 106), (70, 65, 80), (46, 42, 54), (28, 26, 34)]
SLATE = [(84, 80, 96), (62, 58, 72), (44, 41, 52), (30, 28, 36)]
PURP = [(128, 84, 146), (98, 62, 114), (70, 44, 84), (48, 30, 58)]
BONE = [(226, 218, 196), (186, 176, 154), (136, 128, 110), (92, 86, 74)]
GLOW = [(204, 255, 170), (150, 240, 100), (90, 200, 60), (46, 130, 36)]
BLIGHT = [(76, 58, 82), (60, 45, 66), (48, 36, 54), (36, 27, 41)]
WOOD = [(104, 78, 58), (80, 58, 42), (58, 42, 31), (40, 29, 22)]
MEAT = [(170, 52, 48), (130, 34, 34), (90, 22, 26)]
IRON = [(110, 108, 116), (76, 74, 82), (48, 47, 54)]
SPIRIT = [(232, 255, 250), (170, 240, 230), (110, 200, 196), (70, 150, 150)]
SHADOW = (14, 12, 16)
PC = [(40, 40, 255 - i * 26) for i in range(8)]  # team colour, PC[0] = brightest


class Layer:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)

    def _p(self, pts):
        return [(x * SS, y * SS) for x, y in pts]

    def poly(self, pts, c):
        self.d.polygon(self._p(pts), fill=c)

    def ell(self, cx, cy, rx, ry, c):
        self.d.ellipse([(cx - rx) * SS, (cy - ry) * SS, (cx + rx) * SS, (cy + ry) * SS], fill=c)

    def rect(self, x0, y0, x1, y1, c):
        self.d.rectangle([x0 * SS, y0 * SS, x1 * SS - 1, y1 * SS - 1], fill=c)

    def line(self, pts, c, w=1.0):
        self.d.line(self._p(pts), fill=c, width=max(1, int(w * SS)), joint="curve")

    def shaded_ell(self, cx, cy, rx, ry, cols, lx=-0.35, ly=-0.4):
        """Dome/blob lit from the top left: darkest full size, lighter ones
        smaller and shifted towards the light."""
        n = len(cols)
        for i, c in enumerate(reversed(cols)):
            f = 1 - i / n * 0.75
            self.ell(cx + lx * rx * (1 - f), cy + ly * ry * (1 - f), rx * f, ry * f, c)

    def block(self, x0, x1, yb, h, depth, top, front, side=None, sidew=0):
        """Oblique box: front face from yb-h to yb, top face above it."""
        self.rect(x0, yb - h, x1, yb, front)
        self.poly([(x0, yb - h - depth), (x1, yb - h - depth), (x1, yb - h), (x0, yb - h)], top)
        if side and sidew:
            self.poly([(x1, yb - h - depth), (x1 + sidew, yb - h - depth + sidew * 0.5),
                       (x1 + sidew, yb + sidew * 0.5 - depth * 0.0), (x1, yb)], side)

    def spike(self, x, y, dx, dy, w, cols=BONE):
        """Curved bone tusk from (x, y) with tip at (x+dx, y+dy)."""
        mx, my = x + dx * 0.55 - dy * 0.15, y + dy * 0.55 + dx * 0.15
        nx, ny = -dy, dx
        ln = math.hypot(nx, ny) or 1
        nx, ny = nx / ln * w / 2, ny / ln * w / 2
        self.poly([(x - nx, y - ny), (mx - nx * 0.6, my - ny * 0.6), (x + dx, y + dy),
                   (mx + nx * 0.6, my + ny * 0.6), (x + nx, y + ny)], cols[1])
        self.line([(x - nx * 0.4, y - ny * 0.4), (mx - nx * 0.3, my - ny * 0.3), (x + dx, y + dy)], cols[0], 0.6)

    def banner(self, x, y, w, h):
        """Team-coloured banner hanging from a crossbar at (x, y)."""
        self.rect(x, y, x + w, y + h, PC[3])
        self.rect(x, y, x + w * 0.35, y + h, PC[1])
        self.rect(x + w * 0.75, y, x + w, y + h, PC[5])
        self.poly([(x, y + h), (x + w / 2, y + h - w * 0.5), (x + w, y + h), (x + w, y + h + 0.01), (x, y + h + 0.01)], (0, 0, 0, 0))
        self.d.polygon(self._p([(x, y + h), (x + w / 2, y + h - w * 0.55), (x + w, y + h)]), fill=(0, 0, 0, 0))
        self.line([(x - 1, y), (x + w + 1, y)], BONE[2], 0.8)
        self.ell(x + w / 2, y + h * 0.4, w * 0.18, w * 0.18, BONE[1])  # skull emblem

    def glow(self, cx, cy, rx, ry):
        for i, c in enumerate(reversed(GLOW)):
            f = 1 - i * 0.22
            self.ell(cx, cy, rx * f, ry * f, c)

    def skull(self, x, y, s=1.6):
        self.ell(x, y, s, s * 0.9, BONE[1])
        self.ell(x - s * 0.15, y - s * 0.2, s * 0.6, s * 0.5, BONE[0])
        self.ell(x - s * 0.45, y + s * 0.1, s * 0.25, s * 0.25, SHADOW)
        self.ell(x + s * 0.45, y + s * 0.1, s * 0.25, s * 0.25, SHADOW)


def blight(L, cx, cy, rx, ry, seed):
    """Irregular purple Blight patch with a few bones in it."""
    rnd = random.Random(seed)
    pts = []
    for i in range(28):
        a = i / 28 * 2 * math.pi
        r = 1 - rnd.random() * 0.18
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    L.poly(pts, BLIGHT[2])
    for _ in range(int(rx * ry / 9)):
        a = rnd.random() * 2 * math.pi
        r = rnd.random() ** 0.6 * 0.85
        x, y = cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r
        L.ell(x, y, 0.6 + rnd.random() * 1.6, 0.4 + rnd.random() * 0.9, rnd.choice(BLIGHT))
    for _ in range(int(rx / 6)):
        a = rnd.random() * 2 * math.pi
        x, y = cx + math.cos(a) * rx * 0.8, cy + math.sin(a) * ry * 0.8
        L.line([(x - 1, y), (x + 1, y + 0.6)], BONE[2], 0.5)


# ---------------------------------------------------------------- buildings
def crypt(G, S):
    """Crypt: a stone tomb mound with bone ribs and a glowing doorway."""
    blight(G, 32, 38, 30, 24, 1)
    S.ell(33, 50, 27, 8, SHADOW)
    S.shaded_ell(32, 34, 26, 19, STONE[1:])
    # rows of stone blocks on the mound
    for r, yy in enumerate((24, 31, 38)):
        S.line([(10 + r * 1.5, yy + 2), (32, yy - 2), (54 - r * 1.5, yy + 2)], STONE[3], 0.5)
    # bone ribs arching over the mound
    for k in (-14, -7, 7, 14):
        x = 32 + k
        S.line([(x, 45), (x * 0.82 + 32 * 0.18, 26), (x * 0.6 + 32 * 0.4, 17)], BONE[2], 2.4)
        S.line([(x - 0.4, 44), (x * 0.82 + 32 * 0.18 - 0.4, 26), (x * 0.6 + 32 * 0.4 - 0.4, 17.5)], BONE[0], 0.9)
    # portal at the front
    S.block(22, 42, 55, 16, 4, STONE[1], STONE[2])
    S.poly([(24.5, 55), (24.5, 45), (32, 40), (39.5, 45), (39.5, 55)], SHADOW)
    S.glow(32, 52, 5, 3)
    S.poly([(26, 55), (26, 46), (32, 42.5), (38, 46), (38, 55), (36, 55), (36, 47), (32, 44.5), (28, 47), (28, 55)], (0, 0, 0, 0))
    S.poly([(26, 55), (26, 46), (32, 42.5), (38, 46), (38, 55)], (20, 34, 18))
    S.glow(32, 53, 4.5, 2.6)
    # pillars with tusks and banners
    for x in (19, 45):
        S.block(x - 3, x + 3, 56, 20, 2, STONE[0], STONE[2])
        S.spike(x, 35, -2 if x < 32 else 2, -9, 3)
        S.banner(x - 2.2, 42, 4.4, 9)
    S.skull(32, 37, 2.2)


def slaughterhouse(G, S):
    """Slaughterhouse: dark timber hall on a stone base, spiked roof, meat."""
    blight(G, 24, 28, 23, 19, 2)
    S.ell(25, 41, 21, 5, SHADOW)
    S.block(7, 41, 42, 9, 3, STONE[1], STONE[2])  # stone base
    S.block(9, 39, 34, 9, 2, WOOD[1], WOOD[2])  # timber walls
    for x in range(11, 39, 4):
        S.line([(x, 25.5), (x, 34)], WOOD[3], 0.5)
    # gable roof
    S.poly([(6, 26), (24, 9), (42, 26)], WOOD[2])
    S.poly([(6, 26), (24, 9), (24, 26)], WOOD[1])
    for k in range(1, 5):
        S.line([(6 + k * 4.2, 26 - k * 3.8), (24, 26 - k * 3.8 - 0.0)], WOOD[3], 0.4)
    S.line([(6, 26), (24, 9), (42, 26)], BONE[2], 1.0)
    for t in (0.2, 0.4, 0.6, 0.8):  # spikes along the ridge line
        x, y = 6 + 18 * t * 2 if t <= 0.5 else 24 + 18 * (t - 0.5) * 2, 0
        y = 26 - 17 * (1 - abs(x - 24) / 18)
        S.spike(x, y, (x - 24) * 0.12, -5, 1.8)
    S.spike(24, 9.5, 0, -6, 2.2)
    # door with red light, and the team-coloured stripe
    S.rect(20, 33, 28, 42, SHADOW)
    S.rect(21, 36, 27, 42, MEAT[2])
    S.ell(24, 41, 3, 1.4, MEAT[0])
    S.rect(9, 29, 39, 31, PC[3])
    S.rect(9, 29, 39, 29.8, PC[1])
    # hanging meat on a beam
    S.line([(29, 30), (40, 30)], WOOD[3], 0.8)
    for x in (31, 35, 39):
        S.line([(x, 30), (x, 32)], IRON[1], 0.5)
        S.ell(x, 34.5, 1.4, 2.6, MEAT[1])
        S.ell(x - 0.4, 34, 0.7, 1.6, MEAT[0])
    # chain and hook
    S.line([(12, 26), (12, 35)], IRON[0], 0.5)
    S.line([(12, 35), (13, 36.5)], IRON[0], 0.6)


def temple(G, S):
    """Temple of the Damned: a stepped stone platform, four spires and a
    green cauldron of plague in the middle."""
    blight(G, 32, 38, 30, 24, 3)
    S.ell(33, 52, 28, 8, SHADOW)
    # two octagonal tiers
    def octa(cx, cy, rx, ry):
        return [(cx + math.cos(a) * rx, cy + math.sin(a) * ry)
                for a in [math.pi / 8 + k * math.pi / 4 for k in range(8)]]
    S.poly([(x, y + 4) for x, y in octa(32, 42, 27, 13)], STONE[3])
    S.poly(octa(32, 42, 27, 13), STONE[1])
    S.poly([(x, y + 3) for x, y in octa(32, 37, 18, 9)], STONE[3])
    S.poly(octa(32, 37, 18, 9), STONE[0])
    # team-coloured trim round the upper tier
    pts = octa(32, 40, 18, 9)
    for i in range(3, 6):
        S.line([pts[i], pts[i + 1]], PC[2], 1.2)
    # cauldron
    S.ell(32, 38, 8, 4.5, SLATE[3])
    S.ell(32, 36.5, 8, 4, SLATE[1])
    S.glow(32, 36.5, 6.5, 3)
    for dx in (-3, 1, 4):
        S.ell(32 + dx, 33 - abs(dx) * 0.3, 1.1, 1.4, GLOW[1])
    S.ell(31, 29, 2.0, 2.4, GLOW[2])
    S.ell(33, 25, 1.4, 1.8, GLOW[3])
    # four spires (the back two first)
    for x, yb, h in ((14, 34, 26), (50, 34, 26), (10, 48, 24), (54, 48, 24)):
        S.poly([(x - 3.6, yb), (x - 2.6, yb - h * 0.75), (x, yb - h), (x + 2.6, yb - h * 0.75), (x + 3.6, yb)], SLATE[1])
        S.poly([(x - 3.6, yb), (x - 2.6, yb - h * 0.75), (x, yb - h), (x, yb)], SLATE[0])
        S.line([(x - 2.8, yb - h * 0.5), (x + 2.8, yb - h * 0.5)], PURP[1], 1.2)
        S.ell(x, yb - h * 0.62, 1.3, 1.3, GLOW[1])
        S.spike(x - 2.5, yb - h * 0.75, -3, -3, 1.4)
        S.spike(x + 2.5, yb - h * 0.75, 3, -3, 1.4)
    S.banner(25, 44, 5, 8)
    S.banner(34, 44, 5, 8)


def graveyard(G, S):
    """Graveyard: spiked iron fence, tombstones, a small mausoleum, a dead
    tree and a pile of coffins."""
    blight(G, 32, 34, 31, 28, 4)
    rnd = random.Random(44)
    # mausoleum at the back
    S.ell(33, 27, 11, 3, SHADOW)
    S.block(24, 40, 26, 10, 3, STONE[1], STONE[2])
    S.poly([(22, 16), (32, 8), (42, 16)], PC[3])
    S.poly([(22, 16), (32, 8), (32, 16)], PC[1])
    S.line([(22, 16), (32, 8), (42, 16)], STONE[3], 0.6)
    S.rect(29, 19, 35, 26, SHADOW)
    S.glow(32, 24.5, 2.2, 1.4)
    S.spike(32, 8.5, 0, -4, 1.4)
    # dead tree
    t = [(10, 30), (11, 22), (9, 16), (6, 12)]
    S.line(t, WOOD[3], 1.6)
    S.line([(11, 22), (15, 17), (17, 15)], WOOD[3], 1.0)
    S.line([(10, 18), (6, 18)], WOOD[3], 0.7)
    # tombstones in rows
    for row, y in enumerate((36, 44, 52)):
        for i in range(4):
            x = 16 + i * 10 + (row % 2) * 4 + rnd.uniform(-1, 1)
            h = rnd.uniform(4, 5.5)
            S.ell(x + 1, y + 0.7, 2.6, 0.9, SHADOW)
            S.rect(x - 2, y - h, x + 2, y, STONE[2])
            S.ell(x, y - h, 2, 1.6, STONE[2])
            S.rect(x - 2, y - h, x - 0.6, y, STONE[1])
            S.ell(x - 0.5, y - h - 0.3, 1.2, 1, STONE[0])
            S.line([(x, y - h + 1.2), (x, y - 1.2)], STONE[3], 0.5)
            S.line([(x - 1, y - h + 2.2), (x + 1, y - h + 2.2)], STONE[3], 0.5)
    # coffin pile (the "lumber")
    for i, (x, y) in enumerate(((50, 31), (55, 32), (52.5, 28))):
        S.poly([(x - 2, y - 1), (x + 3, y - 2), (x + 4, y), (x - 1, y + 1.3)], WOOD[1 + i % 2])
        S.line([(x - 2, y - 1), (x + 3, y - 2)], WOOD[0], 0.4)
    # spiked iron fence round three sides
    for x in range(4, 62, 3):
        S.line([(x, 60), (x, 55)], IRON[2], 0.8)
        S.line([(x, 55), (x, 54)], IRON[0], 0.5)
    S.line([(4, 57), (61, 57)], IRON[1], 0.6)
    for y in range(12, 58, 3):
        for x in (3, 61):
            S.line([(x, y + 4), (x, y)], IRON[2], 0.8)
            S.line([(x, y), (x, y - 1)], IRON[0], 0.5)
    S.line([(3, 12), (3, 58)], IRON[1], 0.5)
    S.line([(61, 12), (61, 58)], IRON[1], 0.5)
    # ghostly wisps
    for x, y in ((20, 32), (44, 40)):
        S.ell(x, y, 1.1, 1.6, GLOW[1])


def sacrificial_pit(G, S):
    """Sacrificial Pit: a round stone rim round a glowing green pool, bone
    tusks curling over it and an altar slab at the front."""
    blight(G, 32, 36, 30, 26, 5)
    S.ell(33, 47, 27, 12, SHADOW)
    S.ell(32, 38, 26, 15, STONE[3])
    S.ell(32, 36, 26, 15, STONE[1])
    # stone blocks along the rim
    for i in range(16):
        a = i / 16 * 2 * math.pi
        x, y = 32 + math.cos(a) * 22.5, 36 + math.sin(a) * 12.8
        S.ell(x, y, 3.2, 2.1, STONE[2 if math.sin(a) > 0 else 0])
        S.ell(x - 0.6, y - 0.6, 1.8, 1.0, STONE[1 if math.sin(a) > 0 else 0])
    # the pool
    S.ell(32, 36, 18, 9.5, SHADOW)
    S.glow(32, 37, 16, 8)
    for x, y in ((26, 36), (37, 39), (33, 34)):
        S.ell(x, y, 1.6, 0.9, GLOW[0])
    # tusks curling inward over the pool
    for a in (0.6, 1.4, 2.0, 2.9, 3.6, 4.3, 5.0, 5.8):
        x, y = 32 + math.cos(a) * 24, 36 + math.sin(a) * 14
        S.spike(x, y, -math.cos(a) * 6, -math.sin(a) * 3 - 6, 2.4)
    # altar slab at the front with a team-coloured cloth
    S.block(25, 39, 56, 4, 4, STONE[0], STONE[2])
    S.rect(29, 48, 35, 54, PC[2])
    S.rect(29, 48, 31, 54, PC[0])
    S.ell(32, 50, 1.5, 1.0, MEAT[1])
    # banners on poles
    for x in (8, 56):
        S.line([(x, 46), (x, 22)], WOOD[3], 1.0)
        S.banner(x - 2.4, 24, 4.8, 9)
        S.skull(x, 21.5, 1.5)


def spirit_tower(G, S):
    """Spirit Tower: a little ziggurat with a bone spire and a pale spirit
    orb on top."""
    blight(G, 24, 30, 23, 18, 6)
    S.ell(25, 41, 19, 5, SHADOW)
    # three stepped tiers
    for i, (x0, x1, yb, h, d) in enumerate(((5, 43, 43, 6, 6), (10, 38, 37, 5, 5), (15, 33, 32, 5, 4))):
        S.block(x0, x1, yb, h, d, STONE[i], STONE[2 + (i > 0)])
        S.rect(x0, yb - h, x1, yb - h + 1.2, PC[2 + i * 2])
    # spire with bone ribs
    S.poly([(19, 27), (21, 12), (24, 2), (27, 12), (29, 27)], SLATE[1])
    S.poly([(19, 27), (21, 12), (24, 2), (24, 27)], SLATE[0])
    for y, w in ((24, 6), (19, 5), (14, 4)):
        S.spike(24 - w / 2, y, -3.5, -4, 1.4)
        S.spike(24 + w / 2, y, 3.5, -4, 1.4)
    # spirit orb
    for i, c in enumerate(reversed(SPIRIT)):
        f = 1 - i * 0.22
        S.ell(24, 6, 4.2 * f, 4.2 * f, c)
    S.ell(23, 5, 1.2, 1.2, (255, 255, 255))
    # glowing door
    S.rect(21, 37, 27, 43, SHADOW)
    S.glow(24, 42, 2.4, 1.4)


def black_citadel(G, S):
    """Black Citadel: a large stepped necropolis keep with a central spire,
    four corner spires, bone tusks, green windows and banners."""
    blight(G, 40, 48, 39, 31, 7)
    S.ell(41, 66, 36, 9, SHADOW)
    # base tiers
    for i, (x0, x1, yb, h, d) in enumerate(((5, 75, 70, 9, 9), (12, 68, 60, 9, 8), (20, 60, 50, 8, 7))):
        S.block(x0, x1, yb, h, d, STONE[i], STONE[2 + (i > 0)])
        S.rect(x0, yb - h, x1, yb - h + 1.4, PURP[1])
        for x in range(int(x0) + 4, int(x1) - 2, 7):
            S.rect(x, yb - h + 3, x + 2, yb - 2, SHADOW)
            S.rect(x + 0.4, yb - h + 4.5, x + 1.6, yb - 2.5, GLOW[2])
    # central spire
    S.poly([(30, 43), (33, 20), (40, 2), (47, 20), (50, 43)], SLATE[1])
    S.poly([(30, 43), (33, 20), (40, 2), (40, 43)], SLATE[0])
    S.line([(40, 6), (40, 42)], SLATE[2], 0.6)
    S.ell(40, 26, 3, 3.4, SHADOW)
    S.glow(40, 26, 2.2, 2.6)
    for y, w in ((38, 18), (30, 14), (20, 9)):
        S.spike(40 - w / 2, y, -5, -6, 2.4)
        S.spike(40 + w / 2, y, 5, -6, 2.4)
    # corner spires
    for x, yb, h in ((10, 64, 22), (70, 64, 22), (18, 52, 18), (62, 52, 18)):
        S.poly([(x - 3.5, yb), (x - 2.5, yb - h * 0.7), (x, yb - h), (x + 2.5, yb - h * 0.7), (x + 3.5, yb)], SLATE[1])
        S.poly([(x - 3.5, yb), (x - 2.5, yb - h * 0.7), (x, yb - h), (x, yb)], SLATE[0])
        S.ell(x, yb - h * 0.55, 1.1, 1.3, GLOW[1])
    # gate and banners
    S.poly([(34, 70), (34, 62), (40, 57), (46, 62), (46, 70)], SHADOW)
    S.glow(40, 68, 4.5, 2.4)
    S.skull(40, 54, 2.4)
    for x in (26, 50):
        S.banner(x, 61, 5, 9)


def ziggurat(G, S):
    """Ziggurat (farm): a squat stepped obsidian pyramid with glowing green
    runes and a floating fel crystal at the apex."""
    blight(G, 24, 30, 23, 18, 6)
    S.ell(25, 41, 20, 5, SHADOW)
    # three stepped pyramid tiers
    for i, (x0, x1, yb, h, d) in enumerate(((4, 44, 43, 6, 6), (9, 39, 37, 6, 5), (14, 34, 31, 5, 4))):
        S.block(x0, x1, yb, h, d, STONE[i], STONE[2 + (i > 0)])
        S.rect(x0, yb - h, x1, yb - h + 1.2, PURP[1])
        for x in range(int(x0) + 4, int(x1) - 2, 6):
            S.rect(x, yb - h + 2.0, x + 1.5, yb - 1.0, SHADOW)
            S.rect(x + 0.3, yb - h + 2.4, x + 1.2, yb - 1.3, GLOW[2])
    # team-coloured banners flanking the entrance
    for x in (13, 32):
        S.banner(x, 34, 3.2, 6)
    # dark archway
    S.poly([(20, 43), (20, 38), (24, 35), (28, 38), (28, 43)], SHADOW)
    S.glow(24, 41.5, 2.2, 1.4)
    # floating crystal
    S.poly([(24, 7), (28, 15), (24, 23), (20, 15)], GLOW[2])
    S.poly([(24, 7), (24, 23), (20, 15)], GLOW[0])
    S.ell(24, 15, 1.6, 2.2, GLOW[0])


def necropolis(G, S):
    """Necropolis (town_hall): a stepped obsidian bastion with corner bone
    spires, glowing green windows and a central spire."""
    blight(G, 32, 38, 31, 24, 6)
    S.ell(33, 53, 28, 7, SHADOW)
    # two stepped tiers
    for i, (x0, x1, yb, h, d) in enumerate(((5, 59, 56, 8, 8), (12, 52, 47, 8, 7))):
        S.block(x0, x1, yb, h, d, STONE[i], STONE[2 + (i > 0)])
        S.rect(x0, yb - h, x1, yb - h + 1.3, PURP[1])
        for x in range(int(x0) + 4, int(x1) - 2, 7):
            S.rect(x, yb - h + 2.5, x + 2, yb - 1.8, SHADOW)
            S.rect(x + 0.4, yb - h + 3.5, x + 1.6, yb - 2.2, GLOW[2])
    # central spire
    S.poly([(24, 39), (27, 20), (32, 4), (37, 20), (40, 39)], SLATE[1])
    S.poly([(24, 39), (27, 20), (32, 4), (32, 39)], SLATE[0])
    S.ell(32, 24, 2.5, 3.0, SHADOW)
    S.glow(32, 24, 1.8, 2.2)
    for y, w in ((34, 14), (27, 10), (19, 7)):
        S.spike(32 - w / 2, y, -4, -5, 2.0)
        S.spike(32 + w / 2, y, 4, -5, 2.0)
    # corner spires
    for x, yb, h in ((10, 50, 16), (54, 50, 16)):
        S.poly([(x - 3, yb), (x - 2, yb - h * 0.7), (x, yb - h), (x + 2, yb - h * 0.7), (x + 3, yb)], SLATE[1])
        S.poly([(x - 3, yb), (x - 2, yb - h * 0.7), (x, yb - h), (x, yb)], SLATE[0])
        S.ell(x, yb - h * 0.55, 1.0, 1.2, GLOW[1])
    # gate and banners
    S.poly([(27, 56), (27, 49), (32, 45), (37, 49), (37, 56)], SHADOW)
    S.glow(32, 54, 3.8, 2.0)
    S.skull(32, 42, 2.0)
    for x in (20, 40):
        S.banner(x, 49, 4.2, 8)


BUILDINGS = {
    # name: (draw function, size, has construction sheet)
    "barracks": (crypt, 64, True),
    "blacksmith": (slaughterhouse, 48, True),
    "church": (temple, 64, True),
    "farm": (ziggurat, 48, True),
    "lumber_mill": (graveyard, 64, True),
    "stable": (sacrificial_pit, 64, True),
    "tower": (spirit_tower, 48, True),
    "town_hall": (necropolis, 64, True),
    "stormwind_keep": (black_citadel, 80, False),
}


# ---------------------------------------------------------------- finishing
def finish(layer, seed):
    """Shrink, threshold alpha, add grit and snap team colour."""
    w, h = layer.w, layer.h
    im = layer.im.resize((w, h), Image.LANCZOS)
    px = im.load()
    rnd = random.Random(seed)
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 140:
                px[x, y] = (0, 0, 0, 0)
            elif b > r + 60 and b > g + 60:
                k = max(0, min(7, int((255 - b) / 26)))
                px[x, y] = (254, 0, 207 - k, 255)  # 200 = darkest, 207 = brightest
            else:
                glowing = g > r + 50 and g > b + 40
                j = 0 if glowing else rnd.randint(-9, 9)
                px[x, y] = (max(0, min(255, r + j)), max(0, min(255, g + j)), max(0, min(255, b + j)), 255)
    return im


def scaffold(im, frac, seed):
    """Bone scaffolding poles over a partly built frame."""
    d = ImageDraw.Draw(im)
    w, h = im.size
    rnd = random.Random(seed)
    top = int(h * (1 - frac))
    for i in range(3 + w // 24):
        x = rnd.randint(w // 6, w - w // 6)
        d.line([(x, top - 2), (x, h - h // 6)], fill=BONE[2] + (255,), width=1)
    for y in (top, top + (h - top) // 2):
        d.line([(w // 6, y), (w - w // 6, y)], fill=BONE[3] + (255,), width=1)


def render(name):
    fn, size, has_constr = BUILDINGS[name]
    G, S = Layer(size, size), Layer(size, size)
    fn(G, S)
    ground = finish(G, zlib.crc32(name.encode()) & 0xffff)
    struct = finish(S, (zlib.crc32(name.encode()) >> 4) & 0xffff)
    full = ground.copy()
    full.alpha_composite(struct)

    frames = []
    if has_constr:
        # 0%: just Blight and a few foundation stones
        f0 = ground.copy()
        d = ImageDraw.Draw(f0)
        rnd = random.Random(size)
        for _ in range(size // 8):
            x, y = rnd.randint(size // 4, size * 3 // 4), rnd.randint(size // 3, size * 3 // 4)
            d.rectangle([x, y, x + 2, y + 1], fill=STONE[2] + (255,))
        frames.append(f0)
        # 33% and 67%: lower part of the building plus scaffolding
        sp = struct.load()
        ys = [y for y in range(size) for x in range(size) if sp[x, y][3]]
        top, bot = min(ys), max(ys)
        for frac in (0.45, 0.75):
            cut = bot - (bot - top) * frac
            part = struct.copy()
            pp = part.load()
            for y in range(size):
                if y < cut:
                    for x in range(size):
                        pp[x, y] = (0, 0, 0, 0)
            f = ground.copy()
            f.alpha_composite(part)
            scaffold(f, frac, size + int(frac * 10))
            frames.append(f)
    return full, frames


def main():
    names = sys.argv[1:] or list(BUILDINGS)
    for ts in ("forest", "swamp"):
        d = os.path.join(GRAPHICS_DIR, "tilesets", ts, "forsaken", "buildings")
        pal = Image.open(os.path.join(GRAPHICS_DIR, "tilesets", ts, "orc", "buildings", "town_hall.png")).getpalette()
        for name in names:
            full, frames = render(name)
            rgba_to_indexed(full, pal).save(os.path.join(d, name + ".png"))
            if frames:
                size = full.size[0]
                sheet = Image.new("RGBA", (size, size * 3), (0, 0, 0, 0))
                for i, f in enumerate(frames):
                    sheet.paste(f, (0, i * size))
                rgba_to_indexed(sheet, pal).save(os.path.join(d, name + "_construction.png"))
            print("wrote", ts, name)


if __name__ == "__main__":
    main()
