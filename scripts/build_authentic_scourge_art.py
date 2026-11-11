#!/usr/bin/env python3
"""
Build high-fidelity, authentic Warcraft III Scourge art based directly on
original Blizzard Warcraft 1 pixel art assets:

1. Crypt (barracks.png / barracks_construction.png):
   Sculpted from human/buildings/church.png (64x64 stone gothic cathedral)
   with dark obsidian masonry, 4 soaring vaulted ribcage arches, sunken portal
   with glowing green necrotic mist, gargoyle watchers, and teal Scourge crystals.

2. Graveyard (lumber_mill.png / lumber_mill_construction.png):
   Sculpted from human/buildings/lumber_mill.png (64x64)
   with stone mausoleum, wrought-iron perimeter fence, open graves, bone piles,
   skulls, crooked tombstones, rising green mist, and necrotic soul crystal.

3. Sacrificial Pit (stable.png / stable_construction.png):
   Sculpted from human/buildings/stable.png (64x64)
   with obsidian basin, swirling green ectoplasm pool, 4 floating obelisks, and chains.

4. Crypt Fiend (crypt_fiend.png):
   Sculpted from neutral/units/spider.png (160x448, 14 rows of 32x32 frames)
   with dark obsidian nerubian chitin, glowing venom glands, pale chevron markings,
   upright armored nerubian carapace, horned visage, and mantis scythe claws.

5. Abomination (abomination.png):
   Sculpted from neutral/units/ogre.png (240x720, 15 rows of 48x48 frames)
   with sickly decaying corpse flesh, thick black surgical cross-sutures,
   bloated stitched belly, giant butcher's cleaver, meat hook with chain,
   third vestigial skeletal arm, and stitched face.

6. Icons:
   Sculpted directly from authentic portrait_icons frames with transparency=255.

CRITICAL REQUIREMENT: Every single saved PNG MUST include transparency=255!
"""

import os
import math
from PIL import Image

BASE_DIR = "/home/smiles/forsaken-mod"
GRAPHICS_DIR = os.path.join(BASE_DIR, "graphics")
UI_FORSAKEN_DIR = os.path.join(BASE_DIR, "contrib", "graphics", "ui", "forsaken")


def get_palette_matcher(ref_pal, allow_pc=False):
    cache = {}
    def find_idx(r, g, b):
        key = (r, g, b)
        if key in cache:
            return cache[key]
        best_d = 10**9
        best_i = 0
        for i in range(255):
            if not allow_pc and (200 <= i <= 207):
                continue
            pr, pg, pb = ref_pal[i * 3], ref_pal[i * 3 + 1], ref_pal[i * 3 + 2]
            d = (pr - key[0]) ** 2 + (pg - key[1]) ** 2 + (pb - key[2]) ** 2
            if d < best_d:
                best_d = d
                best_i = i
        cache[key] = best_i
        return best_i
    return find_idx


def rgba_to_indexed_with_transparency(rgba_im, ref_pal, orig_im=None):
    """
    Convert RGBA image to indexed palette P mode, preserving player colors (200..207)
    and exact transparent background at index 255.
    """
    w, h = rgba_im.size
    out = Image.new("P", (w, h), 255)
    out.putpalette(ref_pal)
    src_px = rgba_im.load()
    out_px = out.load()
    orig_px = orig_im.load() if orig_im is not None else None
    find_idx = get_palette_matcher(ref_pal)

    for y in range(h):
        for x in range(w):
            r, g, b, a = src_px[x, y]
            if a < 128:
                out_px[x, y] = 255
            elif r == 254 and g == 0 and 200 <= b <= 207:
                out_px[x, y] = b
            elif orig_px is not None and 200 <= orig_px[x, y] <= 207:
                out_px[x, y] = orig_px[x, y]
            else:
                out_px[x, y] = find_idx(r, g, b)
    return out


