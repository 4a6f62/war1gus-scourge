#!/usr/bin/env python3
"""
Generate authentic Warcraft III Scourge pixel art in native .aseprite format
and compile into Stratagus unit spritesheets.

Units generated:
1. Ghoul (160x480 PNG + ghoul.aseprite):
   Hunched feral prowler with dorsal spine spikes, razor bone claws, glowing feral eyes,
   and player-color loincloth.
2. Crypt Fiend (160x448 PNG + crypt_fiend.aseprite):
   Nerubian Centaur with armored 6-legged arachnid chassis, team-color necrotic runes,
   and upright mummified humanoid torso wielding twin scythe blades.
3. Abomination (240x720 PNG + abomination.aseprite):
   Colossal stitched meat golem with swollen sagging gut, surgical sutures, giant meat
   cleaver, iron hook & chains, third skeletal arm, and player-color apron.

All sprites strictly adhere to Warcraft 1 unit palette indices [96..254] (transparency 255).
"""

import os
import sys
import numpy as np
from PIL import Image

BASE_DIR = "/home/smiles/forsaken-mod"
UNITS_DIR = os.path.join(BASE_DIR, "graphics", "forsaken", "units")
REF_PAL_IMG = os.path.join(BASE_DIR, "graphics", "human", "units", "footman.png")

sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
from aseprite_tool import write_aseprite, compile_aseprite_to_sheet

# Palette Constants (strict [96..254])
OUTLINE = 96        # Pure black (0, 0, 0)
SHADOW_DEEP = 253   # Darkest midnight shadow (20, 20, 40)
SHADOW_MID = 252    # Dark shadow (48, 48, 80)
SHADOW_LIGHT = 251  # Mid shadow (84, 84, 120)

STEEL_BRIGHT = 217  # White highlight (252, 252, 252)
STEEL_HIGH = 219    # High steel (196, 196, 196)
STEEL_MID = 249     # Polished steel (176, 176, 196)
STEEL_DARK = 250    # Shadowed steel (124, 124, 152)

FLESH_SHADOW = 184  # Crease shadow (12, 20, 12)
FLESH_DEEP = 209    # Dark olive teal (28, 68, 68)
FLESH_DARK = 210    # Dark necrotic green-gray (48, 80, 88)
FLESH_MID = 211     # Mid decaying flesh (80, 104, 104)
FLESH_LIGHT = 212   # Light necrotic flesh (100, 124, 108)
FLESH_HIGH = 213    # Sickly pale flesh (128, 140, 112)
FLESH_PALE = 214    # Highlight corpse skin (156, 180, 148)

BLOOD_DARK = 176    # Coagulated blood (84, 0, 0)
BLOOD_MID = 177     # Deep red blood (108, 0, 0)
BLOOD_BRIGHT = 179  # Bright red blood (156, 0, 0)
BLOOD_FRESH = 182   # Crimson gore (228, 0, 4)

BONE_WHITE = 217    # Pure bone highlight (252, 252, 252)
BONE_PALE = 240     # Weathered ivory bone (204, 196, 184)
BONE_MID = 191      # Shaded bone (208, 208, 236)
BONE_SHADOW = 190   # Bone crease (176, 184, 208)

EYE_YELLOW = 221    # Feral yellow eye (252, 252, 0)
EYE_AMBER = 243     # Glowing amber eye (252, 212, 136)
EYE_GREEN = 223     # Nerubian green cluster eye (0, 252, 0)

PC_SHADOW = 200     # Deepest team shadow (0, 8, 36)
PC_DARK = 201       # Dark team color (0, 16, 64)
PC_MID = 203        # Mid team color (0, 40, 128)
PC_LIGHT = 204      # Light team color (4, 52, 156)
PC_BRIGHT = 205     # Bright team color (8, 64, 188)
PC_HIGH = 206       # High team color (12, 80, 220)
PC_SHINE = 207      # Team color highlight (20, 96, 252)

TRANSPARENT = 255


def get_ref_palette():
    return Image.open(REF_PAL_IMG).getpalette()


