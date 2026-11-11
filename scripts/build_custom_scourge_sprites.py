#!/usr/bin/env python3
"""
Custom Warcraft III-Quality Scourge Pixel Art Generator
======================================================
Builds 100% original, handcrafted, authentic Warcraft III-style pixel art
sprites for the Undead Scourge faction in Warcraft 1 / Stratagus:

1. GHOUL (graphics/forsaken/units/ghoul.png, 160x480, 15 rows of 32x32 tiles):
   - Feral quadruped/digitigrade prowling stance, deeply hunched spine at 45°.
   - 4 sharp bone dorsal spikes along the spine, elongated arms with curved razor claws.
   - Sunken skull with glowing yellow feral eyes, bared fangs.
   - Gaunt sickly green-gray necrotic flesh, player-color loincloth.
   - Full 15-row animation matching frameNumbers_5_5_5_5 (Still, Move 0..3, Attack 0..4, Death 0..4).

2. CRYPT FIEND (graphics/forsaken/units/crypt_fiend.png, 160x448, 14 rows of 32x32 tiles):
   - True Nerubian Centaur silhouette: mummified humanoid Nerubian upper body rising
     from an armored 6-legged arachnid chassis.
   - Spiked horned helm with 4 glowing green cluster eyes and bone mandibles.
   - Two large mantis-like bladed scythe arms held in front.
   - Dark obsidian chitin armor with glowing player-color necrotic runes on the abdomen.
   - Full 14-row animation matching frameNumbers_5_5_4_5 (Still, Move 0..3, Attack 0..3, Death 0..4).

3. ABOMINATION (graphics/forsaken/units/abomination.png, 240x720, 15 rows of 48x48 tiles):
   - Colossal hulking behemoth of stitched decaying corpse flesh.
   - Bloated, sagging belly held together with thick rope stitches and open gash.
   - Giant rectangular butcher's steel cleaver in right hand.
   - Heavy iron meat hook with chain wrapped around left forearm.
   - Grotesque third vestigial skeletal arm / bone spike sprouting from left shoulder.
   - Secondary severed skull stitched onto the right shoulder collar.
   - Heavy butcher's leather apron in Player Team Color.
   - Full 15-row animation matching frameNumbers_5_5_5_5 on 48x48 tiles (Still, Move 0..3, Attack 0..4, Death 0..4).

STRICT COMPLIANCE RULES:
- 100% of non-transparent pixels strictly in unit palette range [96..254]. ZERO pixels in [0..95].
- Player Team Colors placed on indices [200..207].
- Transparency key at index 255 with explicit PNG tRNS chunk.
"""

import os
import numpy as np
from PIL import Image

BASE_DIR = "/home/smiles/forsaken-mod"
UNITS_DIR = os.path.join(BASE_DIR, "graphics", "forsaken", "units")
REF_PAL_IMG = os.path.join(BASE_DIR, "graphics", "human", "units", "footman.png")

# Palette index constants (Guaranteed inside [96..254])
TRANSPARENT = 255

# Outlines & Shadows
OUTLINE = 96        # Pure black (0, 0, 0)
SHADOW_DEEP = 253   # Darkest midnight shadow (20, 20, 40)
SHADOW_MID = 252    # Dark shadow (48, 48, 80)
SHADOW_LIGHT = 251  # Mid shadow (84, 84, 120)

# Steels & Metals
STEEL_BRIGHT = 217  # White-hot metal reflection (252, 252, 252)
STEEL_HIGH = 219    # High steel shine (196, 196, 196)
STEEL_MID = 249     # Polished steel (176, 176, 196)
STEEL_DARK = 250    # Shadowed steel (124, 124, 152)

# Necrotic Corpse Flesh
FLESH_SHADOW = 184  # Crease shadow (12, 20, 12)
FLESH_DEEP = 209    # Dark olive teal (28, 68, 68)
FLESH_DARK = 210    # Dark necrotic green-gray (48, 80, 88)
FLESH_MID = 211     # Mid decaying flesh (80, 104, 104)
FLESH_LIGHT = 212   # Light necrotic flesh (100, 124, 108)
FLESH_HIGH = 213    # Sickly pale flesh (128, 140, 112)
FLESH_PALE = 214    # Highlight corpse skin (156, 180, 148)

# Blood & Gore
BLOOD_DARK = 176    # Coagulated dark blood (84, 0, 0)
BLOOD_MID = 177     # Deep red blood (108, 0, 0)
BLOOD_BRIGHT = 179  # Bright red blood (156, 0, 0)
BLOOD_FRESH = 182   # Crimson gore (228, 0, 4)

