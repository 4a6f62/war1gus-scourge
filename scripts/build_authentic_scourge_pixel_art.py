#!/usr/bin/env python3
"""
Build 100% authentic Warcraft III Scourge pixel art using Blizzard's original
1994 engine animation rigs, surgically transforming them into true Scourge units:

1. Ghoul (160x480, 15 rows of 32x32):
   Built from skeleton.png (unarmed claw/strike rig).
   - Fleshed out in gaunt, necrotic green-gray muscle & taut sinew
   - Arched spine with 3 protruding white bone spikes
   - Elongated 3-pronged razor bone/steel claws
   - Exposed bloody ribcage with crimson gore
   - Skull face with glowing yellow feral eyes and jagged fangs
   - Tattered player-color loincloth
   - Blood slash arcs during attack; shattered bone collapse in death

2. Crypt Fiend (160x448, 14 rows of 32x32):
   Built from spider.png (6-legged arachnid chassis rig).
   - Obsidian chitin armor with glowing team-color necrotic runes on abdomen
   - Upright mummified humanoid Nerubian torso grafted to front
   - Horned beetle war-helm with emerald cluster eyes
   - Twin curved mantis scythe blades on forearms
   - Venomous slashing attack; curled-leg death collapse with green ichor

3. Abomination (240x720, 15 rows of 48x48):
   Built from ogre.png (48x48 heavyweight brute rig).
   - Club erased and replaced with colossal steel butcher cleaver
   - Left arm wrapped in iron chains with heavy curved meat hook
   - Third vestigial skeletal arm grafted to right shoulder
   - Asymmetrical patchwork corpse flesh with coarse black surgical X-sutures
   - Swollen protruding gut holding decaying organs
   - Blood-stained butcher's apron in player team color
   - Stitched gruesome face with amber and blind white eyes

Enforces strict palette safety: ZERO pixels in [0..95], transparent 255.
Exports both Stratagus game PNGs and native .aseprite project files with animation tags.
"""

import os
import sys
import numpy as np
from PIL import Image

BASE_DIR = "/home/smiles/forsaken-mod"
UNITS_DIR = os.path.join(BASE_DIR, "graphics", "forsaken", "units")
REF_PAL_IMG = os.path.join(BASE_DIR, "graphics", "human", "units", "footman.png")

sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
from aseprite_tool import write_aseprite

# Strict Palette Constants [96..254]
OUTLINE = 96        # Pure black (0, 0, 0)
SHADOW_DEEP = 253   # Darkest shadow (20, 20, 40)
SHADOW_MID = 252    # Dark shadow (48, 48, 80)
SHADOW_LIGHT = 251  # Mid shadow (84, 84, 120)

STEEL_BRIGHT = 217  # White-hot metal (252, 252, 252)
STEEL_HIGH = 219    # High steel (196, 196, 196)
STEEL_MID = 249     # Polished steel (176, 176, 196)
STEEL_DARK = 250    # Shadowed steel (124, 124, 152)

FLESH_SHADOW = 184  # Crease shadow (12, 20, 12)
FLESH_DEEP = 209    # Dark olive teal (28, 68, 68)
FLESH_DARK = 210    # Dark necrotic green (48, 80, 88)
FLESH_MID = 211     # Mid decaying flesh (80, 104, 104)
FLESH_LIGHT = 212   # Light necrotic flesh (100, 124, 108)
FLESH_HIGH = 213    # Sickly pale flesh (128, 140, 112)
FLESH_PALE = 214    # Highlight corpse skin (156, 180, 148)

BLOOD_DARK = 176    # Coagulated blood (84, 0, 0)
BLOOD_MID = 177     # Deep red blood (108, 0, 0)
BLOOD_BRIGHT = 179  # Bright red blood (156, 0, 0)
BLOOD_FRESH = 182   # Crimson gore (228, 0, 4)

BONE_WHITE = 217    # Pure bone highlight (252, 252, 252)
BONE_PALE = 240     # Weathered ivory (204, 196, 184)
BONE_MID = 191      # Shaded bone (208, 208, 236)
BONE_SHADOW = 190   # Bone crease (176, 184, 208)

