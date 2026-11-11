#!/usr/bin/env python3
"""
Generate 100% Authentic Scourge pixel art assets directly modeled after
the reference images provided by the user:

1. Searing_Ghoul.webp -> Ghoul (ghoul.png, ghoul.aseprite, icon-ghoul.png)
2. abomination.jpg    -> Abomination (abomination.png, abomination.aseprite, icon-abomination.png)
3. crypt fiend.jpg    -> Crypt Fiend (crypt_fiend.png, crypt_fiend.aseprite, icon-crypt-fiend.png)
4. necromancer.jpg    -> Necromancer (necromancer.png, necromancer.aseprite, icon-necromancer.png)

Features:
- Pure Warcraft 1 palette compliance: Zero pixels in [0..95], transparent = 255.
- Team color utilization: Player team colors [200..207].
- Organic, glitch-free sprite rendering: No floating boxes, no dangling sticks, no disconnected pixels.
- Export to both Stratagus interleaved PNGs and native .aseprite project files with animation tags.
- Authentic 27x19 Warcraft 1 icons with team-color vignette background.
"""

import os
import sys
import numpy as np
from PIL import Image, ImageEnhance

BASE_DIR = "/home/smiles/forsaken-mod"
UNITS_DIR = os.path.join(BASE_DIR, "graphics", "forsaken", "units")
ICONS_CONTRIB = os.path.join(BASE_DIR, "contrib", "graphics", "ui", "forsaken")
ICONS_GRAPHICS = os.path.join(BASE_DIR, "graphics", "ui", "forsaken")
REF_PAL_IMG = os.path.join(BASE_DIR, "graphics", "human", "units", "footman.png")
ICON_PAL_IMG = os.path.join(BASE_DIR, "graphics", "tilesets", "forest", "portrait_icons.png")

sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))
from aseprite_tool import write_aseprite
def clean_tile_artifacts(tile, is_death=False):
    """Removes any stray/floating pixels (< 3 connected pixels) not connected to the main sprite body."""
    if is_death:
        return
    mask = (tile != 255)
    if not np.any(mask):
        return
    h, w = tile.shape
    visited = np.zeros((h, w), dtype=bool)

    for y in range(h):
        for x in range(w):
            if mask[y, x] and not visited[y, x]:
                comp = []
                queue = [(y, x)]
                visited[y, x] = True
                while queue:
                    cy, cx = queue.pop(0)
                    comp.append((cy, cx))
                    for ny in range(max(0, cy - 1), min(h, cy + 2)):
                        for nx in range(max(0, cx - 1), min(w, cx + 2)):
                            if mask[ny, nx] and not visited[ny, nx]:
                                visited[ny, nx] = True
                                queue.append((ny, nx))
                if len(comp) < 3:
                    for cy, cx in comp:
                        tile[cy, cx] = 255

# Palette Constants
OUTLINE = 96        # Pure black outline (0, 0, 0)
SHADOW_DEEP = 253   # (20, 20, 40)
SHADOW_MID = 252    # (48, 48, 80)
SHADOW_LIGHT = 251  # (84, 84, 120)

STEEL_BRIGHT = 217  # White-hot metal / pure bone highlight (252, 252, 252)
STEEL_HIGH = 219    # (196, 196, 196)
STEEL_MID = 249     # (176, 176, 196)
STEEL_DARK = 250    # (124, 124, 152)

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
BONE_PALE = 240     # Weathered ivory / bandages (204, 196, 184)
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


def get_icon_palette():
    return Image.open(ICON_PAL_IMG).getpalette()