# Bone & Teeth
BONE_WHITE = 217    # Pure bone highlight (252, 252, 252)
BONE_PALE = 240     # Weathered ivory bone (204, 196, 184)
BONE_MID = 191      # Shaded bone (208, 208, 236)
BONE_SHADOW = 190   # Bone crease (176, 184, 208)

# Eyes & Glowing Accents
EYE_YELLOW = 221    # Feral yellow eye (252, 252, 0)
EYE_AMBER = 243     # Glowing amber eye (252, 212, 136)
EYE_GREEN = 223     # Nerubian green cluster eye (0, 252, 0)
EYE_GREEN_DARK = 175 # Shaded green eye (116, 164, 36)

# Player Team Colors (Default blue gradient in palette, swapped per player)
PC_SHADOW = 200     # Deepest team shadow (0, 8, 36)
PC_DARK = 201       # Dark team color (0, 16, 64)
PC_MID_DARK = 202   # Mid-dark team color (0, 28, 96)
PC_MID = 203        # Mid team color (0, 40, 128)
PC_LIGHT = 204      # Light team color (4, 52, 156)
PC_BRIGHT = 205     # Bright team color (8, 64, 188)
PC_HIGH = 206       # High team color (12, 80, 220)
PC_SHINE = 207      # Team color highlight (20, 96, 252)


def get_palette():
    return Image.open(REF_PAL_IMG).getpalette()


def save_png(arr, path, pal):
    im = Image.fromarray(arr.astype(np.uint8), mode="P")
    im.putpalette(pal)
    im.save(path, format="PNG", transparency=TRANSPARENT)