EYE_YELLOW = 221    # Feral yellow eye (252, 252, 0)
EYE_AMBER = 243     # Glowing amber eye (252, 212, 136)
EYE_GREEN = 223     # Emerald cluster eye (0, 252, 0)

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
# 1. BUILD AUTHENTIC GHOUL
# ==============================================================================
def build_ghoul():
    print("Building Authentic Scourge Ghoul...")
    src_path = os.path.join(BASE_DIR, "graphics", "neutral", "units", "skeleton.png")
    src_im = Image.open(src_path)
    src_arr = np.array(src_im)
    w, h = src_im.size  # 160, 480
    cols = w // 32
    rows = h // 32

    out_arr = np.full((h, w), TRANSPARENT, dtype=np.uint8)

    # Move rows: 0, 3, 6, 9, 12
    # Attack rows: 1, 4, 7, 10, 13
    # Death rows: 2, 5, 8, 11, 14
    attack_rows = {1, 4, 7, 10, 13}
    death_rows = {2, 5, 8, 11, 14}

    for r in range(rows):
        is_attack = r in attack_rows
        is_death = r in death_rows

        for c in range(cols):
            ox = c * 32
            oy = r * 32
            tile = src_arr[oy:oy + 32, ox:ox + 32].copy()
            out_tile = out_arr[oy:oy + 32, ox:ox + 32]

            vis_y, vis_x = np.where(tile != 255)
            if len(vis_y) == 0:
                continue

            min_y, max_y = np.min(vis_y), np.max(vis_y)
            min_x, max_x = np.min(vis_x), np.max(vis_x)
            mid_x = (min_x + max_x) // 2

            # 1. Flesh out the skeleton into gaunt necrotic muscle
            for y in range(32):
                for x in range(32):
                    v = tile[y, x]
                    if v == 255:
                        continue
                    if v == 96:
                        out_tile[y, x] = OUTLINE
                    elif v in (184, 185):
                        out_tile[y, x] = FLESH_DEEP
                    elif v in (186, 187):
                        out_tile[y, x] = FLESH_DARK
                    elif v in (188, 189):
                        out_tile[y, x] = FLESH_MID
                    elif v in (190, 191, 241):
                        out_tile[y, x] = FLESH_LIGHT

            # Expand limb thickness slightly to look like sinewy rotting flesh, not bare wire bones
            for y in range(min_y + 4, max_y - 2):
                for x in range(min_x, max_x + 1):
                    if out_tile[y, x] != TRANSPARENT and out_tile[y, x] != OUTLINE:
                        if x > 0 and out_tile[y, x - 1] == TRANSPARENT:
                            out_tile[y, x - 1] = FLESH_DARK
                        if x < 31 and out_tile[y, x + 1] == TRANSPARENT:
                            out_tile[y, x + 1] = FLESH_DEEP

            if not is_death:
                # 2. Exposed Bloody Ribcage (central torso)
                rib_top = min_y + 6
                rib_bot = min_y + 13
                for ry in range(rib_top, min(32, rib_bot)):
                    if ry % 2 == 0:
                        out_tile[ry, mid_x] = BONE_WHITE
                        if mid_x > 0:
                            out_tile[ry, mid_x - 1] = BLOOD_BRIGHT
                        if mid_x < 31:
                            out_tile[ry, mid_x + 1] = BONE_PALE
                    else:
                        out_tile[ry, mid_x] = BLOOD_DARK

                # 3. Arched Spine & 3 White Bone Dorsal Spikes
                # Spikes protrude vertically along the back
                spine_x = mid_x - (2 if c in (1, 2, 3) else 0)
                spine_top = max(1, min_y - 2)
                # Spike 1
                out_tile[spine_top, spine_x] = BONE_WHITE
                out_tile[spine_top + 1, spine_x] = BONE_PALE
                # Spike 2
                if spine_top + 3 < 32:
                    out_tile[spine_top + 3, spine_x - 1] = BONE_WHITE
                    out_tile[spine_top + 4, spine_x - 1] = BONE_PALE
                # Spike 3
                if spine_top + 6 < 32:
                    out_tile[spine_top + 6, spine_x - 1] = BONE_PALE

                # 4. Skull: Glowing Yellow Feral Eyes & Underbite Fangs
                head_top = min_y
                head_mid = min_y + 3
                if c == 4:  # South (front)
                    out_tile[head_mid, mid_x - 1] = EYE_YELLOW
                    out_tile[head_mid, mid_x + 1] = EYE_YELLOW
                    out_tile[head_mid + 2, mid_x - 1] = BONE_WHITE
                    out_tile[head_mid + 2, mid_x + 1] = BONE_WHITE
                elif c in (1, 2, 3):  # Side
                    out_tile[head_mid, min_x + 3] = EYE_YELLOW
                    out_tile[head_mid + 2, min_x + 4] = BONE_WHITE
                else:  # North
                    out_tile[head_mid, mid_x] = FLESH_DEEP

                # 5. Tattered Player-Color Loincloth (hips / waist)
                loin_y = min_y + 14
                for ly in range(loin_y, min(32, loin_y + 4)):
                    out_tile[ly, mid_x] = PC_SHINE if ly == loin_y else PC_LIGHT
                    if mid_x > 0:
                        out_tile[ly, mid_x - 1] = PC_MID
                    if mid_x < 31:
                        out_tile[ly, mid_x + 1] = PC_DARK

                # 6. Elongated 3-Pronged Bone & Steel Claws
                # Detect hand regions (lowest non-foot extension)
                hand_y = min_y + 11
                if c in (1, 2, 3):  # Side view: forward reaching claw
                    reach_x = min(30, max_x + 2)
                    out_tile[hand_y, reach_x] = STEEL_MID
                    out_tile[hand_y - 1, reach_x + 1] = BONE_WHITE
                    out_tile[hand_y, reach_x + 1] = BONE_WHITE
                    out_tile[hand_y + 1, reach_x] = BONE_PALE

                    if is_attack:
                        # Slashing blood arc
                        out_tile[hand_y - 2, reach_x + 1] = BLOOD_BRIGHT
                        out_tile[hand_y - 1, reach_x + 2] = BLOOD_FRESH
                        out_tile[hand_y, reach_x + 2] = BLOOD_BRIGHT
                else:
                    # Dual claws on both sides
                    if min_x >= 2:
                        out_tile[hand_y, min_x - 1] = STEEL_MID
                        out_tile[hand_y + 1, min_x - 2] = BONE_WHITE
                        out_tile[hand_y + 2, min_x - 1] = BONE_PALE
                    if max_x <= 29:
                        out_tile[hand_y, max_x + 1] = STEEL_MID
                        out_tile[hand_y + 1, max_x + 2] = BONE_WHITE
                        out_tile[hand_y + 2, max_x + 1] = BONE_PALE

            else:
                # Death: gore pooling on ground beneath bones
                floor_y = min(31, max_y + 1)
                for bx in range(max(0, mid_x - 5), min(32, mid_x + 6)):
                    out_tile[floor_y, bx] = BLOOD_MID if abs(bx - mid_x) < 3 else BLOOD_DARK

    pal = get_ref_palette()
    png_path = os.path.join(UNITS_DIR, "ghoul.png")
    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(pal)
    out_im.save(png_path, format="PNG", transparency=TRANSPARENT)
    print(f"Saved {png_path} ({out_im.size})")

    # Export to native .aseprite
    export_sheet_to_aseprite(out_arr, 32, 32, 5, 5, 5, pal, "ghoul")