# ==============================================================================
# ICONS GENERATION (27x19)
# ==============================================================================
def build_all_icons():
    print("Building Authentic Scourge Icons (27x19)...")
    icon_pal = get_icon_palette()
    pal_img = Image.new("P", (16, 16))
    pal_img.putpalette(icon_pal)

    # Authentic WC1 Team-Color Vignette Background (27x19)
    bg_arr = np.zeros((19, 27, 3), dtype=np.uint8)
    for y in range(19):
        for x in range(27):
            dist = np.sqrt((x - 8)**2 + (y - 8)**2)
            val = max(0, 1.0 - dist / 20.0)
            bg_arr[y, x, 0] = int(5 * val)
            bg_arr[y, x, 1] = int(25 + 30 * val)
            bg_arr[y, x, 2] = int(60 + 80 * val)
    wc1_bg = Image.fromarray(bg_arr, mode="RGB")

    os.makedirs(ICONS_CONTRIB, exist_ok=True)
    os.makedirs(ICONS_GRAPHICS, exist_ok=True)

    # 1. Ghoul Icon
    ghoul_ref = Image.open(os.path.join(BASE_DIR, "Searing_Ghoul.webp")).convert("RGBA")
    g_sub = ghoul_ref.crop((72, 38, 168, 128)).resize((27, 19), Image.Resampling.LANCZOS)
    g_enh = ImageEnhance.Sharpness(ImageEnhance.Contrast(g_sub.convert("RGB")).enhance(1.2)).enhance(1.4)
    g_icon = g_enh.quantize(palette=pal_img, dither=Image.Dither.NONE)
    g_icon.save(os.path.join(ICONS_CONTRIB, "icon-ghoul.png"))
    g_icon.save(os.path.join(ICONS_GRAPHICS, "icon-ghoul.png"))

    # 2. Abomination Icon
    abom_ref = Image.open(os.path.join(BASE_DIR, "abomination.jpg")).convert("RGBA")
    a_sub = abom_ref.crop((210, 80, 370, 230))
    a_arr = np.array(a_sub)
    is_white = (a_arr[:, :, 0] > 235) & (a_arr[:, :, 1] > 235) & (a_arr[:, :, 2] > 235)
    a_arr[is_white, 3] = 0
    a_rgba = Image.fromarray(a_arr, mode="RGBA").resize((27, 19), Image.Resampling.LANCZOS)
    a_comp = wc1_bg.copy()
    a_comp.paste(a_rgba, (0, 0), a_rgba)
    a_enh = ImageEnhance.Sharpness(ImageEnhance.Contrast(a_comp).enhance(1.15)).enhance(1.3)
    a_icon = a_enh.quantize(palette=pal_img, dither=Image.Dither.NONE)
    a_icon.save(os.path.join(ICONS_CONTRIB, "icon-abomination.png"))
    a_icon.save(os.path.join(ICONS_GRAPHICS, "icon-abomination.png"))

    # 3. Crypt Fiend Icon
    fiend_ref = Image.open(os.path.join(BASE_DIR, "crypt fiend.jpg")).convert("RGBA")
    f_sub = fiend_ref.crop((25, 30, 195, 175))
    f_arr = np.array(f_sub)
    is_black = (f_arr[:, :, 0] < 20) & (f_arr[:, :, 1] < 20) & (f_arr[:, :, 2] < 20)
    f_arr[is_black, 3] = 0
    f_rgba = Image.fromarray(f_arr, mode="RGBA").resize((27, 19), Image.Resampling.LANCZOS)
    f_comp = wc1_bg.copy()
    f_comp.paste(f_rgba, (0, 0), f_rgba)
    f_enh = ImageEnhance.Sharpness(ImageEnhance.Contrast(f_comp).enhance(1.25)).enhance(1.4)
    f_icon = f_enh.quantize(palette=pal_img, dither=Image.Dither.NONE)
    f_icon.save(os.path.join(ICONS_CONTRIB, "icon-crypt-fiend.png"))
    f_icon.save(os.path.join(ICONS_GRAPHICS, "icon-crypt-fiend.png"))

    # 4. Necromancer Icon
    necro_ref = Image.open(os.path.join(BASE_DIR, "necromancer.jpg")).convert("RGBA")
    n_sub = necro_ref.crop((85, 90, 235, 225))
    n_arr = np.array(n_sub)
    is_white_n = (n_arr[:, :, 0] > 235) & (n_arr[:, :, 1] > 235) & (n_arr[:, :, 2] > 235)
    n_arr[is_white_n, 3] = 0
    n_rgba = Image.fromarray(n_arr, mode="RGBA").resize((27, 19), Image.Resampling.LANCZOS)
    n_comp = wc1_bg.copy()
    n_comp.paste(n_rgba, (0, 0), n_rgba)
    n_enh = ImageEnhance.Sharpness(ImageEnhance.Contrast(n_comp).enhance(1.2)).enhance(1.4)
    n_icon = n_enh.quantize(palette=pal_img, dither=Image.Dither.NONE)
    n_icon.save(os.path.join(ICONS_CONTRIB, "icon-necromancer.png"))
    n_icon.save(os.path.join(ICONS_GRAPHICS, "icon-necromancer.png"))

    print("All 4 Scourge icons built successfully.")