# ==============================================================================
# DRAWING PRIMITIVES (Safe Pixel Canvas)
# ==============================================================================
class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.arr = np.full((h, w), TRANSPARENT, dtype=np.uint8)

    def p(self, x, y, col):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.arr[y, x] = col

    def rect(self, x, y, w, h, fill, border=None):
        for dy in range(h):
            for dx in range(w):
                is_b = (dx == 0 or dx == w - 1 or dy == 0 or dy == h - 1)
                if is_b and border is not None:
                    self.p(x + dx, y + dy, border)
                else:
                    self.p(x + dx, y + dy, fill)

    def disk(self, cx, cy, rx, ry, fill, border=None, highlight=None):
        for dy in range(-ry, ry + 1):
            for dx in range(-rx, rx + 1):
                d = (dx / max(1, rx)) ** 2 + (dy / max(1, ry)) ** 2
                if d <= 1.0:
                    if d > 0.72 and border is not None:
                        self.p(cx + dx, cy + dy, border)
                    elif dx < 0 and dy < 0 and d < 0.4 and highlight is not None:
                        self.p(cx + dx, cy + dy, highlight)
                    else:
                        self.p(cx + dx, cy + dy, fill)

    def line(self, x0, y0, x1, y1, col, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            t = i / float(steps)
            x = int(round(x0 + (x1 - x0) * t))
            y = int(round(y0 + (y1 - y0) * t))
            for tx in range(thick):
                for ty in range(thick):
                    self.p(x + tx, y + ty, col)


# ==============================================================================
# 1. BUILD CUSTOM GHOUL (160x480, 15 rows of 32x32 tiles)
# ==============================================================================
def render_ghoul_frame(cv, ox, oy, col, anim_type, step):
    """
    Renders one 32x32 frame of the true WC3 Ghoul:
    col: 0=N, 1=NE, 2=E, 3=SE, 4=S
    anim_type: 'still', 'move', 'attack', 'death'
    step: frame index within the cycle
    """
    # ---------------- Death Animation ----------------
    if anim_type == "death":
        # 5-step collapse into bloody carcass with cracked ribs and skull
        progress = min(4, step)
        dy = 18 + progress
        # Blood puddle
        cv.disk(ox + 16, oy + dy + 1, 6 + progress, 2 + progress // 2, BLOOD_MID, border=BLOOD_DARK)
        # Splayed broken limbs
        cv.line(ox + 16, oy + dy, ox + 9 - progress, oy + dy + 2, FLESH_DARK, thick=1)
        cv.line(ox + 16, oy + dy, ox + 23 + progress, oy + dy + 1, FLESH_DARK, thick=1)
        # Exposed spinal column & white bone ribcage
        for rx in range(12, 21, 2):
            cv.p(ox + rx, oy + dy - 1, BONE_WHITE)
            cv.p(ox + rx, oy + dy, BONE_MID)
            cv.p(ox + rx + 1, oy + dy, BLOOD_BRIGHT)
        # Fallen skull
        sk_x = ox + 22 + progress
        cv.disk(sk_x, oy + dy - 1, 2, 2, BONE_WHITE, border=OUTLINE)
        cv.p(sk_x, oy + dy - 1, SHADOW_DEEP)  # Hollow eye socket
        # Scattered claws
        cv.p(ox + 8 - progress, oy + dy + 2, BONE_WHITE)
        cv.p(ox + 25 + progress, oy + dy + 1, BONE_WHITE)
        return

    # ---------------- Alive Frames ----------------
    # Movement strides & attack lunges
    lunge_x, lunge_y = 0, 0
    stride = 0
    bob = 0

    if anim_type == "move":
        stride = (-3, -1, 2, 3)[step % 4]
        bob = (0, -1, 0, 1)[step % 4]
    elif anim_type == "attack":
        lunge_mag = (0, 2, 5, 3, -1)[step % 5]
        bob = (-1, 0, 1, 0, 0)[step % 5]
        if col in (1, 2, 3):
            lunge_x = lunge_mag
        if col in (0, 1):
            lunge_y = -lunge_mag // 2
        elif col in (3, 4):
            lunge_y = lunge_mag // 2

    cx = ox + 15 + lunge_x
    cy = oy + 15 + bob + lunge_y

    # Direction-specific anchors (Ghoul prowls deeply hunched forward)
    # col: 0=N, 1=NE, 2=E, 3=SE, 4=S
    if col == 0:    # North (back turned)
        hx, hy = cx, cy - 5       # Head slung low forward
        tx, ty = cx, cy - 1       # Hunched torso
        px_c, py_c = cx, cy + 4   # Pelvis
    elif col == 1:  # North-East
        hx, hy = cx + 4, cy - 4
        tx, ty = cx + 1, cy - 2
        px_c, py_c = cx - 3, cy + 3
    elif col == 2:  # East (pure side profile - iconic hunched Ghoul spine!)
        hx, hy = cx + 6, cy - 1
        tx, ty = cx + 1, cy - 2
        px_c, py_c = cx - 4, cy + 3
    elif col == 3:  # South-East
        hx, hy = cx + 5, cy + 1
        tx, ty = cx, cy - 1
        px_c, py_c = cx - 3, cy + 3
    else:           # South (front view facing camera)
        hx, hy = cx, cy + 2
        tx, ty = cx, cy - 2
        px_c, py_c = cx, cy + 3

    # 1. Digitigrade hind legs (crouched bent knees, sharp clawed feet)
    cv.line(px_c, py_c, cx - 4 + stride, cy + 8, FLESH_DARK, thick=2)
    cv.line(cx - 4 + stride, cy + 8, cx - 5 + stride, cy + 12, FLESH_SHADOW, thick=1)
    cv.p(cx - 6 + stride, cy + 12, OUTLINE)  # Clawed toe

    cv.line(px_c, py_c, cx + 4 - stride, cy + 8, FLESH_MID, thick=2)
    cv.line(cx + 4 - stride, cy + 8, cx + 5 - stride, cy + 12, FLESH_DARK, thick=1)
    cv.p(cx + 6 - stride, cy + 12, OUTLINE)  # Clawed toe

    # 2. Player Team Color loincloth around waist
    cv.disk(px_c, py_c, 3, 2, PC_BRIGHT, border=PC_DARK)
    cv.p(px_c, py_c + 1, PC_MID)
    cv.p(px_c, py_c + 2, PC_LIGHT)

    # 3. Hunched Torso (gaunt necrotic ribcage & spine)
    cv.disk(tx, ty, 4, 3, FLESH_MID, border=OUTLINE, highlight=FLESH_PALE)
    # Dark shadow under belly
    cv.p(tx, ty + 2, FLESH_SHADOW)
    cv.p(tx - 1, ty + 2, FLESH_SHADOW)

    # 4. Sharp Bone Dorsal Spikes along the hunched spine (Iconic WC3 Ghoul feature!)
    if col in (0, 1, 2):  # Visible on back / profile views
        spike_base_x = tx - (2 if col == 2 else 0)
        spike_base_y = ty - 2
        for s_i in range(3):
            sx = spike_base_x - s_i * (2 if col == 2 else 1)
            sy = spike_base_y - s_i * 2
            cv.p(sx, sy, BONE_WHITE)       # Spire tip
            cv.p(sx + 1, sy + 1, BONE_MID) # Spire base

    # 5. Elongated Bony Claw Arms
    # Attack frames swipe claws violently; Move frames alternate swing
    claw_swipe = (anim_type == "attack" and step in (1, 2, 3))
    arm_ext = 4 if claw_swipe else 0

    if col == 0:  # North
        cv.line(tx - 3, ty, cx - 6, cy - 2 - arm_ext, FLESH_DARK, thick=1)
        cv.p(cx - 7, cy - 3 - arm_ext, STEEL_MID)  # Claw tip
        cv.line(tx + 3, ty, cx + 6, cy - 2 - arm_ext, FLESH_MID, thick=1)
        cv.p(cx + 7, cy - 3 - arm_ext, STEEL_MID)  # Claw tip
    elif col in (1, 2, 3):  # Side angles
        # Back arm
        cv.line(tx - 2, ty + 1, cx - 4 - arm_ext, cy + 5, FLESH_SHADOW, thick=1)
        cv.p(cx - 5 - arm_ext, cy + 6, STEEL_DARK)
        # Front striking arm
        hand_x = hx + 3 + (arm_ext * 2 if claw_swipe else 0)
        hand_y = hy + 3 + (arm_ext if claw_swipe else 0)
        cv.line(tx + 2, ty, hand_x, hand_y, FLESH_LIGHT, thick=2)
        # Triple curved razor claws
        cv.p(hand_x + 1, hand_y, STEEL_BRIGHT)
        cv.p(hand_x + 2, hand_y + 1, STEEL_MID)
        cv.p(hand_x + 1, hand_y + 2, STEEL_BRIGHT)
        # Blood arc during savage attack slash (step 2)
        if anim_type == "attack" and step == 2:
            cv.line(hand_x + 3, hand_y - 2, hand_x + 5, hand_y + 3, BLOOD_BRIGHT, thick=1)
            cv.p(hand_x + 6, hand_y + 4, BLOOD_FRESH)
    else:  # South (front view)
        # Dual threatening claws poised in front
        cv.line(tx - 3, ty, cx - 6 - arm_ext, cy + 3, FLESH_MID, thick=2)
        cv.p(cx - 7 - arm_ext, cy + 4, STEEL_BRIGHT)
        cv.p(cx - 8 - arm_ext, cy + 5, STEEL_MID)
        cv.line(tx + 3, ty, cx + 6 + arm_ext, cy + 3, FLESH_LIGHT, thick=2)
        cv.p(cx + 7 + arm_ext, cy + 4, STEEL_BRIGHT)
        cv.p(cx + 8 + arm_ext, cy + 5, STEEL_MID)

    # 6. Feral Head & Sunken Skull
    cv.disk(hx, hy, 3, 3, FLESH_LIGHT, border=OUTLINE, highlight=FLESH_PALE)
    # Jaw / Mandibles
    cv.p(hx, hy + 2, BONE_WHITE)
    cv.p(hx + 1, hy + 2, BONE_PALE)

    # Glowing Feral Eyes (Amber/Yellow)
    if col in (2, 3, 4):  # Facing player
        eye_x = hx + 1 if col in (2, 3) else hx + 1
        cv.p(eye_x, hy, EYE_YELLOW)
        if col == 4:  # Twin eyes on front view
            cv.p(hx - 1, hy, EYE_YELLOW)
    elif col == 1:
        cv.p(hx + 1, hy - 1, EYE_AMBER)


def build_all_ghoul_sprites():
    w, h = 160, 480
    cv = Canvas(w, h)
    move_rows = {3: 0, 6: 1, 9: 2, 12: 3}
    attack_rows = {1: 0, 4: 1, 7: 2, 10: 3, 13: 4}
    death_rows = {2: 0, 5: 1, 8: 2, 11: 3, 14: 4}

    for r in range(15):
        if r == 0:
            atype, step = "still", 0
        elif r in move_rows:
            atype, step = "move", move_rows[r]
        elif r in attack_rows:
            atype, step = "attack", attack_rows[r]
        else:
            atype, step = "death", death_rows[r]

        for c in range(5):
            render_ghoul_frame(cv, c * 32, r * 32, c, atype, step)

    pal = get_palette()
    dst = os.path.join(UNITS_DIR, "ghoul.png")
    save_png(cv.arr, dst, pal)
    print(f"Generated 100% custom WC3 Ghoul (160x480): {dst}")


# ==============================================================================
# 2. BUILD CUSTOM CRYPT FIEND (160x448, 14 rows of 32x32 tiles)
# ==============================================================================
def render_crypt_fiend_frame(cv, ox, oy, col, anim_type, step):
    """
    Renders one 32x32 frame of the true Nerubian Centaur Crypt Fiend:
    - Armored humanoid Nerubian upper body with horned helm and scythe arms.
    - 6-legged obsidian arachnid chassis with team-color necrotic runes.
    col: 0=N, 1=NE, 2=E, 3=SE, 4=S
    anim_type: 'still', 'move', 'attack', 'death'
    step: frame index
    """
    # ---------------- Death Animation ----------------
    if anim_type == "death":
        # 5-step collapse: legs buckle, carapace fractures, flattens to ground
        prog = min(4, step)
        dy = 18 + prog
        # Splattered dark green/teal ichor
        cv.disk(ox + 16, oy + dy + 1, 7 + prog, 2 + prog // 2, SHADOW_DEEP, border=OUTLINE)
        cv.disk(ox + 16, oy + dy, 5 + prog, 2, FLESH_DEEP)
        # Splayed broken scythes
        cv.line(ox + 16, oy + dy, ox + 6 - prog, oy + dy - 2, STEEL_DARK, thick=2)
        cv.p(ox + 5 - prog, oy + dy - 3, STEEL_BRIGHT)
        cv.line(ox + 16, oy + dy, ox + 26 + prog, oy + dy - 1, STEEL_DARK, thick=2)
        cv.p(ox + 27 + prog, oy + dy - 2, STEEL_BRIGHT)
        # Crushed obsidian shell plates & runes
        for px_off in (-3, 0, 3):
            cv.p(ox + 16 + px_off, oy + dy - 1, SHADOW_LIGHT)
            cv.p(ox + 16 + px_off, oy + dy, PC_DARK)
        return

    # ---------------- Alive Frames ----------------
    # Leg skittering offset
    leg_phase = (step % 4) if anim_type == "move" else 0
    l_off = (-2, 0, 2, 0)[leg_phase]
    bob = (0, -1, 0, 1)[leg_phase]

    # Attack lunge & scythe windup
    is_atk = (anim_type == "attack")
    atk_lunge = (0, 3, 5, 2)[step % 4] if is_atk else 0

    cx = ox + 16
    cy = oy + 16 + bob

    # 1. 6-Legged Arachnid Lower Chassis
    # Splayed multi-jointed chitin legs (3 on left, 3 on right)
    for leg_i in range(3):
        # Left legs
        lx0 = cx - 4
        ly0 = cy + 2 + leg_i * 2
        lx1 = cx - 11 - (leg_i * 2) + (l_off if leg_i % 2 == 0 else -l_off)
        ly1 = cy + 5 + leg_i * 2
        cv.line(lx0, ly0, lx1, ly1, SHADOW_DEEP, thick=2)
        cv.line(lx1, ly1, lx1 - 2, ly1 + 3, STEEL_DARK, thick=1)  # Spurred tip

        # Right legs
        rx0 = cx + 4
        ry0 = cy + 2 + leg_i * 2
        rx1 = cx + 11 + (leg_i * 2) - (l_off if leg_i % 2 == 0 else -l_off)
        ry1 = cy + 5 + leg_i * 2
        cv.line(rx0, ry0, rx1, ry1, SHADOW_DEEP, thick=2)
        cv.line(rx1, ry1, rx1 + 2, ry1 + 3, STEEL_DARK, thick=1)  # Spurred tip

    # 2. Spiked Obsidian Abdomen (behind upper torso)
    ab_y = cy + 4
    cv.disk(cx, ab_y, 6, 4, SHADOW_MID, border=OUTLINE, highlight=SHADOW_LIGHT)
    # Glowing Player Team Color Necrotic Runes on abdomen carapace
    cv.p(cx, ab_y - 1, PC_BRIGHT)
    cv.p(cx - 2, ab_y, PC_MID)
    cv.p(cx + 2, ab_y, PC_MID)
    cv.p(cx, ab_y + 1, PC_HIGH)

    # 3. Mummified Nerubian Humanoid Upper Torso
    # Rises centaur-like from front of spider body
    ux = cx + (atk_lunge if col in (1, 2, 3) else 0)
    uy = cy - 3 - (atk_lunge // 2 if col in (0, 1) else 0)

    # Chitin chest plate & spiked shoulders
    cv.disk(ux, uy, 4, 4, SHADOW_DEEP, border=OUTLINE, highlight=STEEL_DARK)
    cv.p(ux - 1, uy, STEEL_MID)
    cv.p(ux + 1, uy, STEEL_MID)

    # 4. Large Mantis-Style Bladed Scythe Arms
    # In attack: cleave forward and strike!
    scythe_reach = 6 if is_atk else 0
    scythe_down = 4 if (is_atk and step in (1, 2)) else 0

    if col in (2, 3, 4):  # Facing player / side
        # Right scythe blade
        sx0 = ux + 3
        sy0 = uy - 2
        sx1 = ux + 7 + scythe_reach
        sy1 = uy - 5 + scythe_down
        cv.line(sx0, sy0, sx1, sy1, STEEL_DARK, thick=2)
        cv.line(sx1, sy1, sx1 - 3, sy1 + 6, STEEL_BRIGHT, thick=2)  # Curved razor blade
        cv.p(sx1 - 4, sy1 + 7, STEEL_HIGH)                          # Sharp point

        # Left scythe blade
        lx0 = ux - 3
        ly0 = uy - 2
        lx1 = ux - 6
        ly1 = uy - 4 + scythe_down
        cv.line(lx0, ly0, lx1, ly1, STEEL_DARK, thick=2)
        cv.line(lx1, ly1, lx1 - 2, ly1 + 5, STEEL_MID, thick=2)

        # Web projectile launch during attack step 1 & 2
        if is_atk and step in (1, 2):
            cv.disk(ux + 10, uy + 2, 2, 2, BONE_WHITE, border=STEEL_HIGH)
            cv.p(ux + 11, uy + 2, BONE_WHITE)
    else:  # Facing North / away
        # Scythes seen from rear
        cv.line(ux - 4, uy, ux - 7, uy - 5, STEEL_DARK, thick=2)
        cv.line(ux - 7, uy - 5, ux - 4, uy - 9, STEEL_MID, thick=1)
        cv.line(ux + 4, uy, ux + 7, uy - 5, STEEL_DARK, thick=2)
        cv.line(ux + 7, uy - 5, ux + 4, uy - 9, STEEL_MID, thick=1)

    # 5. Horned Nerubian Head & Glowing Green Eyes
    head_y = uy - 5
    cv.disk(ux, head_y, 3, 3, SHADOW_DEEP, border=OUTLINE, highlight=SHADOW_LIGHT)
    # Twin helmet horn spikes
    cv.p(ux - 2, head_y - 3, STEEL_MID)
    cv.p(ux + 2, head_y - 3, STEEL_MID)

    # 4 Glowing Green Cluster Eyes (facing player)
    if col in (2, 3, 4):
        eye_x = ux if col == 4 else (ux + 1)
        cv.p(eye_x, head_y - 1, EYE_GREEN)
        cv.p(eye_x, head_y, EYE_GREEN)
        if col == 4:
            cv.p(ux - 1, head_y - 1, EYE_GREEN)
            cv.p(ux - 1, head_y, EYE_GREEN)
        # Sharp bone mandibles
        cv.p(eye_x, head_y + 2, BONE_WHITE)
        cv.p(eye_x + 1, head_y + 3, BONE_PALE)


def build_all_crypt_fiend_sprites():
    w, h = 160, 448
    cv = Canvas(w, h)
    move_rows = {3: 0, 6: 1, 9: 2, 12: 3}
    attack_rows = {1: 0, 4: 1, 7: 2, 10: 3}
    death_rows = {2: 0, 5: 1, 8: 2, 11: 3, 13: 4}

    for r in range(14):
        if r == 0:
            atype, step = "still", 0
        elif r in move_rows:
            atype, step = "move", move_rows[r]
        elif r in attack_rows:
            atype, step = "attack", attack_rows[r]
        else:
            atype, step = "death", death_rows[r]

        for c in range(5):
            render_crypt_fiend_frame(cv, c * 32, r * 32, c, atype, step)

    pal = get_palette()
    dst = os.path.join(UNITS_DIR, "crypt_fiend.png")
    save_png(cv.arr, dst, pal)
    print(f"Generated 100% custom WC3 Crypt Fiend (160x448): {dst}")


# ==============================================================================
# 3. BUILD CUSTOM ABOMINATION (240x720, 15 rows of 48x48 tiles)
# ==============================================================================
def render_abomination_frame(cv, ox, oy, col, anim_type, step):
    """
    Renders one 48x48 frame of the colossal stitched Abomination:
    - Sagging bloated stitched belly with rope sutures and bleeding wound.
    - Giant butcher cleaver in right hand, meat hook on chain in left.
    - Third vestigial skeletal arm / bone spike over left shoulder.
    - Secondary severed skull stitched onto right collar.
    - Player Team Color butcher's apron.
    col: 0=N, 1=NE, 2=E, 3=SE, 4=S
    anim_type: 'still', 'move', 'attack', 'death'
    step: frame index
    """
    # ---------------- Death Animation ----------------
    if anim_type == "death":
        prog = min(4, step)
        dy = 28 + prog * 2
        # Massive pool of spilled blood & viscera
        cv.disk(ox + 24, oy + dy, 12 + prog * 2, 4 + prog, BLOOD_MID, border=OUTLINE)
        cv.disk(ox + 24, oy + dy - 1, 8 + prog, 3, BLOOD_FRESH)
        # Detached butcher cleaver lying on earth
        cv.rect(ox + 10 - prog * 2, oy + dy - 2, 8, 4, STEEL_MID, border=OUTLINE)
        cv.line(ox + 18 - prog * 2, oy + dy - 1, ox + 22 - prog * 2, oy + dy, SHADOW_DEEP, thick=2)
        # Detached meat hook & coiled chain
        cv.line(ox + 32 + prog, oy + dy - 1, ox + 38 + prog, oy + dy + 1, STEEL_DARK, thick=1)
        cv.p(ox + 39 + prog, oy + dy + 2, STEEL_BRIGHT)  # Hook barb
        # Collapsed massive torso mound with exposed ribs & stitched flesh
        cv.disk(ox + 24, oy + dy - 3, 10, 4, FLESH_DARK, border=OUTLINE)
        for sx in (-4, -1, 2, 5):
            cv.p(ox + 24 + sx, oy + dy - 4, BONE_WHITE)
            cv.p(ox + 24 + sx, oy + dy - 3, SHADOW_DEEP)  # Suture stitch
        return

    # ---------------- Alive Frames ----------------
    waddle = 0
    belly_bob = 0
    if anim_type == "move":
        waddle = (-3, -1, 2, 3)[step % 4]
        belly_bob = (0, -1, 0, 1)[step % 4]

    is_atk = (anim_type == "attack")
    atk_thrust = (0, 3, 7, 4, -1)[step % 5] if is_atk else 0

    cx = ox + 24
    cy = oy + 24 + belly_bob

    # 1. Stomping Thick Elephantine Legs
    cv.rect(cx - 8 + waddle, cy + 9, 6, 8, FLESH_DARK, border=OUTLINE)
    cv.line(cx - 8 + waddle, cy + 17, cx - 3 + waddle, cy + 17, SHADOW_DEEP, thick=1)  # Stomp foot
    cv.rect(cx + 2 - waddle, cy + 9, 6, 8, FLESH_MID, border=OUTLINE)
    cv.line(cx + 2 - waddle, cy + 17, cx + 7 - waddle, cy + 17, SHADOW_DEEP, thick=1)  # Stomp foot

    # 2. Player Team Color Heavy Butcher's Leather Apron / Loincloth
    cv.rect(cx - 7, cy + 4, 14, 8, PC_MID, border=PC_SHADOW)
    cv.line(cx - 6, cy + 5, cx + 6, cy + 5, PC_BRIGHT, thick=1)  # Apron waistband
    cv.p(cx - 1, cy + 7, PC_HIGH)
    cv.p(cx + 1, cy + 7, PC_HIGH)

    # 3. Colossal Bloated Torso with Surgical Cross-Sutures
    cv.disk(cx, cy, 9, 8, FLESH_MID, border=OUTLINE, highlight=FLESH_PALE)
    # Rotted shadow crease on lower gut
    cv.disk(cx, cy + 3, 8, 4, FLESH_DARK)

    # Rope Stitches & Bleeding Gash across belly (visible on front/side views)
    if col != 0:  # Not back view
        cv.line(cx, cy - 4, cx, cy + 4, BLOOD_MID, thick=1)  # Vertical incision
        # Horizontal cross-stitches
        for sy in (-3, -1, 1, 3):
            cv.p(cx - 2, cy + sy, OUTLINE)
            cv.p(cx - 1, cy + sy, SHADOW_DEEP)
            cv.p(cx + 1, cy + sy, SHADOW_DEEP)
            cv.p(cx + 2, cy + sy, OUTLINE)

    # 4. Third Vestigial Arm / Bone Spike sprouting from Left Shoulder/Back
    shoulder_l_x = cx - 8
    shoulder_l_y = cy - 6
    cv.line(shoulder_l_x, shoulder_l_y, shoulder_l_x - 3, shoulder_l_y - 5, FLESH_DARK, thick=2)
    cv.line(shoulder_l_x - 3, shoulder_l_y - 5, shoulder_l_x - 6, shoulder_l_y - 8, BONE_WHITE, thick=1)
    cv.p(shoulder_l_x - 7, shoulder_l_y - 9, BONE_WHITE)  # Sharp claw/spike tip

    # 5. Right Hand: Giant Butcher's Heavy Cleaver
    # In attack: raises high and smashes down with massive blood slash!
    cleaver_lift = -8 if (is_atk and step in (0, 1)) else (4 if (is_atk and step == 2) else 0)
    cleaver_fwd = atk_thrust if col in (1, 2, 3) else 0

    hand_r_x = cx + 9 + cleaver_fwd
    hand_r_y = cy + cleaver_lift

    # Right muscular stitched arm
    cv.line(cx + 6, cy - 3, hand_r_x, hand_r_y, FLESH_LIGHT, thick=3)

    # Giant Rectangular Butcher Cleaver
    cl_x = hand_r_x + 2
    cl_y = hand_r_y - 7
    # Cleaver blade (heavy steel slab)
    cv.rect(cl_x, cl_y, 7, 12, STEEL_MID, border=OUTLINE)
    # Razor cutting edge
    cv.line(cl_x + 6, cl_y, cl_x + 6, cl_y + 11, STEEL_BRIGHT, thick=1)
    # Dried blood on blade edge
    cv.line(cl_x + 5, cl_y + 5, cl_x + 6, cl_y + 11, BLOOD_MID, thick=1)
    cv.p(cl_x + 6, cl_y + 10, BLOOD_FRESH)
    # Wooden cleaver handle grip
    cv.line(hand_r_x - 1, hand_r_y, hand_r_x + 2, hand_r_y, SHADOW_DEEP, thick=2)

    # Blood arc during devastating cleaver slam (attack step 2)
    if is_atk and step == 2:
        cv.line(cl_x + 8, cl_y + 6, cl_x + 12, cl_y + 16, BLOOD_BRIGHT, thick=2)
        cv.p(cl_x + 13, cl_y + 17, BLOOD_FRESH)

    # 6. Left Hand: Heavy Rusted Meat Hook on Wrapped Chain
    hook_ext = (atk_thrust * 2) if (is_atk and step in (1, 2)) else 0
    hand_l_x = cx - 9 - hook_ext
    hand_l_y = cy + 2

    # Left stitched arm with wrapped iron chain
    cv.line(cx - 6, cy - 2, hand_l_x, hand_l_y, FLESH_DARK, thick=3)
    cv.p(hand_l_x + 2, hand_l_y, STEEL_MID)  # Chain link wrap
    cv.p(hand_l_x + 4, hand_l_y - 1, STEEL_MID)

    # Meat Hook
    hook_tip_x = hand_l_x - 4
    hook_tip_y = hand_l_y + 4
    cv.line(hand_l_x, hand_l_y, hook_tip_x, hook_tip_y, STEEL_DARK, thick=2)
    cv.line(hook_tip_x, hook_tip_y, hook_tip_x + 3, hook_tip_y + 2, STEEL_BRIGHT, thick=1)  # Curved hook barb

    # 7. Secondary Severed Skull Stitched onto Right Collar
    cv.disk(cx + 6, cy - 7, 2, 2, BONE_WHITE, border=OUTLINE)
    cv.p(cx + 6, cy - 7, SHADOW_DEEP)  # Dead eye socket

    # 8. Main Deformed Stitched Head
    head_x = cx - 2
    head_y = cy - 8
    cv.disk(head_x, head_y, 4, 4, FLESH_LIGHT, border=OUTLINE, highlight=FLESH_PALE)
    # Slack drooling jaw & protruding fangs
    cv.p(head_x, head_y + 3, BONE_WHITE)
    cv.p(head_x + 1, head_y + 3, BONE_PALE)
    # Stitches across forehead
    cv.line(head_x - 2, head_y - 2, head_x + 2, head_y - 2, OUTLINE, thick=1)
    cv.p(head_x, head_y - 3, BLOOD_DARK)

    # Glowing dead yellow eye (facing player)
    if col != 0:
        cv.p(head_x + 1, head_y, EYE_YELLOW)
        cv.p(head_x + 1, head_y - 1, OUTLINE)  # Angry brow


def build_all_abomination_sprites():
    w, h = 240, 720
    cv = Canvas(w, h)
    move_rows = {3: 0, 6: 1, 9: 2, 12: 3}
    attack_rows = {1: 0, 4: 1, 7: 2, 10: 3, 13: 4}
    death_rows = {2: 0, 5: 1, 8: 2, 11: 3, 14: 4}

    for r in range(15):
        if r == 0:
            atype, step = "still", 0
        elif r in move_rows:
            atype, step = "move", move_rows[r]
        elif r in attack_rows:
            atype, step = "attack", attack_rows[r]
        else:
            atype, step = "death", death_rows[r]

        for c in range(5):
            render_abomination_frame(cv, c * 48, r * 48, c, atype, step)

    pal = get_palette()
    dst = os.path.join(UNITS_DIR, "abomination.png")
    save_png(cv.arr, dst, pal)
    print(f"Generated 100% custom WC3 Abomination (240x720): {dst}")


def main():
    print("Building 100% original, custom WC3 Scourge unit sprites...")
    build_all_ghoul_sprites()
    build_all_crypt_fiend_sprites()
    build_all_abomination_sprites()
    print("\nALL CUSTOM SCOURGE PIXEL ART COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