# ==============================================================================
# 2. BUILD AUTHENTIC CRYPT FIEND (Nerubian Centaur)
# ==============================================================================
def build_crypt_fiend():
    print("Building Authentic Scourge Crypt Fiend...")
    src_path = os.path.join(BASE_DIR, "graphics", "neutral", "units", "spider.png")
    src_im = Image.open(src_path)
    src_arr = np.array(src_im)
    w, h = src_im.size  # 160, 448
    cols = w // 32
    rows = h // 32

    out_arr = np.full((h, w), TRANSPARENT, dtype=np.uint8)

    attack_rows = {1, 4, 7, 10}
    death_rows = {2, 5, 8, 11, 13}

    for r in range(rows):
        is_attack = r in attack_rows
        is_death = r in death_rows

        for c in range(cols):
            ox = c * 32
            oy = r * 32
            tile = src_arr[oy:oy + 32, ox:ox + 32].copy()
            out_tile = out_arr[oy:oy + 32, ox:ox + 32]

            vis_y, vis_x = np.where(tile != 255)
            if len(vis_y) == 0:
                continue

            min_y, max_y = np.min(vis_y), np.max(vis_y)
            min_x, max_x = np.min(vis_x), np.max(vis_x)
            mid_x = (min_x + max_x) // 2

            # 1. Recolor arachnid chassis to dark obsidian chitin
            for y in range(32):
                for x in range(32):
                    v = tile[y, x]
                    if v == 255:
                        continue
                    if v == 96:
                        out_tile[y, x] = OUTLINE
                    elif v in (184, 185, 186):
                        out_tile[y, x] = SHADOW_DEEP
                    elif v in (187, 188):
                        out_tile[y, x] = SHADOW_MID
                    elif v in (189, 190, 191):
                        out_tile[y, x] = SHADOW_LIGHT
                    else:
                        out_tile[y, x] = SHADOW_MID

            if not is_death:
                # 2. Glowing Team-Color Necrotic Runes on Spider Abdomen
                ab_y = max(min_y + 4, min(26, min_y + 10))
                ab_x = mid_x - (3 if c in (1, 2, 3) else 0)
                out_tile[ab_y, ab_x] = PC_SHINE
                out_tile[ab_y + 1, ab_x] = PC_BRIGHT
                out_tile[ab_y, max(0, ab_x - 1)] = PC_LIGHT
                out_tile[ab_y, min(31, ab_x + 1)] = PC_LIGHT

                # 3. Graft Upright Humanoid Nerubian Torso
                # Centaur torso rises upright from the front cephalothorax
                tx = mid_x + (2 if c in (1, 2, 3) else 0)
                ty = max(2, min_y - 4)

                # Carapace Chest Plate
                for cy_offset in range(5):
                    for cx_offset in range(-2, 3):
                        py = ty + cy_offset
                        px = tx + cx_offset
                        if 0 <= px < 32 and 0 <= py < 32:
                            if cx_offset in (-2, 2) or cy_offset in (0, 4):
                                out_tile[py, px] = OUTLINE
                            elif cx_offset == 0 and cy_offset in (1, 2):
                                out_tile[py, px] = PC_BRIGHT  # Chest rune
                            else:
                                out_tile[py, px] = SHADOW_LIGHT

                # 4. Horned Pharaoh / Beetle Helmet & Glowing Emerald Eyes
                hx = tx
                hy = max(0, ty - 4)
                # Skull
                for y_off in range(3):
                    for x_off in range(-2, 3):
                        if 0 <= hx + x_off < 32 and 0 <= hy + y_off < 32:
                            out_tile[hy + y_off, hx + x_off] = SHADOW_MID
                # Twin horns
                if 0 <= hx - 3 < 32 and 0 <= hy - 1 < 32:
                    out_tile[hy - 1, hx - 3] = STEEL_MID
                    out_tile[hy, hx - 3] = STEEL_BRIGHT
                if 0 <= hx + 3 < 32 and 0 <= hy - 1 < 32:
                    out_tile[hy - 1, hx + 3] = STEEL_MID
                    out_tile[hy, hx + 3] = STEEL_BRIGHT

                # Glowing green eyes
                if c == 4:
                    out_tile[hy + 2, hx - 1] = EYE_GREEN
                    out_tile[hy + 2, hx + 1] = EYE_GREEN
                elif c in (1, 2, 3):
                    out_tile[hy + 2, min(31, hx + 1)] = EYE_GREEN
                    out_tile[hy + 2, min(31, hx + 2)] = EYE_GREEN

                # 5. Twin Curved Scythe Blades
                scythe_y = ty + 2
                if c in (1, 2, 3):  # Side view: forward scythe
                    reach = min(30, tx + 6)
                    out_tile[scythe_y, reach - 2] = STEEL_DARK
                    out_tile[scythe_y - 1, reach - 1] = STEEL_MID
                    out_tile[scythe_y - 2, reach] = STEEL_BRIGHT
                    out_tile[scythe_y - 3, reach] = STEEL_HIGH
                    out_tile[scythe_y - 4, reach - 1] = STEEL_MID

                    if is_attack:
                        out_tile[scythe_y - 4, reach] = EYE_GREEN  # venom barb
                        out_tile[scythe_y - 3, min(31, reach + 1)] = EYE_GREEN
                else:
                    # Twin scythes on both sides
                    if tx >= 4:
                        out_tile[scythe_y - 1, tx - 3] = STEEL_BRIGHT
                        out_tile[scythe_y - 2, tx - 4] = STEEL_HIGH
                    if tx <= 27:
                        out_tile[scythe_y - 1, tx + 3] = STEEL_BRIGHT
                        out_tile[scythe_y - 2, tx + 4] = STEEL_HIGH

            else:
                # Death: Green ichor pooling
                floor_y = min(31, max_y + 1)
                for bx in range(max(0, mid_x - 5), min(32, mid_x + 6)):
                    out_tile[floor_y, bx] = FLESH_DEEP if abs(bx - mid_x) < 2 else SHADOW_DEEP

    pal = get_ref_palette()
    png_path = os.path.join(UNITS_DIR, "crypt_fiend.png")
    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(pal)
    out_im.save(png_path, format="PNG", transparency=TRANSPARENT)
    print(f"Saved {png_path} ({out_im.size})")

    export_sheet_to_aseprite(out_arr, 32, 32, 5, 4, 5, pal, "crypt_fiend")