def save_transparent_png(indexed_im, path):
    """Save indexed image ensuring transparency=255 chunk is written to disk."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    indexed_im.save(path, transparency=255)


def recolor_to_obsidian_undead(rgba_im, orig_im=None):
    """Transform WC1 building colors into dark gothic obsidian stone with purple/teal tones."""
    w, h = rgba_im.size
    out = rgba_im.copy()
    px = out.load()
    orig_px = orig_im.load() if orig_im is not None else None

    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if a < 128:
                continue
            if orig_px is not None and 200 <= orig_px[x, y] <= 207:
                px[x, y] = (254, 0, orig_px[x, y], 255)
                continue

            lum = 0.299 * r + 0.587 * g + 0.114 * b
            # Green grass -> blighted purple-grey soil
            if g > r + 12 and g > b + 12:
                px[x, y] = (int(lum * 0.42 + 18), int(lum * 0.38 + 14), int(lum * 0.55 + 24), 255)
            # Bright stone / roof highlights -> pale bone / slate highlight
            elif lum > 140 and abs(r - g) < 35:
                px[x, y] = (min(255, int(lum * 0.85 + 20)), min(255, int(lum * 0.88 + 22)), min(255, int(lum * 0.98 + 35)), 255)
            # Warm wood / thatch / red roof -> dark obsidian slate
            elif r > g + 25:
                px[x, y] = (int(lum * 0.42 + 16), int(lum * 0.40 + 16), int(lum * 0.60 + 26), 255)
            # Cool stone masonry -> dark necrotic stone with deep purple/teal shadow
            else:
                px[x, y] = (int(lum * 0.50 + 15), int(lum * 0.52 + 16), int(lum * 0.68 + 24), 255)
    return out


def stamp_crystal(rgba_im, cx, cy, rx, ry):
    """Stamp a shaded floating necrotic Scourge crystal with highlights."""
    px = rgba_im.load()
    w, h = rgba_im.size
    for dy in range(-ry, ry + 1):
        span = int(rx * (1.0 - abs(dy) / float(ry + 1)))
        for dx in range(-span, span + 1):
            xx, yy = cx + dx, cy + dy
            if 0 <= xx < w and 0 <= yy < h:
                if abs(dx) + abs(dy) <= 2:
                    px[xx, yy] = (215, 255, 235, 255)
                elif abs(dx) == span or abs(dy) == ry:
                    px[xx, yy] = (15, 55, 40, 255)
                elif dx < 0 and dy < 0:
                    px[xx, yy] = (115, 245, 185, 255)
                elif dx <= 0:
                    px[xx, yy] = (50, 205, 145, 255)
                elif dy < 0:
                    px[xx, yy] = (38, 175, 120, 255)
                else:
                    px[xx, yy] = (22, 115, 80, 255)


# ==============================================================================
# 1. BUILD AUTHENTIC WC3 CRYPT (64x64) FROM HUMAN CHURCH (64x64 GOTHIC CATHEDRAL)
# ==============================================================================
def sculpt_crypt(base_church_path):
    base_im = Image.open(base_church_path)
    rgba = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
    px = rgba.load()
    w, h = rgba.size

    # 1. Sculpt 4 Vaulted Gothic Ribcage Arches over the stone roof
    # Rib curves soaring above the roofline
    rib_arcs = [
        # (center_x, top_y, left_x, right_x, bottom_y)
        (22, 10, 12, 32, 28),
        (32, 7,  18, 46, 28),
        (42, 10, 32, 52, 28),
    ]
    for cx_r, ty, lx, rx_r, by in rib_arcs:
        for t_step in range(30):
            t = t_step / 29.0
            # Parabolic curve
            x = int(lx + (rx_r - lx) * t)
            y = int(ty + (by - ty) * ((2 * t - 1) ** 2))
            if 0 <= x < w and 0 <= y < h:
                px[x, y] = (175, 170, 195, 255)
                if 0 <= y + 1 < h:
                    px[x, y + 1] = (65, 60, 80, 255)
                if 0 <= x - 1 < w:
                    px[x - 1, y] = (120, 115, 135, 255)

    # 2. Transform the arched entrance into a subterranean descent with glowing green mist
    # Find entrance area (center bottom of church facade, around x: 26..38, y: 36..48)
    for y in range(36, 48):
        for x in range(27, 38):
            d = abs(x - 32)
            if y < 40 and d > 3:
                continue
            dist_center = abs(x - 32) + abs(y - 42)
            if dist_center <= 2:
                px[x, y] = (160, 255, 185, 255)  # Eerie green inner glow
            elif dist_center <= 4:
                px[x, y] = (45, 210, 105, 255)
            elif dist_center <= 6:
                px[x, y] = (25, 120, 60, 255)
            else:
                px[x, y] = (12, 10, 18, 255)  # Abyss entrance

    # 3. Flanking stone gargoyle / nerubian statues on entrance buttresses
    for gx in (24, 40):
        # Gargoyle wings & body atop buttress
        px[gx - 1, 34] = (140, 135, 160, 255)
        px[gx + 1, 34] = (140, 135, 160, 255)
        px[gx, 35] = (95, 90, 115, 255)
        px[gx - 1, 36] = (255, 50, 40, 255)  # Glowing red eye
        px[gx + 1, 36] = (255, 50, 40, 255)

    # 4. Floating Scourge crystals atop spires
    stamp_crystal(rgba, 32, 6, 4, 6)
    stamp_crystal(rgba, 14, 18, 3, 4)
    stamp_crystal(rgba, 50, 18, 3, 4)

    return rgba


# ==============================================================================
# 2. BUILD AUTHENTIC WC3 GRAVEYARD (64x64) FROM HUMAN LUMBER MILL (64x64)
# ==============================================================================
def sculpt_graveyard(base_lm_path):
    base_im = Image.open(base_lm_path)
    rgba = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
    px = rgba.load()
    w, h = rgba.size

    # 1. Transform lumber yard / log stacks into open graves, bone piles, and tombstones
    # In human lumber mill, logs and yard are around x: 10..36, y: 28..50
    bone_white = (220, 215, 200, 255)
    bone_mid = (165, 160, 145, 255)
    bone_shadow = (85, 80, 75, 255)
    mist_green = (55, 225, 115, 200)

    # Convert log stacks into bone mounds
    for y in range(30, 46):
        for x in range(12, 34):
            r, g, b, a = px[x, y]
            if a > 0 and (x + y * 2) % 3 == 0:
                # Bone fragment
                px[x, y] = bone_white if (x + y) % 2 == 0 else bone_mid
            elif a > 0 and (x * 3 + y) % 5 == 0:
                px[x, y] = bone_shadow

    # Add crooked stone gravestones (slabs and crosses)
    tombstones = [
        (14, 32, "slab"),
        (20, 28, "cross"),
        (16, 42, "slab"),
        (26, 38, "cross"),
        (48, 42, "slab"),
        (52, 36, "cross"),
    ]
    for tx, ty, ttype in tombstones:
        if ttype == "slab":
            for dy in range(-5, 1):
                for dx in range(-2, 2):
                    if 0 <= tx + dx < w and 0 <= ty + dy < h:
                        px[tx + dx, ty + dy] = (130, 125, 145, 255) if dx < 0 else (65, 60, 80, 255)
            px[tx - 1, ty - 6] = (175, 170, 195, 255)
        elif ttype == "cross":
            for dy in range(-7, 1):
                px[tx, ty + dy] = (145, 140, 165, 255)
            for dx in range(-2, 3):
                px[tx + dx, ty - 4] = (145, 140, 165, 255)

    # 2. Add open grave pit with skeletal arm reaching upward
    for dy in range(4):
        for dx in range(6):
            px[18 + dx, 44 + dy] = (14, 10, 18, 255)
    # Skeletal fingers reaching from pit
    px[21, 43] = bone_white
    px[22, 42] = bone_white
    px[21, 41] = bone_white
    px[23, 41] = bone_white

    # 3. Add wrought-iron spires to perimeter fences
    for x in range(8, 56, 4):
        for y in (24, 25, 52, 53):
            if px[x, y][3] > 0:
                px[x, y - 2] = (150, 145, 165, 255)
                px[x, y - 1] = (85, 80, 100, 255)

    # 4. Rising green necrotic mist wisps
    mist_pts = [(16, 30), (22, 36), (48, 40), (28, 44), (32, 38)]
    for mx, my in mist_pts:
        px[mx, my] = mist_green
        px[mx + 1, my - 1] = (40, 185, 90, 160)

    # 5. Floating necrotic soul crystal above the stone mausoleum
    stamp_crystal(rgba, 44, 14, 4, 6)

    return rgba


# ==============================================================================
# 3. BUILD AUTHENTIC WC3 SACRIFICIAL PIT (64x64) FROM HUMAN STABLE (64x64)
# ==============================================================================
def sculpt_sacrificial_pit(base_stable_path):
    base_im = Image.open(base_stable_path)
    rgba = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
    px = rgba.load()
    w, h = rgba.size

    # Paddock area (center of stable around x: 18..46, y: 24..46)
    # Convert into a sunken obsidian stone basin with swirling ectoplasm pool
    for dy in range(-12, 13):
        for dx in range(-15, 16):
            dist_sq = (dx / 15.0)**2 + (dy / 12.0)**2
            xx = 32 + dx
            yy = 35 + dy
            if dist_sq <= 1.0:
                if dist_sq >= 0.85:
                    # Obsidian jagged stone rim
                    px[xx, yy] = (120, 115, 140, 255) if dx < 0 else (45, 40, 58, 255)
                elif dist_sq >= 0.65:
                    # Deep necrotic pool edge
                    px[xx, yy] = (25, 95, 50, 255)
                elif dist_sq >= 0.35:
                    # Swirling green ectoplasm
                    px[xx, yy] = (50, 215, 105, 255)
                else:
                    # Core soul vortex
                    px[xx, yy] = (185, 255, 210, 255)

    # 4 Floating obsidian focus obelisks with glowing runes around rim
    obelisks = [(18, 26), (46, 26), (18, 44), (46, 44)]
    for ox_p, oy_p in obelisks:
        for dy in range(-7, 3):
            span = max(1, 3 - abs(dy + 2) // 2)
            for dx in range(-span, span + 1):
                px[ox_p + dx, oy_p + dy] = (110, 105, 130, 255) if dx <= 0 else (45, 40, 58, 255)
        # Glowing green necrotic rune
        px[ox_p, oy_p - 3] = (60, 255, 130, 255)
        px[ox_p, oy_p - 2] = (60, 255, 130, 255)

    # Floating central soul crystal
    stamp_crystal(rgba, 32, 16, 4, 6)

    return rgba


# ==============================================================================
# 4. BUILD AUTHENTIC WC3 CRYPT FIEND FROM BLIZZARD SPIDER (160x448, 14 ROWS)
# ==============================================================================
def sculpt_crypt_fiend(spider_path):
    spider_im = Image.open(spider_path)
    rgba = spider_im.convert("RGBA")
    orig_px = spider_im.load()
    px = rgba.load()
    w, h = rgba.size  # 160x448 (5 cols x 14 rows, 32x32 frames)

    # Colors
    chitin_high = (125, 115, 150, 255)
    chitin_mid = (68, 58, 88, 255)
    chitin_dark = (32, 26, 44, 255)
    chitin_shadow = (18, 14, 25, 255)
    chevron_pale = (185, 195, 215, 255)
    scythe_steel = (215, 225, 240, 255)
    eye_green = (45, 255, 120, 255)
    venom_green = (35, 210, 90, 255)

    for row in range(14):
        for col in range(5):
            ox = col * 32
            oy = row * 32

            # Find bounding box of spider in this frame
            pts = []
            for y in range(32):
                for x in range(32):
                    p = orig_px[ox + x, oy + y]
                    if p != 255:
                        pts.append((x, y, px[ox + x, oy + y]))

            if not pts:
                continue

            min_x = min(p[0] for p in pts)
            max_x = max(p[0] for p in pts)
            min_y = min(p[1] for p in pts)
            max_y = max(p[1] for p in pts)
            cx = (min_x + max_x) // 2
            cy = (min_y + max_y) // 2

            # 1. Recolor spider body into obsidian nerubian chitin
            for x, y, (r, g, b, a) in pts:
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                xx = ox + x
                yy = oy + y

                # Spider abdomen markings -> pale chevron stripes
                if y > cy and abs(x - cx) in (2, 4, 6) and (x + y) % 2 == 0:
                    px[xx, yy] = chevron_pale
                elif y > cy and abs(x - cx) <= 1:
                    px[xx, yy] = venom_green  # Glowing venom node
                elif lum > 130:
                    px[xx, yy] = chitin_high
                elif lum > 80:
                    px[xx, yy] = chitin_mid
                elif lum > 40:
                    px[xx, yy] = chitin_dark
                else:
                    px[xx, yy] = chitin_shadow

            # Skip adding humanoid torso to death frames (rows 11..13)
            if row in (11, 12, 13):
                continue

            # 2. Add upright Nerubian humanoid carapace torso atop spider cephalothorax
            torso_y = min_y + 2
            # Carapace chestplate
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if abs(dx) + abs(dy) <= 4:
                        xx = ox + cx + dx
                        yy = oy + torso_y + dy
                        if 0 <= xx < w and 0 <= yy < h:
                            px[xx, yy] = chitin_high if dx <= 0 else chitin_mid

            # Spiked shoulder carapaces
            if 0 <= ox + cx - 4 < w and 0 <= oy + torso_y - 2 < h:
                px[ox + cx - 4, oy + torso_y - 2] = scythe_steel
                px[ox + cx - 5, oy + torso_y - 3] = scythe_steel
            if 0 <= ox + cx + 4 < w and 0 <= oy + torso_y - 2 < h:
                px[ox + cx + 4, oy + torso_y - 2] = scythe_steel
                px[ox + cx + 5, oy + torso_y - 3] = scythe_steel

            # 3. Double Mantis Scythe Claws
            # Attack frames (rows 7, 8, 9, 10): Scythes strike forward
            is_attack = (row in (7, 8, 9, 10))
            scythe_l_y = torso_y - (4 if is_attack else -1)
            scythe_r_y = torso_y - (4 if is_attack else -1)
            # Left scythe claw
            if 0 <= ox + cx - 4 < w and 0 <= oy + scythe_l_y < h:
                px[ox + cx - 4, oy + scythe_l_y] = scythe_steel
                px[ox + cx - 5, oy + scythe_l_y + 1] = scythe_steel
                px[ox + cx - 6, oy + scythe_l_y + 2] = chitin_high
            # Right scythe claw
            if 0 <= ox + cx + 4 < w and 0 <= oy + scythe_r_y < h:
                px[ox + cx + 4, oy + scythe_r_y] = scythe_steel
                px[ox + cx + 5, oy + scythe_r_y + 1] = scythe_steel
                px[ox + cx + 6, oy + scythe_r_y + 2] = chitin_high

            # 4. Horned Nerubian Visor & Glowing Green Eyes
            head_y = torso_y - 4
            if 0 <= ox + cx < w and 0 <= oy + head_y < h:
                px[ox + cx, oy + head_y] = chitin_high
                px[ox + cx - 1, oy + head_y - 1] = scythe_steel  # Left horn tip
                px[ox + cx + 1, oy + head_y - 1] = scythe_steel  # Right horn tip
                # 4 Glowing green cluster eyes
                px[ox + cx - 1, oy + head_y + 1] = eye_green
                px[ox + cx + 1, oy + head_y + 1] = eye_green
                px[ox + cx, oy + head_y + 2] = eye_green
                # Mandibles
                px[ox + cx - 1, oy + head_y + 3] = scythe_steel
                px[ox + cx + 1, oy + head_y + 3] = scythe_steel

    return rgba


# ==============================================================================
# 5. BUILD AUTHENTIC WC3 ABOMINATION FROM BLIZZARD OGRE (240x720, 15 ROWS, 48x48)
# ==============================================================================
def sculpt_abomination(ogre_path):
    ogre_im = Image.open(ogre_path)
    rgba = ogre_im.convert("RGBA")
    orig_px = ogre_im.load()
    px = rgba.load()
    w, h = rgba.size  # 240x720 (5 cols x 15 rows, 48x48 frames)

    # Colors
    flesh_shadow = (42, 52, 45, 255)
    flesh_dark = (72, 85, 70, 255)
    flesh_mid = (115, 130, 105, 255)
    flesh_high = (165, 180, 150, 255)
    suture_black = (18, 14, 20, 255)
    suture_red = (85, 18, 25, 255)
    cleaver_metal = (195, 200, 210, 255)
    cleaver_edge = (235, 240, 250, 255)
    cleaver_blood = (165, 25, 35, 255)
    cleaver_dark = (65, 70, 80, 255)
    hook_rust = (135, 75, 55, 255)
    bone_white = (220, 215, 195, 255)
    eye_dead = (225, 235, 140, 255)

    for row in range(15):
        for col in range(5):
            ox = col * 48
            oy = row * 48

            # Find bounds
            pts = []
            for y in range(48):
                for x in range(48):
                    p = orig_px[ox + x, oy + y]
                    if p != 255:
                        pts.append((x, y, px[ox + x, oy + y]))

            if not pts:
                continue

            min_x = min(p[0] for p in pts)
            max_x = max(p[0] for p in pts)
            min_y = min(p[1] for p in pts)
            max_y = max(p[1] for p in pts)
            cx = (min_x + max_x) // 2
            cy = (min_y + max_y) // 2

            # 1. Recolor Ogre body into decaying corpse-flesh
            for x, y, (r, g, b, a) in pts:
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                xx = ox + x
                yy = oy + y

                # Replace Ogre wooden club with dark iron / blood
                if (x > cx + 6 or y < cy - 6) and (r > g + 15 and r > b + 15):
                    px[xx, yy] = cleaver_dark if lum < 100 else cleaver_metal
                elif lum > 140:
                    px[xx, yy] = flesh_high
                elif lum > 95:
                    px[xx, yy] = flesh_mid
                elif lum > 55:
                    px[xx, yy] = flesh_dark
                else:
                    px[xx, yy] = flesh_shadow

            # Death frames (rows 12, 13, 14): add blood pooling and dislodged organs
            if row in (12, 13, 14):
                for dy in range(cy + 4, max_y + 1):
                    for dx in range(min_x, max_x + 1):
                        if (dx + dy) % 2 == 0:
                            px[ox + dx, oy + dy] = cleaver_blood
                continue

            # 2. Heavy surgical cross-sutures across bloated belly and chest
            belly_top = cy - 4
            belly_bot = min(cy + 8, max_y - 2)
            # Vertical surgical incision with cross stitches
            for sy in range(belly_top, belly_bot):
                px[ox + cx, oy + sy] = suture_red
                if sy % 2 == 0:
                    px[ox + cx - 1, oy + sy] = suture_black
                    px[ox + cx + 1, oy + sy] = suture_black
                    px[ox + cx - 2, oy + sy] = suture_black
                    px[ox + cx + 2, oy + sy] = suture_black
            # Diagonal chest incision
            for d in range(-4, 5):
                px[ox + cx - 5 + d, oy + cy - 6 + d] = suture_black

            # 3. Third vestigial arm / bone claw sprouting from left shoulder
            shoulder_x = cx - 8
            shoulder_y = cy - 7
            for d in range(5):
                px[ox + shoulder_x - d, oy + shoulder_y - d] = flesh_dark
            # Bone claw tip
            px[ox + shoulder_x - 5, oy + shoulder_y - 5] = bone_white
            px[ox + shoulder_x - 6, oy + shoulder_y - 4] = bone_white

            # 4. Giant Butcher's Cleaver in right hand
            # Cleaver blade replaces club
            hand_r_x = cx + 10
            hand_r_y = cy + 2
            for by in range(-7, 7):
                for bx in range(1, 8):
                    bx_pos = ox + hand_r_x + bx
                    by_pos = oy + hand_r_y + by
                    if 0 <= bx_pos < w and 0 <= by_pos < h:
                        if bx == 7:
                            px[bx_pos, by_pos] = cleaver_edge  # Sharp razor blade edge
                        elif by >= 3 and bx >= 5:
                            px[bx_pos, by_pos] = cleaver_blood  # Blood spatter on blade
                        else:
                            px[bx_pos, by_pos] = cleaver_metal

            # 5. Meat Hook with chain in left hand
            hand_l_x = cx - 10
            hand_l_y = cy + 4
            # Hook curve
            px[ox + hand_l_x - 1, oy + hand_l_y + 2] = hook_rust
            px[ox + hand_l_x - 2, oy + hand_l_y + 3] = hook_rust
            px[ox + hand_l_x - 1, oy + hand_l_y + 4] = cleaver_metal
            px[ox + hand_l_x, oy + hand_l_y + 3] = hook_rust

            # 6. Grotesque stitched face
            head_x = cx
            head_y = min_y + 3
            # Forehead surgical seam
            for d in range(-3, 4, 2):
                px[ox + head_x + d, oy + head_y - 1] = suture_black
            # Dead yellowish glowing eye & sewn shut eye
            px[ox + head_x - 2, oy + head_y] = eye_dead
            px[ox + head_x + 2, oy + head_y] = suture_black
            # Crooked rotting teeth
            px[ox + head_x - 2, oy + head_y + 3] = bone_white
            px[ox + head_x, oy + head_y + 3] = bone_white
            px[ox + head_x + 2, oy + head_y + 3] = bone_white

    return rgba


# ==============================================================================
# 6. BUILD AUTHENTIC WC1 ICONS (27x19) FROM PORTRAIT_ICONS FRAMES
# ==============================================================================
def get_icon_frame(pi_im, frame_idx):
    box = (0, frame_idx * 19, 27, (frame_idx + 1) * 19)
    crop = pi_im.crop(box)
    return crop.convert("RGBA"), crop


def build_all_scourge_icons(ref_pal):
    pi_path = os.path.join(GRAPHICS_DIR, "tilesets", "forest", "portrait_icons.png")
    pi_im = Image.open(pi_path)

    # 1. icon-abomination.png from frame 44 (Ogre icon)
    ogre_rgba, ogre_p = get_icon_frame(pi_im, 44)
    abom_rgba = ogre_rgba.copy()
    px = abom_rgba.load()
    # Recolor flesh to corpse green
    for y in range(19):
        for x in range(27):
            r, g, b, a = px[x, y]
            if a > 0:
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                px[x, y] = (int(lum * 0.72 + 20), int(lum * 0.82 + 22), int(lum * 0.65 + 18), 255)
    # Stitches across forehead and cheek
    for sx in (8, 10, 12, 14, 16):
        px[sx, 6] = (18, 14, 20, 255)
    px[10, 8] = (225, 235, 140, 255)  # Dead eye
    px[16, 8] = (18, 14, 20, 255)   # Sewn eye
    # Cleaver blade in corner
    for by in range(5, 15):
        px[3, by] = (195, 200, 210, 255)
        px[4, by] = (235, 240, 250, 255)
        if by > 10:
            px[4, by] = (165, 25, 35, 255)
    save_transparent_png(rgba_to_indexed_with_transparency(abom_rgba, ref_pal, ogre_p),
                         os.path.join(UI_FORSAKEN_DIR, "icon-abomination.png"))

    # 2. icon-crypt-fiend.png from frame 45 (Spider icon)
    spider_rgba, spider_p = get_icon_frame(pi_im, 45)
    cf_rgba = spider_rgba.copy()
    px = cf_rgba.load()
    # Recolor to dark obsidian nerubian chitin
    for y in range(19):
        for x in range(27):
            r, g, b, a = px[x, y]
            if a > 0:
                lum = 0.299 * r + 0.587 * g + 0.114 * b
                px[x, y] = (int(lum * 0.45 + 18), int(lum * 0.40 + 16), int(lum * 0.60 + 26), 255)
    # 4 Glowing green eyes
    px[12, 8] = (45, 255, 120, 255)
    px[14, 8] = (45, 255, 120, 255)
    px[13, 9] = (45, 255, 120, 255)
    px[13, 7] = (45, 255, 120, 255)
    # Scythe claws flanking
    for dy in range(6):
        px[5, 10 + dy] = (215, 225, 240, 255)
        px[21, 10 + dy] = (215, 225, 240, 255)
    save_transparent_png(rgba_to_indexed_with_transparency(cf_rgba, ref_pal, spider_p),
                         os.path.join(UI_FORSAKEN_DIR, "icon-crypt-fiend.png"))

    # 3. icon-forsaken-barracks.png (Crypt) from frame 28 (Human Church)
    church_rgba, church_p = get_icon_frame(pi_im, 28)
    crypt_rgba = recolor_to_obsidian_undead(church_rgba, church_p)
    px = crypt_rgba.load()
    # Vaulted rib arches
    for rx in range(8, 20):
        px[rx, 4] = (175, 170, 195, 255)
    # Green subterranean portal
    for y in range(11, 16):
        for x in range(11, 16):
            px[x, y] = (45, 220, 110, 255) if abs(x - 13) + abs(y - 13) <= 2 else (18, 14, 25, 255)
    stamp_crystal(crypt_rgba, 13, 3, 2, 3)
    save_transparent_png(rgba_to_indexed_with_transparency(crypt_rgba, ref_pal, church_p),
                         os.path.join(UI_FORSAKEN_DIR, "icon-forsaken-barracks.png"))

    # 4. icon-forsaken-lumber-mill.png (Graveyard) from frame 22 (Human Lumber Mill)
    lm_rgba, lm_p = get_icon_frame(pi_im, 22)
    gy_rgba = recolor_to_obsidian_undead(lm_rgba, lm_p)
    px = gy_rgba.load()
    # Bones and tombstones
    for tx in (4, 7, 22):
        px[tx, 12] = (165, 160, 180, 255)
        px[tx, 13] = (165, 160, 180, 255)
        px[tx, 14] = (165, 160, 180, 255)
    px[12, 13] = (45, 220, 110, 255)  # Mist
    px[16, 14] = (45, 220, 110, 255)
    stamp_crystal(gy_rgba, 14, 3, 2, 3)
    save_transparent_png(rgba_to_indexed_with_transparency(gy_rgba, ref_pal, lm_p),
                         os.path.join(UI_FORSAKEN_DIR, "icon-forsaken-lumber-mill.png"))

    # 5. icon-forsaken-stable.png (Sacrificial Pit) from frame 24 (Human Stable)
    stable_rgba, stable_p = get_icon_frame(pi_im, 24)
    sp_rgba = recolor_to_obsidian_undead(stable_rgba, stable_p)
    px = sp_rgba.load()
    # Swirling green pool in center
    for y in range(7, 13):
        for x in range(10, 18):
            if (x - 14)**2 + (y - 10)**2 <= 12:
                px[x, y] = (50, 225, 115, 255) if abs(x - 14) <= 1 else (25, 120, 60, 255)
    stamp_crystal(sp_rgba, 14, 3, 2, 3)
    save_transparent_png(rgba_to_indexed_with_transparency(sp_rgba, ref_pal, stable_p),
                         os.path.join(UI_FORSAKEN_DIR, "icon-forsaken-stable.png"))

    print("All Scourge icons generated with authentic WC1 frames and transparency=255!")


# ==============================================================================
# MAIN RUNNER
# ==============================================================================
def main():
    print("Building authentic Blizzard-quality Scourge assets with full transparency...")

    # Reference palettes
    town_hall_ref = Image.open(os.path.join(GRAPHICS_DIR, "tilesets", "forest", "orc", "buildings", "town_hall.png"))
    b_pal = town_hall_ref.getpalette()

    unit_ref = Image.open(os.path.join(GRAPHICS_DIR, "orc", "units", "raider.png"))
    u_pal = unit_ref.getpalette()

    # 1. BUILDINGS for forest and swamp
    for ts in ("forest", "swamp"):
        out_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "forsaken", "buildings")
        hum_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "human", "buildings")

        # A. Crypt (barracks.png & barracks_construction.png)
        crypt_rgba = sculpt_crypt(os.path.join(hum_dir, "church.png"))
        crypt_idx = rgba_to_indexed_with_transparency(crypt_rgba, b_pal)
        save_transparent_png(crypt_idx, os.path.join(out_dir, "barracks.png"))

        # Construction
        c_base = Image.open(os.path.join(hum_dir, "church_construction.png"))
        c_rgba = recolor_to_obsidian_undead(c_base.convert("RGBA"), c_base)
        c_rgba.paste(crypt_rgba, (0, 128), crypt_rgba)
        stamp_crystal(c_rgba, 32, 64 + 18, 4, 5)
        save_transparent_png(rgba_to_indexed_with_transparency(c_rgba, b_pal, c_base),
                             os.path.join(out_dir, "barracks_construction.png"))
        print(f"[{ts}] Saved Crypt: 64x64, constr 64x192 with transparency=255")

        # B. Graveyard (lumber_mill.png & lumber_mill_construction.png)
        gy_rgba = sculpt_graveyard(os.path.join(hum_dir, "lumber_mill.png"))
        gy_idx = rgba_to_indexed_with_transparency(gy_rgba, b_pal)
        save_transparent_png(gy_idx, os.path.join(out_dir, "lumber_mill.png"))

        # Construction
        c_base = Image.open(os.path.join(hum_dir, "lumber_mill_construction.png"))
        c_rgba = recolor_to_obsidian_undead(c_base.convert("RGBA"), c_base)
        c_rgba.paste(gy_rgba, (0, 128), gy_rgba)
        stamp_crystal(c_rgba, 44, 64 + 16, 4, 5)
        save_transparent_png(rgba_to_indexed_with_transparency(c_rgba, b_pal, c_base),
                             os.path.join(out_dir, "lumber_mill_construction.png"))
        print(f"[{ts}] Saved Graveyard: 64x64, constr 64x192 with transparency=255")

        # C. Sacrificial Pit (stable.png & stable_construction.png)
        sp_rgba = sculpt_sacrificial_pit(os.path.join(hum_dir, "stable.png"))
        sp_idx = rgba_to_indexed_with_transparency(sp_rgba, b_pal)
        save_transparent_png(sp_idx, os.path.join(out_dir, "stable.png"))

        # Construction
        c_base = Image.open(os.path.join(hum_dir, "stable_construction.png"))
        c_rgba = recolor_to_obsidian_undead(c_base.convert("RGBA"), c_base)
        c_rgba.paste(sp_rgba, (0, 128), sp_rgba)
        stamp_crystal(c_rgba, 32, 64 + 18, 4, 5)
        save_transparent_png(rgba_to_indexed_with_transparency(c_rgba, b_pal, c_base),
                             os.path.join(out_dir, "stable_construction.png"))
        print(f"[{ts}] Saved Sacrificial Pit: 64x64, constr 64x192 with transparency=255")

    # 2. UNITS
    import scripts.fix_all_scourge_unit_glitches as unit_glitch_fix
    unit_glitch_fix.main()

    # 3. ICONS
    build_all_scourge_icons(b_pal)
    print("ALL SCENERY, UNITS, AND ICONS BUILT WITH FULL TRANSPARENCY & BLIZZARD QUALITY!")


if __name__ == "__main__":
    main()