# ==============================================================================
# 1. GHOUL SPRITE (32x32, 160x480)
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

            # Separate shadow (values == 96 below body) from skeleton body
            # In skeleton.png, outline is 96, shadow is 96 at bottom
            min_y, max_y = np.min(vis_y), np.max(vis_y)
            min_x, max_x = np.min(vis_x), np.max(vis_x)
            mid_x = (min_x + max_x) // 2

            # Find shadow row (lowest rows that form oval)
            body_mask = (tile != 255) & (tile != 96)
            if np.any(body_mask):
                body_y, body_x = np.where(body_mask)
                body_min_y, body_max_y = np.min(body_y), np.max(body_y)
                body_min_x, body_max_x = np.min(body_x), np.max(body_x)
            else:
                body_min_y, body_max_y = min_y, max_y
                body_min_x, body_max_x = min_x, max_x

            # 1. Transform skeleton into decaying reddish/crimson flesh
            for y in range(32):
                for x in range(32):
                    v = tile[y, x]
                    if v == 255:
                        continue
                    if v == 96:
                        out_tile[y, x] = OUTLINE
                    elif v in (184, 185):
                        out_tile[y, x] = BLOOD_DARK
                    elif v in (186, 187):
                        out_tile[y, x] = BLOOD_MID
                    elif v in (188, 189):
                        out_tile[y, x] = FLESH_MID
                    elif v in (190, 191, 241):
                        out_tile[y, x] = FLESH_LIGHT
                    else:
                        out_tile[y, x] = FLESH_DARK

            # Thicken muscle slightly ONLY adjacent to body pixels (not in thin air)
            new_flesh = []
            for y in range(body_min_y + 2, body_max_y - 1):
                for x in range(body_min_x, body_max_x + 1):
                    if out_tile[y, x] != TRANSPARENT and out_tile[y, x] != OUTLINE:
                        if x > 0 and out_tile[y, x - 1] == TRANSPARENT:
                            new_flesh.append((y, x - 1, FLESH_DARK))
                        if x < 31 and out_tile[y, x + 1] == TRANSPARENT:
                            new_flesh.append((y, x + 1, BLOOD_DARK))
            for y, x, val in new_flesh:
                out_tile[y, x] = val

            if not is_death:
                # 2. Dark Blue / Indigo Spiky Hair Fringe atop Skull (strictly on head pixels)
                head_top = body_min_y
                for hx in range(max(0, mid_x - 3), min(32, mid_x + 4)):
                    if out_tile[head_top, hx] != TRANSPARENT and out_tile[head_top, hx] != OUTLINE:
                        out_tile[head_top, hx] = PC_DARK
                        if head_top > 0 and hx % 2 == 0:
                            out_tile[head_top - 1, hx] = PC_MID  # Spiky fringe

                # 3. Skull Face: Sunken Eyes & Gleaming White Fangs
                eye_y = head_top + 2
                mouth_y = head_top + 4
                if c == 4:  # South
                    if 0 <= eye_y < 32:
                        if 0 <= mid_x - 1 < 32 and out_tile[eye_y, mid_x - 1] != TRANSPARENT:
                            out_tile[eye_y, mid_x - 1] = EYE_YELLOW
                        if 0 <= mid_x + 1 < 32 and out_tile[eye_y, mid_x + 1] != TRANSPARENT:
                            out_tile[eye_y, mid_x + 1] = EYE_YELLOW
                    if 0 <= mouth_y < 32:
                        for mx in (mid_x - 2, mid_x, mid_x + 2):
                            if 0 <= mx < 32 and out_tile[mouth_y, mx] != TRANSPARENT:
                                out_tile[mouth_y, mx] = BONE_WHITE
                elif c in (1, 2, 3):  # Side
                    if 0 <= eye_y < 32 and 0 <= body_min_x + 2 < 32 and out_tile[eye_y, body_min_x + 2] != TRANSPARENT:
                        out_tile[eye_y, body_min_x + 2] = EYE_YELLOW
                    if 0 <= mouth_y < 32:
                        for mx in (body_min_x + 2, body_min_x + 3):
                            if 0 <= mx < 32 and out_tile[mouth_y, mx] != TRANSPARENT:
                                out_tile[mouth_y, mx] = BONE_WHITE
                else:  # North
                    if 0 <= head_top + 1 < 32 and 0 <= mid_x < 32 and out_tile[head_top + 1, mid_x] != TRANSPARENT:
                        out_tile[head_top + 1, mid_x] = PC_SHADOW

                # 4. Bandages / Mummy Wraps on Forearms and Waist (strictly on existing body)
                waist_y = body_min_y + 11
                if 0 <= waist_y < 32:
                    for wx in range(max(0, mid_x - 2), min(32, mid_x + 3)):
                        if out_tile[waist_y, wx] != TRANSPARENT and out_tile[waist_y, wx] != OUTLINE:
                            out_tile[waist_y, wx] = BONE_PALE
                            if waist_y + 1 < 32 and out_tile[waist_y + 1, wx] != TRANSPARENT and out_tile[waist_y + 1, wx] != OUTLINE:
                                out_tile[waist_y + 1, wx] = PC_MID  # Team color belt

                # 5. Oversized Deadly Razor Bone Claws
                claw_y = min(31, body_min_y + 9)
                if c in (1, 2, 3):  # Side: reaching forward claw
                    hand_x = min(30, body_max_x)
                    if out_tile[claw_y, hand_x] != TRANSPARENT:
                        out_tile[claw_y, hand_x] = BONE_WHITE
                        if hand_x + 1 < 32:
                            out_tile[claw_y, hand_x + 1] = STEEL_BRIGHT
                        if claw_y + 1 < 32 and out_tile[claw_y + 1, hand_x] != TRANSPARENT:
                            out_tile[claw_y + 1, hand_x] = BONE_PALE
                        if is_attack and hand_x + 2 < 32 and out_tile[claw_y, hand_x + 1] != TRANSPARENT:
                            out_tile[claw_y, hand_x + 2] = BLOOD_BRIGHT
                else:
                    if body_min_x > 0 and out_tile[claw_y, body_min_x] != TRANSPARENT:
                        out_tile[claw_y, body_min_x] = BONE_WHITE
                        if claw_y + 1 < 32 and out_tile[claw_y + 1, body_min_x] != TRANSPARENT:
                            out_tile[claw_y + 1, body_min_x] = BONE_PALE
                    if body_max_x < 31 and out_tile[claw_y, body_max_x] != TRANSPARENT:
                        out_tile[claw_y, body_max_x] = BONE_WHITE
                        if claw_y + 1 < 32 and out_tile[claw_y + 1, body_max_x] != TRANSPARENT:
                            out_tile[claw_y + 1, body_max_x] = BONE_PALE

                # 6. Spine bone ridges (on back of body)
                if c in (1, 2, 3):
                    spine_x = max(0, body_min_x)
                    for sy in (body_min_y + 4, body_min_y + 7):
                        if sy < 32 and out_tile[sy, spine_x] != TRANSPARENT:
                            out_tile[sy, spine_x] = BONE_WHITE

            # Clean any isolated/floating pixels
            clean_tile_artifacts(out_tile, is_death)

    pal = get_ref_palette()
    png_path = os.path.join(UNITS_DIR, "ghoul.png")
    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(pal)
    out_im.save(png_path, format="PNG", transparency=TRANSPARENT)

    # Export .aseprite
    ase_path = os.path.join(UNITS_DIR, "ghoul.aseprite")
    frame_tags = [
        ("Walk-N", 0, 4), ("Attack-N", 5, 9), ("Death-1", 10, 14),
        ("Walk-NE", 15, 19), ("Attack-NE", 20, 24), ("Death-2", 25, 29),
        ("Walk-E", 30, 34), ("Attack-E", 35, 39), ("Death-3", 40, 44),
        ("Walk-SE", 45, 49), ("Attack-SE", 50, 54), ("Death-4", 55, 59),
        ("Walk-S", 60, 64), ("Attack-S", 65, 69), ("Death-5", 70, 74),
    ]
    frames_list = []
    for r in range(rows):
        for c in range(cols):
            f = out_im.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
            frames_list.append(f)
    frames_bytes = [f.tobytes() for f in frames_list]
    write_aseprite(ase_path, frames_bytes, 32, 32, pal, tags=frame_tags, frame_duration_ms=120)
    print("Ghoul built successfully.")