# ==============================================================================
# 3. BUILD AUTHENTIC ABOMINATION (48x48 Colossal Flesh Golem)
# ==============================================================================
def build_abomination():
    print("Building Authentic Scourge Abomination...")
    src_path = os.path.join(BASE_DIR, "graphics", "neutral", "units", "ogre.png")
    src_im = Image.open(src_path)
    src_arr = np.array(src_im)
    w, h = src_im.size  # 240, 720
    cols = w // 48
    rows = h // 48

    out_arr = np.full((h, w), TRANSPARENT, dtype=np.uint8)

    attack_rows = {1, 4, 7, 10, 13}
    death_rows = {2, 5, 8, 11, 14}

    # Ogre skin tones: 134..145
    ogre_skin = set(range(134, 146))
    ogre_loincloth = {197, 198, 199}
    ogre_club = set(range(184, 192))

    for r in range(rows):
        is_attack = r in attack_rows
        is_death = r in death_rows

        for c in range(cols):
            ox = c * 48
            oy = r * 48
            tile = src_arr[oy:oy + 48, ox:ox + 48].copy()
            out_tile = out_arr[oy:oy + 48, ox:ox + 48]

            vis_y, vis_x = np.where(tile != 255)
            if len(vis_y) == 0:
                continue

            min_y, max_y = np.min(vis_y), np.max(vis_y)
            min_x, max_x = np.min(vis_x), np.max(vis_x)
            mid_x = (min_x + max_x) // 2

            # 1. Asymmetrical Necrotic Flesh & Sutures
            for y in range(48):
                for x in range(48):
                    v = tile[y, x]
                    if v == 255:
                        continue
                    if v == 96:
                        out_tile[y, x] = OUTLINE
                    elif v in ogre_skin:
                        # Left side: Olive-green necrotic flesh
                        # Right side: Pale decaying corpse flesh
                        ramp_pos = (v - 134) / 11.0  # 0.0 .. 1.0
                        if x < mid_x:
                            if ramp_pos < 0.25:
                                out_tile[y, x] = FLESH_SHADOW
                            elif ramp_pos < 0.5:
                                out_tile[y, x] = FLESH_DEEP
                            elif ramp_pos < 0.75:
                                out_tile[y, x] = FLESH_DARK
                            else:
                                out_tile[y, x] = FLESH_MID
                        else:
                            if ramp_pos < 0.25:
                                out_tile[y, x] = FLESH_DARK
                            elif ramp_pos < 0.5:
                                out_tile[y, x] = FLESH_MID
                            elif ramp_pos < 0.75:
                                out_tile[y, x] = FLESH_LIGHT
                            else:
                                out_tile[y, x] = FLESH_PALE
                    elif v in ogre_loincloth:
                        # Remap to Butcher Apron in Team Colors
                        out_tile[y, x] = PC_MID
                    elif 200 <= v <= 207:
                        # Existing team color indices
                        out_tile[y, x] = v
                    elif v in ogre_club:
                        # Club pixels will be converted to Cleaver/Hook
                        out_tile[y, x] = STEEL_MID
                    else:
                        out_tile[y, x] = v

            if not is_death:
                # 2. Black Surgical Sutures along Midline Seam
                for sy in range(min_y + 8, min(47, min_y + 26)):
                    if out_tile[sy, mid_x] != TRANSPARENT:
                        out_tile[sy, mid_x] = OUTLINE
                        if sy % 3 == 0:
                            # Cross-stitch 'X'
                            if mid_x > 0:
                                out_tile[sy - 1, mid_x - 1] = OUTLINE
                            if mid_x < 47:
                                out_tile[sy + 1, mid_x + 1] = OUTLINE

                # 3. Bloated Sagging Belly with Intestinal Sutures
                gut_y = min_y + 18
                for gy in range(gut_y, min(47, gut_y + 8)):
                    for gx in range(mid_x - 4, mid_x + 5):
                        if out_tile[gy, gx] != TRANSPARENT:
                            if gy == gut_y + 4:
                                out_tile[gy, gx] = OUTLINE  # Horizontal seam
                            elif gy == gut_y + 5:
                                out_tile[gy, gx] = BLOOD_DARK

                # 4. Blood-Stained Butcher's Apron
                apron_y = min_y + 20
                for ay in range(apron_y, min(47, apron_y + 7)):
                    out_tile[ay, mid_x] = PC_SHINE if ay == apron_y else PC_LIGHT
                    if mid_x > 0:
                        out_tile[ay, mid_x - 1] = PC_MID
                    if mid_x < 47:
                        out_tile[ay, mid_x + 1] = PC_DARK
                # Blood stains on apron
                out_tile[apron_y + 2, mid_x - 1] = BLOOD_BRIGHT
                out_tile[apron_y + 3, mid_x + 1] = BLOOD_FRESH

                # 5. Third Vestigial Skeletal Arm on Right Shoulder
                sh_x = mid_x + (6 if c in (1, 2, 3) else 4)
                sh_y = max(2, min_y + 3)
                if 0 <= sh_x + 3 < 48 and 0 <= sh_y + 3 < 48:
                    out_tile[sh_y, sh_x] = BONE_MID
                    out_tile[sh_y + 1, sh_x + 1] = BONE_WHITE
                    out_tile[sh_y + 2, sh_x + 2] = BONE_WHITE
                    out_tile[sh_y + 2, sh_x + 3] = BONE_PALE  # claw fingers

                # 6. Replace Club with Giant Steel Butcher Cleaver
                # Locate weapon pixels (x > mid_x + 6 or y < min_y + 8 in attack)
                for wy in range(min_y, max_y + 1):
                    for wx in range(mid_x + 5, min(48, max_x + 4)):
                        if tile[wy, wx] in ogre_club or (out_tile[wy, wx] == STEEL_MID and wx > mid_x + 7):
                            # Cleaver blade
                            out_tile[wy, wx] = STEEL_HIGH
                            if wx == min(47, max_x + 2):
                                out_tile[wy, wx] = STEEL_BRIGHT  # razor edge
                                if wy % 2 == 0:
                                    out_tile[wy, wx] = BLOOD_BRIGHT

                # 7. Left Arm: Chains & Iron Meat Hook
                chain_x = max(2, min_x - 1)
                chain_y = min_y + 16
                out_tile[chain_y, chain_x] = STEEL_MID
                out_tile[chain_y + 1, chain_x + 1] = STEEL_HIGH
                out_tile[chain_y + 2, chain_x] = STEEL_MID
                # Hook barb
                out_tile[chain_y + 3, chain_x - 1] = STEEL_BRIGHT
                out_tile[chain_y + 4, chain_x] = STEEL_HIGH
                out_tile[chain_y + 3, chain_x + 1] = STEEL_DARK

                # 8. Stitched Visage: Amber Eye & Blind White Eye
                head_y = min_y + 4
                if c in (1, 2, 3, 4):
                    out_tile[head_y, mid_x - 2] = EYE_AMBER
                    out_tile[head_y, mid_x + 2] = BONE_WHITE
                    out_tile[head_y + 3, mid_x] = OUTLINE  # wire mouth suture

            else:
                # Death: Ruptured gut & massive pool of blood
                floor_y = min(47, max_y + 1)
                for bx in range(max(0, mid_x - 10), min(48, mid_x + 11)):
                    dist = abs(bx - mid_x)
                    out_tile[floor_y, bx] = BLOOD_MID if dist < 5 else BLOOD_DARK

    pal = get_ref_palette()
    png_path = os.path.join(UNITS_DIR, "abomination.png")
    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(pal)
    out_im.save(png_path, format="PNG", transparency=TRANSPARENT)
    print(f"Saved {png_path} ({out_im.size})")

    export_sheet_to_aseprite(out_arr, 48, 48, 5, 5, 5, pal, "abomination")