# ==============================================================================
# 1. GHOUL SPRITES
# ==============================================================================
def draw_ghoul_frame(step, dir_idx, mode):
    """
    Renders one 32x32 frame of the feral Scourge Ghoul.
    mode: 'walk', 'attack', 'death'
    step: 0..4
    dir_idx: 0=N, 1=NE, 2=E, 3=SE, 4=S
    """
    arr = np.full((32, 32), TRANSPARENT, dtype=np.uint8)

    def p(x, y, c):
        if 0 <= x < 32 and 0 <= y < 32:
            arr[y, x] = c

    def block(x0, y0, w, h, fill, border=OUTLINE):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if border and (x == x0 or x == x0 + w - 1 or y == y0 or y == y0 + h - 1):
                    p(x, y, border)
                else:
                    p(x, y, fill)

    # ---------------- DEATH ANIMATION ----------------
    if mode == "death":
        prog = step
        # Base blood puddle spreading on the ground
        rad = 3 + prog * 2
        for dy in range(-prog, prog + 1):
            for dx in range(-rad, rad + 1):
                if (dx * dx) / (rad * rad + 0.1) + (dy * dy) / (max(1, prog * prog) + 0.1) <= 1.0:
                    p(16 + dx, 24 + dy, BLOOD_MID if abs(dx) + abs(dy) < 3 else BLOOD_DARK)

        # Body collapses down from upright to floor
        head_y = 12 + prog * 3
        torso_y = 16 + prog * 2

        if prog < 3:
            # Hunched spine buckling
            block(13, torso_y, 7, 5, FLESH_DARK, OUTLINE)
            # Bone spikes snapping
            p(15, torso_y - 1, BONE_WHITE)
            p(17, torso_y - 1, BONE_PALE)
            # Head rolling
            block(12, head_y, 5, 5, FLESH_MID, OUTLINE)
            p(13, head_y + 2, EYE_YELLOW)
        else:
            # Splayed rotting ribcage and severed limbs
            for rx in range(12, 21, 2):
                p(rx, 23, BONE_WHITE)
                p(rx + 1, 24, BONE_MID)
                p(rx, 25, BLOOD_FRESH)
            # Cracked skull on side
            block(21, 22, 5, 4, BONE_PALE, OUTLINE)
            p(22, 23, OUTLINE)  # eye socket
            p(24, 24, BONE_WHITE)  # fangs
            p(20, 24, BLOOD_BRIGHT)

        return arr.tobytes()

    # ---------------- WALK / ATTACK ANIMATIONS ----------------
    # Walking leg bob and claw reach
    bob = [0, -1, 0, 1, 0][step]
    l_leg_swing = [-2, 0, 2, 0, -1][step]
    r_leg_swing = [2, 0, -2, 0, 1][step]

    # Claw attack extensions
    claw_ext = [0, 2, 4, 2, 0][step] if mode == "attack" else 0

    # Direction-based offsets (N, NE, E, SE, S)
    # Ghoul is hunched forward: body center is around (16, 17)
    cy = 16 + bob
    cx = 16

    # 1. Shadow beneath unit
    for sx in range(-5, 6):
        p(cx + sx, 28, SHADOW_DEEP if abs(sx) < 3 else SHADOW_MID)

    # 2. Digitigrade Legs (bent backwards at hock)
    if dir_idx == 0:    # North (back view)
        # Left leg
        p(cx - 4, cy + 5, FLESH_DEEP)
        p(cx - 5 + l_leg_swing, cy + 8, FLESH_DARK)
        p(cx - 5 + l_leg_swing, cy + 11, OUTLINE)
        # Right leg
        p(cx + 4, cy + 5, FLESH_DEEP)
        p(cx + 5 + r_leg_swing, cy + 8, FLESH_DARK)
        p(cx + 5 + r_leg_swing, cy + 11, OUTLINE)
    elif dir_idx == 4:  # South (front view)
        # Left leg
        p(cx - 4, cy + 5, FLESH_MID)
        p(cx - 5 + l_leg_swing, cy + 8, FLESH_DARK)
        p(cx - 5 + l_leg_swing, cy + 11, OUTLINE)
        # Right leg
        p(cx + 4, cy + 5, FLESH_LIGHT)
        p(cx + 5 + r_leg_swing, cy + 8, FLESH_MID)
        p(cx + 5 + r_leg_swing, cy + 11, OUTLINE)
    else:               # East / NE / SE (side view)
        p(cx - 2 + l_leg_swing, cy + 5, FLESH_DEEP)
        p(cx - 3 + l_leg_swing, cy + 8, FLESH_DARK)
        p(cx - 3 + l_leg_swing, cy + 11, OUTLINE)
        p(cx + 3 + r_leg_swing, cy + 5, FLESH_MID)
        p(cx + 2 + r_leg_swing, cy + 8, FLESH_LIGHT)
        p(cx + 2 + r_leg_swing, cy + 11, OUTLINE)

    # 3. Torso (hunched mass of green/gray muscle and exposed ribs)
    for dy in range(-4, 5):
        w_span = 4 if abs(dy) < 3 else 3
        for dx in range(-w_span, w_span + 1):
            if dx == -w_span or dx == w_span or dy == -4 or dy == 4:
                p(cx + dx, cy + dy, OUTLINE)
            elif dx < 0 and dy < 0:
                p(cx + dx, cy + dy, FLESH_LIGHT)
            elif dx > 1 or dy > 2:
                p(cx + dx, cy + dy, FLESH_DEEP)
            else:
                p(cx + dx, cy + dy, FLESH_MID)

    # Exposed bloody ribcage (visible from front and sides)
    if dir_idx in (1, 2, 3, 4):
        p(cx - 1, cy, BONE_WHITE)
        p(cx, cy, BLOOD_BRIGHT)
        p(cx + 1, cy + 1, BONE_PALE)
        p(cx, cy + 2, BLOOD_DARK)

    # Player-colored tattered loincloth
    p(cx - 2, cy + 4, PC_DARK)
    p(cx - 1, cy + 4, PC_LIGHT)
    p(cx, cy + 4, PC_BRIGHT)
    p(cx + 1, cy + 4, PC_MID)
    p(cx - 1, cy + 5, PC_LIGHT)
    p(cx, cy + 5, PC_SHINE)
    p(cx, cy + 6, PC_DARK)

    # 4. Hunched Spine & Dorsal Bone Spikes (Warcraft III iconic feature)
    # Spikes jutting out along the arched back
    if dir_idx in (0, 1, 2):  # Back / side views
        # Spike 1 (upper neck)
        p(cx - 1, cy - 5, BONE_WHITE)
        p(cx - 1, cy - 6, BONE_WHITE)
        p(cx - 2, cy - 5, OUTLINE)
        # Spike 2 (mid back)
        p(cx - 3, cy - 3, BONE_WHITE)
        p(cx - 4, cy - 4, BONE_PALE)
        p(cx - 4, cy - 3, OUTLINE)
        # Spike 3 (lower back)
        p(cx - 4, cy - 1, BONE_PALE)
        p(cx - 5, cy - 1, OUTLINE)
    else:  # Front views (spikes peek over shoulder)
        p(cx - 3, cy - 5, BONE_WHITE)
        p(cx + 3, cy - 5, BONE_PALE)

    # 5. Skull Head (jutting forward, low center)
    hx = cx + (3 if dir_idx in (1, 2, 3) else 0)
    hy = cy - 4 + (1 if dir_idx == 4 else 0)

    # Skull cranium
    block(hx - 2, hy - 3, 5, 4, FLESH_LIGHT, OUTLINE)
    p(hx - 1, hy - 3, BONE_WHITE)
    p(hx, hy - 3, BONE_PALE)

    # Eyes & Underbite
    if dir_idx == 0:    # North
        p(hx, hy - 2, FLESH_DARK)
    elif dir_idx == 4:  # South (front)
        p(hx - 1, hy - 1, EYE_YELLOW)
        p(hx + 1, hy - 1, EYE_YELLOW)
        p(hx - 1, hy + 1, BONE_WHITE)  # fangs
        p(hx + 1, hy + 1, BONE_WHITE)
        p(hx, hy + 1, BLOOD_DARK)     # mouth cavity
    else:               # East / Side
        p(hx + 1, hy - 1, EYE_YELLOW)
        p(hx + 2, hy, BONE_WHITE)      # jutting lower canine
        p(hx + 1, hy, BLOOD_DARK)

    # 6. Elongated Arms & Razor Claws
    # Arms hang down to knees; during attack, they slash forward
    if dir_idx in (1, 2, 3):  # Side view
        # Back arm
        p(cx - 3, cy - 1, FLESH_DARK)
        p(cx - 4, cy + 2, FLESH_DEEP)
        # Main front arm with massive 3-pronged claws
        arm_reach = 4 + claw_ext
        p(cx + 2, cy - 1, FLESH_LIGHT)
        p(cx + 3, cy + 2, FLESH_MID)
        p(cx + 4 + claw_ext // 2, cy + 5, FLESH_DARK)
        # 3 Razor Claws
        p(cx + arm_reach, cy + 7, STEEL_MID)
        p(cx + arm_reach + 1, cy + 8, BONE_WHITE)
        p(cx + arm_reach, cy + 9, BONE_WHITE)
        p(cx + arm_reach - 1, cy + 10, BONE_PALE)
        if mode == "attack" and step in (2, 3):
            # Blood slash arc
            p(cx + arm_reach + 2, cy + 6, BLOOD_BRIGHT)
            p(cx + arm_reach + 3, cy + 8, BLOOD_FRESH)
    elif dir_idx == 4:        # South (both arms visible)
        # Left claw
        p(cx - 5, cy + 1, FLESH_MID)
        p(cx - 6 - claw_ext, cy + 5, FLESH_DARK)
        p(cx - 6 - claw_ext, cy + 8, BONE_WHITE)
        p(cx - 7 - claw_ext, cy + 9, BONE_PALE)
        # Right claw
        p(cx + 5, cy + 1, FLESH_LIGHT)
        p(cx + 6 + claw_ext, cy + 5, FLESH_MID)
        p(cx + 6 + claw_ext, cy + 8, BONE_WHITE)
        p(cx + 7 + claw_ext, cy + 9, BONE_PALE)
    else:                     # North
        p(cx - 5, cy + 1, FLESH_DEEP)
        p(cx - 6, cy + 6, FLESH_DARK)
        p(cx - 6, cy + 9, BONE_PALE)
        p(cx + 5, cy + 1, FLESH_DEEP)
        p(cx + 6, cy + 6, FLESH_DARK)
        p(cx + 6, cy + 9, BONE_PALE)

    return arr.tobytes()


# ==============================================================================
# 2. CRYPT FIEND SPRITES (Nerubian Centaur)
# ==============================================================================
def draw_crypt_fiend_frame(step, dir_idx, mode):
    """
    Renders one 32x32 frame of the Nerubian Centaur Crypt Fiend.
    mode: 'walk', 'attack', 'death'
    step: 0..4 (walk/death) or 0..3 (attack)
    dir_idx: 0=N, 1=NE, 2=E, 3=SE, 4=S
    """
    arr = np.full((32, 32), TRANSPARENT, dtype=np.uint8)

    def p(x, y, c):
        if 0 <= x < 32 and 0 <= y < 32:
            arr[y, x] = c

    def block(x0, y0, w, h, fill, border=OUTLINE):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if border and (x == x0 or x == x0 + w - 1 or y == y0 or y == y0 + h - 1):
                    p(x, y, border)
                else:
                    p(x, y, fill)

    # ---------------- DEATH ANIMATION ----------------
    if mode == "death":
        prog = step
        # Green ichor puddle
        rad = 3 + prog * 2
        for dy in range(-prog // 2, prog // 2 + 1):
            for dx in range(-rad, rad + 1):
                if (dx * dx) / (rad * rad + 0.1) + (dy * dy) / (max(1, (prog // 2) ** 2) + 0.1) <= 1.0:
                    p(16 + dx, 25 + dy, FLESH_DEEP if abs(dx) < 2 else SHADOW_DEEP)

        if prog < 3:
            # Curled legs and collapsing chassis
            block(12, 18 + prog * 2, 9, 6, SHADOW_MID, OUTLINE)
            # Torso slumped forward
            block(14, 13 + prog * 3, 5, 5, SHADOW_LIGHT, OUTLINE)
            p(16, 12 + prog * 3, STEEL_MID)  # horned crest
        else:
            # Flattened dead carapace with cracked green shell and broken scythes
            block(10, 22, 13, 5, SHADOW_DEEP, OUTLINE)
            p(13, 23, PC_BRIGHT)  # shattered rune
            p(15, 23, EYE_GREEN)  # green ichor
            p(17, 24, EYE_GREEN)
            # Broken scythe blades
            p(8, 24, STEEL_MID)
            p(9, 23, STEEL_BRIGHT)
            p(23, 24, STEEL_MID)
            p(24, 25, STEEL_DARK)

        return arr.tobytes()

    # ---------------- WALK / ATTACK ANIMATIONS ----------------
    bob = [0, -1, 0, 1, 0][step]
    leg_phase = step % 4
    rear_up = [0, 2, 4, 1][step] if mode == "attack" else 0

    cx = 16
    cy = 19 + bob - rear_up // 2

    # 1. Ground Shadow
    for sx in range(-8, 9):
        p(cx + sx, 28, SHADOW_DEEP if abs(sx) < 5 else SHADOW_MID)

    # 2. Armored 6-Legged Spider Chassis (Arachnid Lower Body)
    # Abdomen bulb at rear
    if dir_idx == 0:    # North: Abdomen is prominent
        block(cx - 5, cy - 2, 11, 8, SHADOW_MID, OUTLINE)
        # Team color necrotic runes on carapace
        p(cx - 2, cy + 1, PC_LIGHT)
        p(cx - 1, cy + 1, PC_BRIGHT)
        p(cx, cy + 2, PC_SHINE)
        p(cx + 1, cy + 1, PC_BRIGHT)
        p(cx + 2, cy + 1, PC_LIGHT)
    elif dir_idx == 4:  # South: Cephalothorax in front, abdomen behind
        block(cx - 5, cy, 11, 7, SHADOW_DEEP, OUTLINE)
    else:               # Side: Abdomen extends to the left/back
        block(cx - 8, cy - 1, 10, 8, SHADOW_MID, OUTLINE)
        # Carapace runes
        p(cx - 5, cy + 1, PC_LIGHT)
        p(cx - 4, cy + 2, PC_BRIGHT)
        p(cx - 3, cy + 1, PC_LIGHT)

    # 6 Jointed Spiky Legs (3 pairs)
    leg_offsets = [
        (-7, 2 + (1 if leg_phase in (0, 1) else -1)),
        (-3, 4 + (1 if leg_phase in (1, 2) else -1)),
        (3, 4 + (1 if leg_phase in (2, 3) else -1)),
        (7, 2 + (1 if leg_phase in (3, 0) else -1)),
    ]
    for lx, ly in leg_offsets:
        # Leg upper joint
        p(cx + lx, cy + ly - 2, SHADOW_LIGHT)
        # Knee barb
        p(cx + lx + (1 if lx > 0 else -1), cy + ly, SHADOW_MID)
        # Pointed talon touching ground
        p(cx + lx + (2 if lx > 0 else -2), cy + ly + 3, OUTLINE)

    # 3. Upright Mummified Humanoid Nerubian Torso
    # Rises from the front of the chassis
    tx = cx + (2 if dir_idx in (1, 2, 3) else 0)
    ty = cy - 7 - rear_up

    # Torso chitin plating
    block(tx - 3, ty, 7, 7, SHADOW_LIGHT, OUTLINE)
    # Carapace chest rune (Player Team Color)
    p(tx, ty + 2, PC_BRIGHT)
    p(tx, ty + 3, PC_SHINE)
    p(tx - 1, ty + 3, PC_LIGHT)
    p(tx + 1, ty + 3, PC_LIGHT)

    # 4. Horned Pharaoh / Nerubian Helmet & Glowing Eyes
    hx = tx
    hy = ty - 5

    # Helmet skull
    block(hx - 2, hy - 1, 5, 4, SHADOW_MID, OUTLINE)
    # Twin curved beetle horns
    p(hx - 3, hy - 3, STEEL_MID)
    p(hx - 3, hy - 2, STEEL_BRIGHT)
    p(hx + 3, hy - 3, STEEL_MID)
    p(hx + 3, hy - 2, STEEL_BRIGHT)

    # Glowing cluster eyes
    if dir_idx == 4:  # South
        p(hx - 1, hy + 1, EYE_GREEN)
        p(hx, hy + 1, EYE_GREEN)
        p(hx + 1, hy + 1, EYE_GREEN)
    elif dir_idx in (1, 2, 3):  # Side
        p(hx + 1, hy + 1, EYE_GREEN)
        p(hx + 2, hy + 1, EYE_GREEN)

    # 5. Twin Scythe Blades (Curved Mantis Blades)
    scythe_reach = rear_up
    if dir_idx in (1, 2, 3):  # Side view
        # Right scythe extended forward
        p(tx + 3, ty + 1, STEEL_DARK)
        p(tx + 4 + scythe_reach, ty - 1, STEEL_MID)
        p(tx + 5 + scythe_reach, ty - 3, STEEL_BRIGHT)
        p(tx + 6 + scythe_reach, ty - 4, STEEL_HIGH)
        p(tx + 7 + scythe_reach, ty - 2, STEEL_MID)
        # Venom drip from scythe tip
        if mode == "attack" and step in (1, 2):
            p(tx + 8 + scythe_reach, ty - 2, EYE_GREEN)
            p(tx + 9 + scythe_reach, ty - 1, EYE_GREEN)
    else:  # Front / back: Twin scythes on both sides
        p(tx - 4, ty + 1, STEEL_DARK)
        p(tx - 5 - scythe_reach, ty - 2, STEEL_BRIGHT)
        p(tx - 6 - scythe_reach, ty - 4, STEEL_HIGH)
        p(tx + 4, ty + 1, STEEL_DARK)
        p(tx + 5 + scythe_reach, ty - 2, STEEL_BRIGHT)
        p(tx + 6 + scythe_reach, ty - 4, STEEL_HIGH)

    return arr.tobytes()


# ==============================================================================
# 3. ABOMINATION SPRITES (48x48 Colossal Stitched Meat Golem)
# ==============================================================================
def draw_abomination_frame(step, dir_idx, mode):
    """
    Renders one 48x48 frame of the colossal Scourge Abomination.
    mode: 'walk', 'attack', 'death'
    step: 0..4
    dir_idx: 0=N, 1=NE, 2=E, 3=SE, 4=S
    """
    arr = np.full((48, 48), TRANSPARENT, dtype=np.uint8)

    def p(x, y, c):
        if 0 <= x < 48 and 0 <= y < 48:
            arr[y, x] = c

    def block(x0, y0, w, h, fill, border=OUTLINE):
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                if border and (x == x0 or x == x0 + w - 1 or y == y0 or y == y0 + h - 1):
                    p(x, y, border)
                else:
                    p(x, y, fill)

    # ---------------- DEATH ANIMATION ----------------
    if mode == "death":
        prog = step
        # Colossal gore and bile puddle
        rad_x = 7 + prog * 3
        rad_y = 3 + prog
        for dy in range(-rad_y, rad_y + 1):
            for dx in range(-rad_x, rad_x + 1):
                if (dx * dx) / (rad_x * rad_x + 0.1) + (dy * dy) / (rad_y * rad_y + 0.1) <= 1.0:
                    dist = abs(dx) + abs(dy)
                    p(24 + dx, 38 + dy, BLOOD_MID if dist < 5 else (BLOOD_DARK if dist < 8 else SHADOW_DEEP))

        if prog < 3:
            # Massive bulk toppling forward
            block(15, 24 + prog * 3, 18, 12, FLESH_DARK, OUTLINE)
            # Belly rupturing
            p(24, 28 + prog * 3, BLOOD_FRESH)
            p(25, 29 + prog * 3, BLOOD_BRIGHT)
            # Cleaver clattering to side
            block(33, 30 + prog * 3, 7, 5, STEEL_HIGH, OUTLINE)
        else:
            # Flattened heap of rotting corpse flesh and severed organs
            block(12, 34, 24, 9, FLESH_DEEP, OUTLINE)
            for ox in range(16, 31, 3):
                p(ox, 36, BONE_WHITE)
                p(ox + 1, 37, BLOOD_FRESH)
                p(ox - 1, 38, FLESH_LIGHT)
            # Fallen giant butcher cleaver on the left
            block(6, 37, 7, 4, STEEL_HIGH, OUTLINE)
            p(7, 36, STEEL_BRIGHT)
            # Meat hook and chain tangled on right
            p(37, 37, STEEL_MID)
            p(38, 38, STEEL_DARK)
            p(39, 39, STEEL_BRIGHT)

        return arr.tobytes()

    # ---------------- WALK / ATTACK ANIMATIONS ----------------
    bob = [0, -1, 0, 1, 0][step]
    l_leg = [-3, 0, 3, 0, -2][step]
    r_leg = [3, 0, -3, 0, 2][step]
    swing = [0, -3, 5, 2, 0][step] if mode == "attack" else 0

    cx = 24
    cy = 24 + bob

    # 1. Broad Ground Shadow
    for sx in range(-12, 13):
        p(cx + sx, 42, SHADOW_DEEP if abs(sx) < 7 else SHADOW_MID)

    # 2. Massive Trunk Legs
    # Left leg
    block(cx - 9 + l_leg, cy + 10, 6, 8, FLESH_DEEP, OUTLINE)
    # Right leg
    block(cx + 3 + r_leg, cy + 10, 6, 8, FLESH_DARK, OUTLINE)

    # 3. Colossal Stitched Torso (Asymmetrical flesh patches)
    # Left half: Olive-green necrotic flesh
    block(cx - 11, cy - 8, 11, 18, FLESH_DARK, OUTLINE)
    # Right half: Pale decaying corpse flesh
    block(cx, cy - 8, 11, 18, FLESH_LIGHT, OUTLINE)

    # Black Surgical Rope Sutures (Vertical midline seam)
    for sy in range(cy - 7, cy + 9, 2):
        p(cx, sy, OUTLINE)
        p(cx - 1, sy, SHADOW_DEEP)
        # Cross stitches 'X'
        p(cx - 2, sy - 1, OUTLINE)
        p(cx + 2, sy + 1, OUTLINE)

    # 4. Protruding Bloated Sagging Gut
    block(cx - 7, cy + 2, 14, 9, FLESH_MID, OUTLINE)
    # Horizontal abdominal suture holding entrails
    for sx in range(cx - 5, cx + 6, 2):
        p(sx, cy + 6, OUTLINE)
        p(sx, cy + 7, BLOOD_DARK)

    # 5. Butcher's Apron (Player Team Color)
    # Apron hangs over the lower gut and hips
    for ay in range(cy + 4, cy + 12):
        span = 5 - (ay - (cy + 4)) // 2
        for ax in range(-span, span + 1):
            if ax == -span or ax == span or ay == cy + 11:
                p(cx + ax, ay, PC_DARK)
            elif ax < 0:
                p(cx + ax, ay, PC_LIGHT)
            elif ax == 0:
                p(cx + ax, ay, PC_SHINE)
            else:
                p(cx + ax, ay, PC_MID)

    # Blood splatters across the apron
    p(cx - 2, cy + 7, BLOOD_BRIGHT)
    p(cx + 1, cy + 8, BLOOD_DARK)

    # 6. Deformed Stitched Head
    hx = cx + (2 if dir_idx in (1, 2, 3) else 0)
    hy = cy - 12

    block(hx - 4, hy, 8, 6, FLESH_MID, OUTLINE)
    # Stitched jaw
    p(hx - 2, hy + 4, OUTLINE)
    p(hx, hy + 4, OUTLINE)
    p(hx + 2, hy + 4, OUTLINE)

    if dir_idx in (1, 2, 3, 4):  # Front / side views
        # Asymmetrical eyes: One glowing amber, one dead white
        p(hx - 2, hy + 2, EYE_AMBER)
        p(hx + 2, hy + 2, BONE_WHITE)
    else:  # North
        p(hx, hy + 1, FLESH_DEEP)

    # 7. Third Vestigial Skeletal Arm on Right Shoulder
    # Perched on the right collarbone, reaching forward
    p(cx + 8, cy - 9, BONE_MID)
    p(cx + 9, cy - 8, BONE_WHITE)
    p(cx + 10, cy - 7, BONE_WHITE)
    p(cx + 11, cy - 7, BONE_PALE)  # claw fingers

    # 8. Left Arm: Iron Meat Hook & Chains
    # Arm wrapped in chains, heavy curved meat hook dangling
    block(cx - 15, cy - 4, 5, 10, FLESH_DEEP, OUTLINE)
    # Chains
    p(cx - 14, cy, STEEL_MID)
    p(cx - 13, cy + 2, STEEL_LIGHT := STEEL_HIGH)
    p(cx - 14, cy + 4, STEEL_MID)
    # Curved iron meat hook
    hook_x = cx - 14
    hook_y = cy + 7 + (swing if mode == "attack" else 0)
    p(hook_x, hook_y, STEEL_HIGH)
    p(hook_x - 1, hook_y + 1, STEEL_HIGH)
    p(hook_x - 1, hook_y + 2, STEEL_MID)
    p(hook_x, hook_y + 3, STEEL_BRIGHT)
    p(hook_x + 1, hook_y + 2, STEEL_MID)  # Barb

    # 9. Right Arm: Giant Steel Butcher Cleaver
    # In attack mode: swings high overhead and chops down
    cleaver_y = cy + swing
    block(cx + 10, cy - 4, 5, 8, FLESH_LIGHT, OUTLINE)

    # Giant rectangular cleaver blade
    blade_x = cx + 14
    blade_y = cleaver_y - 2
    block(blade_x, blade_y, 7, 10, STEEL_MID, OUTLINE)
    # Razor cutting edge highlight
    for by in range(blade_y, blade_y + 10):
        p(blade_x + 6, by, STEEL_BRIGHT)
    # Blood dripping from cleaver edge
    p(blade_x + 6, blade_y + 7, BLOOD_BRIGHT)
    p(blade_x + 6, blade_y + 8, BLOOD_FRESH)
    p(blade_x + 7, blade_y + 9, BLOOD_FRESH)

    return arr.tobytes()


# ==============================================================================
# MAIN ASSET GENERATOR
# ==============================================================================
def generate_unit(name, draw_fn, tile_size, num_walk_steps, num_atk_steps, num_die_steps, unit_type):
    print(f"\nGenerating 100% Custom Scourge Unit: {name} (Tile size {tile_size}x{tile_size})...")
    pal = get_ref_palette()

    frames = []
    tags = []
    frame_idx = 0

    # 1. Walk Animation Tags & Frames (5 directions: N, NE, E, SE, S)
    dir_names = ["N", "NE", "E", "SE", "S"]
    for s in range(num_walk_steps):
        for d in range(5):
            frames.append(draw_fn(s, d, "walk"))

    # Add Aseprite tags for walking
    for d_idx, d_name in enumerate(dir_names):
        # In sequential tag view: step s, dir d -> index s*5 + d
        tags.append((f"Walk-{d_name}", d_idx, d_idx + (num_walk_steps - 1) * 5))

    # 2. Attack Animation Tags & Frames
    atk_start = len(frames)
    for s in range(num_atk_steps):
        for d in range(5):
            frames.append(draw_fn(s, d, "attack"))

    for d_idx, d_name in enumerate(dir_names):
        tags.append((f"Attack-{d_name}", atk_start + d_idx, atk_start + d_idx + (num_atk_steps - 1) * 5))

    # 3. Death Animation Tags & Frames
    die_start = len(frames)
    for s in range(num_die_steps):
        for d in range(5):
            frames.append(draw_fn(s, d, "death"))

    tags.append(("Death", die_start, len(frames) - 1))

    # Save Native Aseprite Project File
    ase_path = os.path.join(UNITS_DIR, f"{name}.aseprite")
    write_aseprite(ase_path, frames, tile_size, tile_size, pal, tags)
    print(f"Saved Native Aseprite Project: {ase_path} ({len(frames)} frames, {len(tags)} tags)")

    # Compile into Stratagus Unit Spritesheet PNG
    png_path = os.path.join(UNITS_DIR, f"{name}.png")
    compile_aseprite_to_sheet(ase_path, png_path, unit_type)


def main():
    os.makedirs(UNITS_DIR, exist_ok=True)

    # 1. Ghoul (32x32, 5 walk, 5 attack, 5 death -> 15 rows of 5)
    generate_unit("ghoul", draw_ghoul_frame, 32, 5, 5, 5, "ghoul")

    # 2. Crypt Fiend (32x32, 5 walk, 4 attack, 5 death -> 14 rows of 5)
    generate_unit("crypt_fiend", draw_crypt_fiend_frame, 32, 5, 4, 5, "crypt-fiend")

    # 3. Abomination (48x48, 5 walk, 5 attack, 5 death -> 15 rows of 5)
    generate_unit("abomination", draw_abomination_frame, 48, 5, 5, 5, "abomination")

    print("\nALL SCOURGE ASEPRITE ASSETS GENERATED & COMPILED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