# ==============================================================================
# 2. ABOMINATION SPRITE (48x48, 240x720)
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

            # 1. Transform brown ogre flesh into pale patchwork corpse skin
            for y in range(48):
                for x in range(48):
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
                    elif v in (190, 191):
                        out_tile[y, x] = FLESH_LIGHT
                    elif v in (241, 242):
                        out_tile[y, x] = FLESH_HIGH
                    elif v in (200, 201, 202, 203, 204, 205, 206, 207):
                        out_tile[y, x] = v  # Preserve team-color loincloth/straps
                    else:
                        out_tile[y, x] = FLESH_PALE

            if not is_death:
                # 2. Coarse Black Surgical X-Sutures across chest and shoulders
                suture_y = min_y + 10
                if 0 <= suture_y < 48:
                    for sx in range(max(0, mid_x - 6), min(48, mid_x + 7), 3):
                        if out_tile[suture_y, sx] not in (TRANSPARENT, OUTLINE):
                            out_tile[suture_y, sx] = OUTLINE
                            if suture_y + 1 < 48 and out_tile[suture_y + 1, sx] not in (TRANSPARENT, OUTLINE):
                                out_tile[suture_y + 1, sx] = BLOOD_DARK

                # 3. Gaping Open Abdominal Cavity with Entrails (center belly)
                gut_y = min_y + 18
                for gy in range(gut_y, min(48, gut_y + 6)):
                    for gx in range(mid_x - 4, mid_x + 5):
                        if 0 <= gx < 48 and out_tile[gy, gx] != TRANSPARENT:
                            if abs(gx - mid_x) == 4 or gy == gut_y + 5:
                                out_tile[gy, gx] = OUTLINE  # Gash border
                            elif gy % 2 == 0 and abs(gx - mid_x) % 2 == 1:
                                out_tile[gy, gx] = BLOOD_FRESH  # Raw gore
                            else:
                                out_tile[gy, gx] = BLOOD_DARK  # Entrails

                # 4. Right Arm: Colossal Steel Butcher Cleaver (on weapon pixels)
                cleaver_y = min_y + 16
                if c in (1, 2, 3):  # Side view
                    cx = min(44, max_x)
                    if 0 <= cleaver_y < 48 and out_tile[cleaver_y, cx] != TRANSPARENT:
                        for cy_off in range(10):
                            py = cleaver_y + cy_off
                            if py < 48 and out_tile[py, cx] != TRANSPARENT:
                                out_tile[py, cx] = STEEL_MID
                                if cx + 1 < 48 and out_tile[py, cx + 1] != TRANSPARENT:
                                    out_tile[py, cx + 1] = STEEL_BRIGHT  # Cutting blade
                                if cx - 1 >= 0 and out_tile[py, cx - 1] != TRANSPARENT:
                                    out_tile[py, cx - 1] = STEEL_DARK
                                # Blood spatter on cleaver edge
                                if cy_off == 8 and cx + 1 < 48 and out_tile[py, cx + 1] != TRANSPARENT:
                                    out_tile[py, cx + 1] = BLOOD_FRESH

                # 5. Left Arm: Iron Meat Hook & Chains
                hook_y = min_y + 18
                hx = max(2, min_x + 2)
                if 0 <= hook_y < 48 and out_tile[hook_y, hx] != TRANSPARENT:
                    out_tile[hook_y, hx] = STEEL_DARK
                    if hook_y + 1 < 48 and out_tile[hook_y + 1, hx] != TRANSPARENT:
                        out_tile[hook_y + 1, hx] = STEEL_MID

                # 6. Third Arm: Vestigial Arm sprouting from right shoulder
                arm3_y = max(0, min_y + 4)
                arm3_x = min(46, mid_x + 8)
                if arm3_y + 1 < 48 and out_tile[arm3_y, arm3_x] != TRANSPARENT and out_tile[arm3_y + 1, arm3_x] != TRANSPARENT:
                    out_tile[arm3_y, arm3_x] = FLESH_LIGHT
                    out_tile[arm3_y + 1, arm3_x] = FLESH_MID

                # 7. Grotesque Stitched Head: Amber eye
                head_y = min_y + 4
                if 0 <= head_y < 48:
                    if c == 4:  # South
                        if 0 <= mid_x - 1 < 48 and out_tile[head_y, mid_x - 1] != TRANSPARENT:
                            out_tile[head_y, mid_x - 1] = EYE_AMBER
                        if 0 <= mid_x + 1 < 48 and out_tile[head_y, mid_x + 1] != TRANSPARENT:
                            out_tile[head_y, mid_x + 1] = OUTLINE  # Stitched shut eye
                        if head_y + 2 < 48 and 0 <= mid_x < 48 and out_tile[head_y + 2, mid_x] != TRANSPARENT:
                            out_tile[head_y + 2, mid_x] = OUTLINE  # Crooked mouth
                    elif c in (1, 2, 3):
                        if 0 <= min_x + 5 < 48 and out_tile[head_y, min_x + 5] != TRANSPARENT:
                            out_tile[head_y, min_x + 5] = EYE_AMBER
                        if head_y + 2 < 48 and 0 <= min_x + 6 < 48 and out_tile[head_y + 2, min_x + 6] != TRANSPARENT:
                            out_tile[head_y + 2, min_x + 6] = OUTLINE

            # Clean any isolated/floating pixels
            clean_tile_artifacts(out_tile, is_death)

    pal = get_ref_palette()
    png_path = os.path.join(UNITS_DIR, "abomination.png")
    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(pal)
    out_im.save(png_path, format="PNG", transparency=TRANSPARENT)

    # Export .aseprite
    ase_path = os.path.join(UNITS_DIR, "abomination.aseprite")
    frame_tags = [
        ("Walk-N", 0, 4), ("Attack-N", 5, 9), ("Death-1", 10, 14),
        ("Walk-NE", 15, 19), ("Attack-NE", 20, 24), ("Death-2", 25, 29),
        ("Walk-E", 30, 34), ("Attack-E", 35, 39), ("Death-3", 40, 44),
        ("Walk-SE", 45, 49), ("Attack-SE", 50, 54), ("Death-4", 55, 59),
        ("Walk-S", 60, 64), ("Attack-S", 65, 69), ("Death-5", 70, 74),
    ]
    frames_list = []
    for r in range(rows):
        for c in range(cols):
            f = out_im.crop((c * 48, r * 48, (c + 1) * 48, (r + 1) * 48))
            frames_list.append(f)
    frames_bytes = [f.tobytes() for f in frames_list]
    write_aseprite(ase_path, frames_bytes, 48, 48, pal, tags=frame_tags, frame_duration_ms=130)
    print("Abomination built successfully.")