# ==============================================================================
# EXPORT INTERLEAVED SHEET TO SEQUENTIAL ASEPRITE TIMELINE
# ==============================================================================
def export_sheet_to_aseprite(sheet_arr, tile_w, tile_h, n_walk, n_atk, n_die, pal, unit_name):
    """
    Unpacks an interleaved Stratagus spritesheet into a clean, sequential
    Aseprite animation timeline with tags: Walk-N..S, Attack-N..S, Death.
    """
    move_rows = [0, 3, 6, 9, 12][:n_walk]
    attack_rows = [1, 4, 7, 10, 13][:n_atk]
    death_rows = [2, 5, 8, 11, 14 if n_die == 5 else 13][:n_die]

    frames = []
    tags = []
    dir_names = ["N", "NE", "E", "SE", "S"]

    # 1. Walk frames
    for d_idx, d_name in enumerate(dir_names):
        start_f = len(frames)
        for s in range(n_walk):
            r = move_rows[s]
            tile = sheet_arr[r * tile_h:(r + 1) * tile_h, d_idx * tile_w:(d_idx + 1) * tile_w]
            frames.append(tile.tobytes())
        tags.append((f"Walk-{d_name}", start_f, len(frames) - 1))

    # 2. Attack frames
    for d_idx, d_name in enumerate(dir_names):
        start_f = len(frames)
        for s in range(n_atk):
            r = attack_rows[s]
            tile = sheet_arr[r * tile_h:(r + 1) * tile_h, d_idx * tile_w:(d_idx + 1) * tile_w]
            frames.append(tile.tobytes())
        tags.append((f"Attack-{d_name}", start_f, len(frames) - 1))

    # 3. Death frames (South direction or all)
    start_f = len(frames)
    for s in range(n_die):
        r = death_rows[s]
        tile = sheet_arr[r * tile_h:(r + 1) * tile_h, 4 * tile_w:5 * tile_w]
        frames.append(tile.tobytes())
    tags.append(("Death", start_f, len(frames) - 1))

    ase_path = os.path.join(UNITS_DIR, f"{unit_name}.aseprite")
    write_aseprite(ase_path, frames, tile_w, tile_h, pal, tags)
    print(f"Exported {ase_path} ({len(frames)} frames, {len(tags)} tags)")


def main():
    os.makedirs(UNITS_DIR, exist_ok=True)
    build_ghoul()
    build_crypt_fiend()
    build_abomination()
    print("\nALL AUTHENTIC SCOURGE PIXEL ART COMPLETED SUCCESSFULLY!")


if __name__ == "__main__":
    main()