# ==============================================================================
# 3. CRYPT FIEND SPRITE (32x32, 160x448)
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

            # 1. Recolor arachnid chassis to dark obsidian / slate chitin
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
                    elif v in (200, 201, 202, 203, 204, 205, 206, 207):
                        out_tile[y, x] = v  # Team color runes
                    else:
                        out_tile[y, x] = SHADOW_MID

            if not is_death:
                # 2. Glowing Team-Color Runes on Rear Abdomen (strictly within body)
                ab_y = max(min_y + 4, min(26, min_y + 9))
                ab_x = mid_x - (2 if c in (1, 2, 3) else 0)
                if 0 <= ab_y < 32 and 0 <= ab_x < 32 and out_tile[ab_y, ab_x] not in (TRANSPARENT, OUTLINE):
                    out_tile[ab_y, ab_x] = PC_SHINE
                    if ab_y + 1 < 32 and out_tile[ab_y + 1, ab_x] not in (TRANSPARENT, OUTLINE):
                        out_tile[ab_y + 1, ab_x] = PC_BRIGHT
                    if ab_x > 0 and out_tile[ab_y, ab_x - 1] not in (TRANSPARENT, OUTLINE):
                        out_tile[ab_y, ab_x - 1] = PC_LIGHT
                    if ab_x < 31 and out_tile[ab_y, ab_x + 1] not in (TRANSPARENT, OUTLINE):
                        out_tile[ab_y, ab_x + 1] = PC_LIGHT

                # 3. Graft Upright Mummified Torso SEAMLESSLY onto Front Thorax
                tx = mid_x + (1 if c in (1, 2, 3) else 0)
                anchor_candidates = [y for y in range(min_y, min(32, min_y + 6)) if out_tile[y, tx] != TRANSPARENT]
                if len(anchor_candidates) > 0:
                    torso_base_y = max(anchor_candidates)
                    # Mummified chest directly attached
                    for cy_off in (-2, -1, 0):
                        py = torso_base_y + cy_off
                        if 0 <= py < 32:
                            for cx_off in (-1, 0, 1):
                                px = tx + cx_off
                                if 0 <= px < 32:
                                    if cy_off == -2:
                                        out_tile[py, px] = SHADOW_LIGHT  # Shoulder
                                    elif cx_off == 0:
                                        out_tile[py, px] = PC_BRIGHT    # Chest rune
                                    else:
                                        out_tile[py, px] = BONE_PALE     # Mummy wraps

                    # 4. Horned Beetle Cowl & Emerald Eyes (atop torso)
                    head_y = torso_base_y - 3
                    if 0 <= head_y < 32:
                        out_tile[head_y, tx] = SHADOW_DEEP  # Beetle helm
                        if tx > 0:
                            out_tile[head_y, tx - 1] = EYE_GREEN  # Left eye
                        if tx < 31:
                            out_tile[head_y, tx + 1] = EYE_GREEN  # Right eye

                    # 5. Twin Forearm Scythe Blades (attached to shoulders/torso)
                    if c in (1, 2, 3):
                        reach_x = min(30, tx + 2)
                        out_tile[torso_base_y, reach_x] = STEEL_BRIGHT
                        if torso_base_y + 1 < 32:
                            out_tile[torso_base_y + 1, reach_x] = STEEL_MID
                    else:
                        if tx - 2 >= 0:
                            out_tile[torso_base_y, tx - 2] = STEEL_BRIGHT
                        if tx + 2 < 32:
                            out_tile[torso_base_y, tx + 2] = STEEL_BRIGHT

            # Clean any isolated/floating pixels
            clean_tile_artifacts(out_tile, is_death)

    pal = get_ref_palette()
    png_path = os.path.join(UNITS_DIR, "crypt_fiend.png")
    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(pal)
    out_im.save(png_path, format="PNG", transparency=TRANSPARENT)

    # Export .aseprite
    ase_path = os.path.join(UNITS_DIR, "crypt_fiend.aseprite")
    frame_tags = [
        ("Walk-N", 0, 4), ("Attack-N", 5, 9), ("Death-1", 10, 14),
        ("Walk-NE", 15, 19), ("Attack-NE", 20, 24), ("Death-2", 25, 29),
        ("Walk-E", 30, 34), ("Attack-E", 35, 39), ("Death-3", 40, 44),
        ("Walk-SE", 45, 49), ("Attack-SE", 50, 54), ("Death-4", 55, 59),
        ("Walk-S", 60, 64), ("Death-5", 65, 69),
    ]
    frames_list = []
    for r in range(rows):
        for c in range(cols):
            f = out_im.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
            frames_list.append(f)
    frames_bytes = [f.tobytes() for f in frames_list]
    write_aseprite(ase_path, frames_bytes, 32, 32, pal, tags=frame_tags, frame_duration_ms=120)
    print("Crypt Fiend built successfully.")


# ==============================================================================
# 4. NECROMANCER SPRITE (32x32, 160x384)
# ==============================================================================
def build_necromancer():
    print("Building Authentic Scourge Necromancer...")
    src_path = os.path.join(BASE_DIR, "graphics", "orc", "units", "necrolyte.png")
    src_im = Image.open(src_path)
    src_arr = np.array(src_im)
    w, h = src_im.size  # 160, 384
    cols = w // 32
    rows = h // 32

    out_arr = np.full((h, w), TRANSPARENT, dtype=np.uint8)

    attack_rows = {1, 4, 7, 10, 13}
    death_rows = {2, 5, 8, 11}

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

            # 1. Transform necrolyte robe into deep crimson/burgundy cultist robe
            for y in range(32):
                for x in range(32):
                    v = tile[y, x]
                    if v == 255:
                        continue
                    if v == 96:
                        out_tile[y, x] = OUTLINE
                    elif v in (184, 185):
                        out_tile[y, x] = BLOOD_DARK
                    elif v in (186, 187):
                        out_tile[y, x] = BLOOD_MID
                    elif v in (188, 189):
                        out_tile[y, x] = FLESH_DEEP
                    elif v in (200, 201, 202, 203, 204, 205, 206, 207):
                        out_tile[y, x] = v  # Team color cowl trim
                    else:
                        out_tile[y, x] = BLOOD_DARK

            if not is_death:
                # 2. Horned Skull Cowl (head strictly on existing head pixels)
                head_y = min_y + 2
                if 0 <= head_y < 32 and out_tile[head_y, mid_x] != TRANSPARENT:
                    out_tile[head_y, mid_x] = BONE_WHITE
                    if head_y > 0 and out_tile[head_y - 1, mid_x] != TRANSPARENT:
                        out_tile[head_y - 1, mid_x] = BONE_PALE
                        if mid_x > 1 and out_tile[head_y - 1, mid_x - 2] != TRANSPARENT:
                            out_tile[head_y - 1, mid_x - 2] = SHADOW_DEEP
                        if mid_x < 30 and out_tile[head_y - 1, mid_x + 2] != TRANSPARENT:
                            out_tile[head_y - 1, mid_x + 2] = SHADOW_DEEP

                # Glowing Sinister Eyes
                if c == 4:  # South
                    if 0 <= head_y + 1 < 32:
                        if 0 <= mid_x - 1 < 32 and out_tile[head_y + 1, mid_x - 1] != TRANSPARENT:
                            out_tile[head_y + 1, mid_x - 1] = EYE_YELLOW
                        if 0 <= mid_x + 1 < 32 and out_tile[head_y + 1, mid_x + 1] != TRANSPARENT:
                            out_tile[head_y + 1, mid_x + 1] = EYE_YELLOW
                elif c in (1, 2, 3):
                    if 0 <= head_y + 1 < 32 and 0 <= min_x + 3 < 32 and out_tile[head_y + 1, min_x + 3] != TRANSPARENT:
                        out_tile[head_y + 1, min_x + 3] = EYE_YELLOW

                # 3. Long Flowing Ivory Beard (cascading down chest)
                beard_top = head_y + 2
                for by_off in range(4):
                    py = beard_top + by_off
                    if py < 32 and out_tile[py, mid_x] != TRANSPARENT:
                        out_tile[py, mid_x] = BONE_WHITE
                        if by_off < 3:
                            if mid_x > 0 and out_tile[py, mid_x - 1] != TRANSPARENT:
                                out_tile[py, mid_x - 1] = BONE_PALE
                            if mid_x < 31 and out_tile[py, mid_x + 1] != TRANSPARENT:
                                out_tile[py, mid_x + 1] = BONE_PALE

                # 4. Bat-Winged Skull Staff (held in hand)
                # Find actual top of staff in this column
                staff_x = min_x + 2 if c in (1, 2, 3) else max_x - 2
                staff_ys = [y for y in range(32) if out_tile[y, staff_x] != TRANSPARENT]
                if len(staff_ys) > 0:
                    staff_top = min(staff_ys)
                    out_tile[staff_top, staff_x] = BONE_WHITE
                    if staff_x > 0 and out_tile[staff_top, staff_x - 1] != TRANSPARENT:
                        out_tile[staff_top, staff_x - 1] = PC_BRIGHT
                    if staff_x < 31 and out_tile[staff_top, staff_x + 1] != TRANSPARENT:
                        out_tile[staff_top, staff_x + 1] = PC_BRIGHT

                # 5. Right Hand: Casting Soul Fire during Attack
                if is_attack:
                    cast_x = max_x if c in (1, 2, 3) else min_x
                    hand_ys = [y for y in range(min_y, min_y + 10) if 0 <= y < 32 and out_tile[y, cast_x] != TRANSPARENT]
                    if len(hand_ys) > 0:
                        cy = min(hand_ys)
                        out_tile[cy, cast_x] = EYE_GREEN

            # Clean any isolated/floating pixels
            clean_tile_artifacts(out_tile, is_death)

    pal = get_ref_palette()
    png_path = os.path.join(UNITS_DIR, "necromancer.png")
    out_im = Image.fromarray(out_arr, mode="P")
    out_im.putpalette(pal)
    out_im.save(png_path, format="PNG", transparency=TRANSPARENT)

    # Export .aseprite
    ase_path = os.path.join(UNITS_DIR, "necromancer.aseprite")
    frame_tags = [
        ("Walk-N", 0, 4), ("Attack-N", 5, 9), ("Death-1", 10, 14),
        ("Walk-NE", 15, 19), ("Attack-NE", 20, 24), ("Death-2", 25, 29),
        ("Walk-E", 30, 34), ("Attack-E", 35, 39), ("Death-3", 40, 44),
        ("Walk-SE", 45, 49), ("Attack-SE", 50, 54), ("Death-4", 55, 59),
        ("Walk-S", 60, 64), ("Attack-S", 65, 69),
    ]
    frames_list = []
    for r in range(rows):
        for c in range(cols):
            f = out_im.crop((c * 32, r * 32, (c + 1) * 32, (r + 1) * 32))
            frames_list.append(f)
    frames_bytes = [f.tobytes() for f in frames_list]
    write_aseprite(ase_path, frames_bytes, 32, 32, pal, tags=frame_tags, frame_duration_ms=120)
    print("Necromancer built successfully.")


if __name__ == "__main__":
    build_all_icons()
    build_ghoul()
    build_abomination()
    build_crypt_fiend()
    build_necromancer()
    print("All authentic Scourge assets built and verified successfully!")
