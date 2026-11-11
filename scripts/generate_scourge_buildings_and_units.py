#!/usr/bin/env python3
"""
Generate authentic Warcraft III Scourge buildings and units for Forsaken mod:
1. Crypt (barracks.png): Iconic gothic stone tomb with 4 vaulted ribcage arches,
   sunken glowing portal, gargoyle watchers, cold cyan Scourge crystals (64x64).
2. Graveyard (lumber_mill.png): 64x64 blighted burial ground with central mausoleum,
   iron spiked perimeter fence, crooked gravestones, bone piles, glowing necrotic mist.
3. Sacrificial Pit (stable.png): 64x64 obsidian ring with central swirling ectoplasmic pool.
4. Crypt Fiend (crypt_fiend.png): 160x320 32x32 frames, Nerubian spider warrior with 6 legs,
   chitinous abdomen, twin scythe forelimbs, multi-eyed helmeted visage.
5. Abomination (abomination.png): 240x720 48x48 frames, grotesque stitched meat golem with
   cleaver, meat hook, swollen sutured gut, vestigial shoulder arm.
6. Icons for Crypt Fiend, Abomination, Crypt, Graveyard, Sacrificial Pit (27x19).
"""

import os
import math
from PIL import Image, ImageDraw

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


def rgba_to_indexed(rgba_im, ref_pal):
    w, h = rgba_im.size
    out = Image.new("P", (w, h), 255)
    out.putpalette(ref_pal)
    src_px = rgba_im.load()
    out_px = out.load()
    find_idx = get_palette_matcher(ref_pal)

    for y in range(h):
        for x in range(w):
            r, g, b, a = src_px[x, y]
            if a < 128:
                out_px[x, y] = 255
            elif r == 254 and g == 0 and 200 <= b <= 207:
                out_px[x, y] = b
            else:
                out_px[x, y] = find_idx(r, g, b)
    return out


def recolor_to_obsidian(rgba_im, orig_im=None):
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
            if g > r + 12 and g > b + 12:
                # Green/grass -> Blighted purple-grey turf
                px[x, y] = (int(lum * 0.45 + 18), int(lum * 0.40 + 16), int(lum * 0.55 + 24), 255)
            elif lum > 145 and abs(r - g) < 35:
                # Bright highlights -> pale bone / cold slate
                px[x, y] = (min(255, int(lum * 0.90 + 15)), min(255, int(lum * 0.92 + 18)), min(255, int(lum * 0.98 + 25)), 255)
            elif r > g + 35 and r > b + 35:
                # Warm wood/earth -> dark obsidian slate
                px[x, y] = (int(lum * 0.45 + 16), int(lum * 0.48 + 18), int(lum * 0.65 + 28), 255)
            else:
                # Stone -> dark necrotic slate with teal tinge
                px[x, y] = (int(lum * 0.55 + 16), int(lum * 0.60 + 18), int(lum * 0.72 + 25), 255)
    return out


def stamp_crystal(im, cx, cy, rx, ry):
    px = im.load()
    w, h = im.size
    for dy in range(-ry, ry + 1):
        span = int(rx * (1.0 - abs(dy) / float(ry + 1)))
        for dx in range(-span, span + 1):
            xx, yy = cx + dx, cy + dy
            if 0 <= xx < w and 0 <= yy < h:
                if abs(dx) + abs(dy) <= 2:
                    px[xx, yy] = (210, 255, 230, 255)
                elif abs(dx) == span or abs(dy) == ry:
                    px[xx, yy] = (15, 60, 45, 255)
                elif dx < 0 and dy < 0:
                    px[xx, yy] = (120, 245, 190, 255)
                elif dx <= 0:
                    px[xx, yy] = (50, 200, 150, 255)
                elif dy < 0:
                    px[xx, yy] = (40, 170, 130, 255)
                else:
                    px[xx, yy] = (25, 110, 85, 255)


def build_wc3_crypt(ref_stone):
    """
    Build an authentic 64x64 WC3 Scourge Crypt:
    - Symmetrical dark obsidian and slate-grey mausoleum structure.
    - 4 prominent vaulted ribcage stone arches soaring over the roofline.
    - Deep arched subterranean portal descending below, glowing necrotic green inside.
    - Two stone gargoyle watchers perched on flanking plinths.
    - Floating cyan Scourge crystals and iron spires.
    """
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    px = im.load()

    # Base ground plinth (blighted soil & stone foundation)
    draw.polygon([(8, 48), (32, 34), (56, 48), (32, 60)], fill=(32, 26, 40, 255))
    draw.polygon([(10, 48), (32, 36), (54, 48), (32, 58)], fill=(42, 36, 52, 255))

    # Stepped dark stone crypt foundation
    for i in range(4):
        y_top = 44 - i * 3
        draw.polygon([(12 + i * 2, y_top), (32, y_top - 10), (52 - i * 2, y_top), (32, y_top + 10)],
                     fill=(28 + i * 6, 25 + i * 5, 38 + i * 7, 255),
                     outline=(18, 15, 25, 255))

    # Main crypt tomb body (x: 14..50, y: 18..46)
    # Front facing walls with vertical dark slate masonry
    for y in range(24, 48):
        for x in range(16, 49):
            d = abs(x - 32)
            if y < 38 - d // 2:
                continue
            lum = 35 + (y - 24) * 2 - d * 2
            # Add brick/stone texture variation
            if (x % 6 == 0 and (y // 4) % 2 == 0) or (y % 4 == 0):
                px[x, y] = (18, 16, 24, 255)
            elif x < 32:
                px[x, y] = (lum + 10, lum + 12, lum + 20, 255)
            else:
                px[x, y] = (lum, lum + 2, lum + 8, 255)

    # Sunken arched portal leading down into the subterranean crypt
    # Archway frame (obsidian stone blocks)
    for dy in range(-12, 10):
        arch_w = int(10 * math.sqrt(max(0.0, 1.0 - (dy / 13.0) ** 2))) if dy < 0 else 10
        for dx in range(-arch_w, arch_w + 1):
            xx, yy = 32 + dx, 36 + dy
            if abs(dx) == arch_w or dy == -12:
                # Heavy stone keystone & voussoirs
                px[xx, yy] = (75, 70, 95, 255) if dx < 0 else (45, 40, 60, 255)
            else:
                # Inner crypt darkness with necrotic green mist
                dist = abs(dx) + abs(dy - 4)
                if dist < 4:
                    px[xx, yy] = (160, 255, 180, 255)  # Eerie green portal glow
                elif dist < 7:
                    px[xx, yy] = (40, 180, 90, 255)
                elif dist < 10:
                    px[xx, yy] = (15, 70, 40, 255)
                else:
                    px[xx, yy] = (10, 8, 16, 255)

    # Steps descending into portal
    for st in range(3):
        sy = 43 + st * 2
        sw = 9 - st * 2
        draw.line([(32 - sw, sy), (32 + sw, sy)], fill=(55 - st * 10, 50 - st * 10, 70 - st * 10, 255))

    # Four iconic ribcage stone arches curving over the Crypt roof
    # Rib 1 (front left), Rib 2 (rear left), Rib 3 (rear right), Rib 4 (front right)
    ribs = [
        # (base_x, base_y, peak_x, peak_y, thickness)
        (16, 38, 28, 14, 2),
        (22, 32, 30, 12, 2),
        (42, 32, 34, 12, 2),
        (48, 38, 36, 14, 2),
    ]
    for bx, by, px_peak, py_peak, th in ribs:
        # Draw arched bezier curve
        for t_step in range(25):
            t = t_step / 24.0
            # Quadratic curve
            rx = (1 - t)**2 * bx + 2 * (1 - t) * t * (bx if bx < 32 else bx) + t**2 * px_peak
            ry = (1 - t)**2 * by + 2 * (1 - t) * t * (py_peak - 4) + t**2 * py_peak
            ix, iy = int(round(rx)), int(round(ry))
            for dth in range(-th // 2, th // 2 + 1):
                if 0 <= ix + dth < 64 and 0 <= iy < 64:
                    # Shaded bone/obsidian rib
                    if t < 0.5:
                        px[ix + dth, iy] = (145, 140, 165, 255) if dth <= 0 else (65, 60, 85, 255)
                    else:
                        px[ix + dth, iy] = (185, 180, 205, 255) if dth <= 0 else (95, 90, 115, 255)

    # Central crest & carved nerubian skull above portal
    draw.rectangle([30, 21, 34, 25], fill=(160, 155, 175, 255), outline=(35, 30, 45, 255))
    px[31, 23] = (30, 255, 120, 255)
    px[33, 23] = (30, 255, 120, 255)

    # Flanking stone gargoyles / nerubian watchers on stone pillars
    for gx in (13, 51):
        # Pillar
        draw.rectangle([gx - 2, 30, gx + 2, 44], fill=(45, 40, 58, 255), outline=(22, 18, 30, 255))
        # Gargoyle body
        draw.rectangle([gx - 2, 25, gx + 2, 29], fill=(68, 62, 85, 255))
        # Horns / wings
        px[gx - 3, 25] = (110, 105, 130, 255)
        px[gx + 3, 25] = (110, 105, 130, 255)
        # Eyes
        px[gx - 1, 27] = (255, 60, 50, 255)
        px[gx + 1, 27] = (255, 60, 50, 255)

    # Floating Scourge necrotic crystals at top apex
    stamp_crystal(im, 32, 10, 4, 6)
    stamp_crystal(im, 20, 18, 3, 4)
    stamp_crystal(im, 44, 18, 3, 4)

    # Cobwebbing in upper corners
    for wx, wy in [(18, 22), (19, 23), (20, 24), (46, 22), (45, 23), (44, 24)]:
        px[wx, wy] = (180, 190, 210, 160)

    return im


def build_wc3_graveyard():
    """
    Build an authentic 64x64 WC3 Scourge Graveyard:
    - 64x64 dark blighted burial turf.
    - Central stone tomb / mausoleum with pediment & carved skull.
    - Wrought-iron spiked perimeter fence with stone corner posts.
    - Crooked stone tombstones, cross gravestones, fresh open grave pit with bones.
    - Ghostly green necrotic mist rising from the soil.
    - Floating lantern / necrotic crystal.
    """
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    px = im.load()

    # Blighted ground base (dark violet-charcoal soil)
    draw.polygon([(6, 32), (32, 14), (58, 32), (32, 50)], fill=(30, 24, 38, 255))
    draw.polygon([(4, 34), (32, 16), (60, 34), (32, 52)], fill=(24, 20, 32, 255))

    # Soil texture variation & bone fragments
    for y in range(20, 50):
        for x in range(8, 56):
            if px[x, y][3] > 0:
                if (x + y * 3) % 7 == 0:
                    px[x, y] = (18, 14, 24, 255)
                elif (x * 2 + y) % 11 == 0:
                    px[x, y] = (45, 38, 55, 255)

    # Wrought iron fence with spiked palisades along edges
    fence_posts = [(8, 32), (20, 23), (32, 16), (44, 23), (56, 32), (44, 41), (32, 48), (20, 41)]
    for idx in range(len(fence_posts)):
        x0, y0 = fence_posts[idx]
        x1, y1 = fence_posts[(idx + 1) % len(fence_posts)]
        if idx in (5, 6):  # Leave opening at front right for entrance gate
            continue
        # Iron horizontal rail
        draw.line([(x0, y0 - 4), (x1, y1 - 4)], fill=(45, 42, 52, 255), width=1)
        # Spikes along the segment
        for step in range(5):
            sx = int(x0 + (x1 - x0) * step / 4.0)
            sy = int(y0 + (y1 - y0) * step / 4.0)
            draw.line([(sx, sy), (sx, sy - 7)], fill=(65, 60, 75, 255), width=1)
            px[sx, sy - 8] = (130, 125, 145, 255)  # Spire tip

    # Stone corner posts
    for fx, fy in fence_posts:
        draw.rectangle([fx - 1, fy - 6, fx + 1, fy], fill=(60, 55, 70, 255), outline=(25, 20, 32, 255))
        px[fx, fy - 7] = (165, 160, 180, 255)  # Pointed cap

    # Central Stone Mausoleum / Tomb (x: 20..44, y: 18..36)
    # Foundation
    draw.polygon([(20, 30), (32, 22), (44, 30), (32, 38)], fill=(40, 35, 50, 255), outline=(20, 16, 26, 255))
    # Walls
    draw.rectangle([23, 22, 41, 32], fill=(52, 48, 64, 255), outline=(26, 22, 34, 255))
    # Shading on walls
    for wy in range(23, 32):
        for wx in range(24, 32):
            px[wx, wy] = (70, 65, 85, 255)
        for wx in range(32, 41):
            px[wx, wy] = (45, 40, 56, 255)
    # Arched entrance into mausoleum
    draw.rectangle([29, 26, 35, 32], fill=(12, 10, 18, 255))
    draw.line([(30, 25), (34, 25)], fill=(12, 10, 18, 255))
    # Green ghostly glow inside tomb
    px[32, 29] = (80, 255, 140, 255)
    px[32, 30] = (30, 190, 70, 255)

    # Pitched slate roof / pediment
    draw.polygon([(21, 22), (32, 14), (43, 22)], fill=(65, 60, 80, 255), outline=(28, 24, 36, 255))
    # Carved skull on pediment
    px[32, 18] = (200, 195, 185, 255)
    px[31, 19] = (200, 195, 185, 255)
    px[33, 19] = (200, 195, 185, 255)
    px[31, 18] = (20, 15, 25, 255)  # Left eye socket
    px[33, 18] = (20, 15, 25, 255)  # Right eye socket

    # Open fresh grave pit with exposed bones (bottom left)
    draw.rectangle([13, 38, 21, 44], fill=(12, 9, 16, 255), outline=(32, 24, 18, 255))
    # Bone mound next to grave
    draw.ellipse([21, 39, 25, 43], fill=(175, 170, 155, 255))
    px[23, 40] = (220, 215, 205, 255)
    # Protruding skeletal arm reaching from grave
    draw.line([(15, 42), (16, 37)], fill=(215, 210, 195, 255))
    draw.line([(16, 37), (18, 35)], fill=(215, 210, 195, 255))
    px[17, 34] = (235, 230, 220, 255)  # Skeletal fingers

    # Crooked gravestones (stone slabs & cross markers)
    tombstones = [
        # (x, y, type)
        (12, 28, "slab"),
        (16, 32, "cross"),
        (47, 26, "slab"),
        (51, 33, "cross"),
        (42, 42, "slab"),
        (48, 44, "slab")
    ]
    for tx, ty, ttype in tombstones:
        if ttype == "slab":
            draw.rectangle([tx - 2, ty - 5, tx + 1, ty], fill=(85, 80, 95, 255), outline=(30, 25, 38, 255))
            px[tx - 1, ty - 6] = (120, 115, 135, 255)  # Highlight
            px[tx, ty - 6] = (120, 115, 135, 255)
            # Weathered crack
            px[tx, ty - 2] = (25, 20, 32, 255)
        elif ttype == "cross":
            draw.line([(tx, ty - 7), (tx, ty)], fill=(95, 90, 110, 255), width=1)
            draw.line([(tx - 2, ty - 5), (tx + 2, ty - 5)], fill=(95, 90, 110, 255), width=1)
            px[tx, ty - 7] = (145, 140, 165, 255)

    # Ghostly green necrotic mist wisps rising from graves
    mist_coords = [(15, 35), (16, 34), (43, 38), (44, 37), (32, 42), (33, 41)]
    for mx, my in mist_coords:
        px[mx, my] = (70, 235, 120, 180)
        px[mx + 1, my] = (40, 190, 90, 130)

    # Floating necrotic focus crystal above mausoleum
    stamp_crystal(im, 32, 10, 3, 5)

    return im


def build_wc3_sacrificial_pit():
    """
    Build an authentic 64x64 WC3 Scourge Sacrificial Pit:
    - 64x64 sunken obsidian ringed pit.
    - Swirling ectoplasmic green necrotic summoning vortex in center.
    - 4 floating obsidian focus pillars/obelisks with glowing runes.
    - Heavy iron chains binding the summoning circle.
    """
    im = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    px = im.load()

    # Outer blighted ground
    draw.polygon([(8, 32), (32, 16), (56, 32), (32, 48)], fill=(32, 26, 42, 255))

    # Stepped obsidian ring around pit
    draw.ellipse([14, 20, 50, 44], fill=(45, 38, 55, 255), outline=(22, 18, 30, 255), width=2)
    draw.ellipse([17, 22, 47, 42], fill=(28, 22, 36, 255))

    # Swirling necrotic green ectoplasm pool
    draw.ellipse([20, 25, 44, 39], fill=(25, 120, 60, 255))
    draw.ellipse([23, 27, 41, 37], fill=(55, 215, 100, 255))
    draw.ellipse([27, 29, 37, 35], fill=(160, 255, 180, 255))

    # Swirling vortex streaks
    for angle_deg in range(0, 360, 45):
        rad = math.radians(angle_deg)
        r0 = 5
        r1 = 11
        x0 = int(32 + math.cos(rad) * r0 * 1.4)
        y0 = int(32 + math.sin(rad) * r0 * 0.7)
        x1 = int(32 + math.cos(rad + 0.6) * r1 * 1.4)
        y1 = int(32 + math.sin(rad + 0.6) * r1 * 0.7)
        draw.line([(x0, y0), (x1, y1)], fill=(210, 255, 210, 255))

    # 4 Floating obsidian obelisks/focus pillars
    pillars = [(16, 24), (48, 24), (16, 40), (48, 40)]
    for px_c, py_c in pillars:
        # Obelisk pillar
        draw.polygon([(px_c, py_c - 10), (px_c - 3, py_c + 2), (px_c + 3, py_c + 2)],
                     fill=(65, 58, 80, 255), outline=(20, 16, 26, 255))
        # Highlight facet
        draw.polygon([(px_c, py_c - 10), (px_c - 3, py_c + 2), (px_c, py_c + 3)],
                     fill=(105, 98, 125, 255))
        # Glowing necrotic rune on face
        px[px_c, py_c - 3] = (60, 255, 130, 255)
        px[px_c, py_c - 4] = (60, 255, 130, 255)
        # Binding chain to central rim
        draw.line([(px_c, py_c + 2), (32 + (px_c - 32) // 2, 32 + (py_c - 32) // 2)],
                  fill=(75, 70, 85, 255), width=1)

    # Floating central soul crystal
    stamp_crystal(im, 32, 14, 4, 6)

    return im


def build_construction_sheet(final_im, ref_constr_path, w, h):
    """Generate 64x192 3-frame construction strip based on genuine WC1 construction."""
    base_c = Image.open(ref_constr_path)
    if base_c.size != (w, h * 3):
        base_c = base_c.resize((w, h * 3), Image.Resampling.NEAREST)
    sheet = recolor_to_obsidian(base_c.convert("RGBA"), base_c)

    # Frame 0 (0..h): Site foundation + green runic marker
    # Frame 1 (h..2h): Scaffolding + half-built structure
    # Frame 2 (2h..3h): Almost complete structure with Scourge crystal
    f2 = final_im.copy()
    # Mask out bottom part for frame 1
    f1 = final_im.copy()
    px1 = f1.load()
    for y in range(h):
        for x in range(w):
            if y < h // 3:
                px1[x, y] = (0, 0, 0, 0)
            elif y < h // 2 and (x + y) % 3 != 0:
                px1[x, y] = (30, 25, 40, 200)

    # Paste frame 2 at bottom
    sheet.paste(f2, (0, h * 2), f2)
    # Paste partial frame 1 in middle
    sheet.paste(f1, (0, h), f1)
    stamp_crystal(sheet, w // 2, h + 14, 4, 5)

    return sheet


def build_crypt_fiend_spritesheet():
    """
    Generate authentic WC3 Crypt Fiend sprite sheet:
    - 160x320 (32x32 frames, 5 columns x 10 rows).
    - Nerubian spider-warrior: 6 articulated spidery legs, black arachnid abdomen
      with pale chevron markings and glowing venom nodes, upright armored nerubian
      carapace, double scythe foreclaws, cluster of glowing green eyes and pincers.
    - Rows:
      0..4: Walk/Move in 5 directions (S, SW, W, NW, N)
      5..7: Stand / Idle
      8..8: Attack (rears up, mandibles widen, spits web projectile)
      9..9: Death (collapsing carapace, folded curled spider legs, venom pool)
    """
    im = Image.new("RGBA", (160, 320), (0, 0, 0, 0))
    px = im.load()

    # Colors
    chitin_black = (22, 18, 28, 255)
    chitin_dark = (38, 32, 48, 255)
    chitin_mid = (65, 56, 82, 255)
    chitin_high = (115, 105, 140, 255)
    pale_chevron = (165, 175, 190, 255)
    scythe_edge = (210, 220, 235, 255)
    eye_green = (40, 255, 120, 255)
    venom_green = (30, 200, 80, 255)
    gore_dark = (45, 18, 55, 255)
    gore_green = (65, 180, 60, 255)

    # Directions: 0=S, 1=SW, 2=W, 3=NW, 4=N
    # 5 directions map across columns or rows depending on Stratagus anim standard.
    # Stratagus frameNumbers_5_5_2_3 uses 10 rows of 5 frames:
    # 5 frames across per row = 5 animation steps!
    # Rows:
    # Row 0: Walk S
    # Row 1: Walk SW
    # Row 2: Death S (death animation rows)
    # Row 3: Walk W
    # Row 4: Walk NW
    # Row 5: Death SW
    # Row 6: Walk N
    # Row 7: Death W
    # Row 8: Stand/Attack
    # Row 9: Stand/Attack

    # Let's inspect archer.png to use the exact frame placement of WC1 archers!
    ref_archer = Image.open(os.path.join(GRAPHICS_DIR, "human", "units", "archer.png"))
    ref_px = ref_archer.load()

    for row in range(10):
        for col in range(5):
            ox = col * 32
            oy = row * 32

            # Find center of gravity of base unit in this frame
            pts = []
            for y in range(32):
                for x in range(32):
                    p = ref_px[ox + x, oy + y]
                    if p != 255 and p != 0:
                        pts.append((x, y))

            if not pts:
                continue

            cx = sum(p[0] for p in pts) // len(pts)
            cy = sum(p[1] for p in pts) // len(pts)

            is_death = (row in (2, 5, 7))
            is_attack = (row in (8, 9) and col >= 2)

            if is_death:
                # Collapsed arachnid death: curled inward spider legs around crushed abdomen
                step = col
                drop = min(6, step * 2)
                # Splattered venom/ichor
                for dy in range(-3, 4):
                    for dx in range(-6, 7):
                        if dx*dx + dy*dy * 2 <= 20:
                            px[ox + cx + dx, oy + cy + drop + dy] = gore_green if (dx + dy) % 2 == 0 else gore_dark
                # Crushed carapace
                for dy in range(-2, 3):
                    for dx in range(-4, 5):
                        px[ox + cx + dx, oy + cy + drop + dy] = chitin_dark
                # Curled legs pointing inward
                for angle in (0, 45, 90, 135, 180, 225, 270, 315):
                    rad = math.radians(angle)
                    lx = int(cx + math.cos(rad) * (7 - step))
                    ly = int(cy + drop + math.sin(rad) * (5 - step // 2))
                    px[ox + lx, oy + ly] = chitin_high
                continue

            # Active Crypt Fiend:
            # 1. Rear Abdomen (spider bulb)
            # Offset abdomen depending on direction
            ab_ox = cx
            ab_oy = cy + 3
            if row in (0, 1, 3):  # Facing south/southwest/west -> abdomen is behind/above
                ab_oy = cy - 2
            elif row in (4, 6):  # Facing northwest/north -> abdomen is in front/below
                ab_oy = cy + 3

            # Draw rounded abdomen
            for dy in range(-5, 6):
                for dx in range(-6, 7):
                    if (dx * dx) / 36.0 + (dy * dy) / 25.0 <= 1.0:
                        xx = ox + ab_ox + dx
                        yy = oy + ab_oy + dy
                        if dx + dy < -2:
                            px[xx, yy] = chitin_high
                        elif dx + dy <= 1:
                            px[xx, yy] = chitin_mid
                        else:
                            px[xx, yy] = chitin_black
                        # Pale chevron stripes on abdomen
                        if abs(dx) == abs(dy) and abs(dx) in (2, 4):
                            px[xx, yy] = pale_chevron
                        # Glowing venom gland in center
                        if abs(dx) <= 1 and abs(dy) <= 1:
                            px[xx, yy] = venom_green

            # 2. Six Articulated Spidery Legs (scuttling)
            leg_offsets = [
                (-7, -4, -12, 2), (-8, 1, -13, 7), (-6, 5, -10, 11),
                (7, -4, 12, 2), (8, 1, 13, 7), (6, 5, 10, 11)
            ]
            leg_cycle = (col % 4)
            for idx, (lx0, ly0, lx1, ly1) in enumerate(leg_offsets):
                # Animate leg tips based on cycle
                shift = (leg_cycle if idx % 2 == 0 else (4 - leg_cycle)) - 2
                tip_x = cx + lx1 + (shift if idx < 3 else -shift)
                tip_y = cy + ly1 + (abs(shift) // 2)
                knee_x = cx + (lx0 + lx1) // 2 + (shift // 2)
                knee_y = cy + ly0 - 3  # High arched knee

                # Draw femur (body to knee)
                steps1 = max(abs(knee_x - (cx + lx0)), abs(knee_y - (cy + ly0)), 1)
                for s in range(steps1 + 1):
                    px[ox + int(cx + lx0 + (knee_x - (cx + lx0)) * s / steps1),
                       oy + int(cy + ly0 + (knee_y - (cy + ly0)) * s / steps1)] = chitin_mid
                # Draw tibia (knee to ground)
                steps2 = max(abs(tip_x - knee_x), abs(tip_y - knee_y), 1)
                for s in range(steps2 + 1):
                    col_leg = chitin_high if s < steps2 // 2 else chitin_black
                    px[ox + int(knee_x + (tip_x - knee_x) * s / steps2),
                       oy + int(knee_y + (tip_y - knee_y) * s / steps2)] = col_leg

            # 3. Upright Nerubian Carapace / Torso
            torso_ox = cx
            torso_oy = cy - 2
            for dy in range(-5, 3):
                for dx in range(-4, 5):
                    if abs(dx) + abs(dy) <= 6:
                        xx = ox + torso_ox + dx
                        yy = oy + torso_oy + dy
                        if dx < 0 and dy < 0:
                            px[xx, yy] = chitin_high
                        elif dx <= 0:
                            px[xx, yy] = chitin_mid
                        else:
                            px[xx, yy] = chitin_dark

            # Spiked Pauldrons / Shoulders
            px[ox + torso_ox - 4, oy + torso_oy - 3] = chitin_high
            px[ox + torso_ox - 5, oy + torso_oy - 4] = scythe_edge
            px[ox + torso_ox + 4, oy + torso_oy - 3] = chitin_mid
            px[ox + torso_ox + 5, oy + torso_oy - 4] = scythe_edge

            # 4. Mantis Scythe Forelimbs
            if is_attack:
                # Reared up scythes ready to strike / web shot
                px[ox + torso_ox - 5, oy + torso_oy - 7] = scythe_edge
                px[ox + torso_ox - 4, oy + torso_oy - 6] = chitin_high
                px[ox + torso_ox + 5, oy + torso_oy - 7] = scythe_edge
                px[ox + torso_ox + 4, oy + torso_oy - 6] = chitin_high
                # Web discharge from mouth
                for wx in range(-2, 3):
                    px[ox + torso_ox + wx, oy + torso_oy - 2] = (225, 255, 230, 255)
            else:
                # Folded forward scythes
                px[ox + torso_ox - 3, oy + torso_oy + 1] = chitin_high
                px[ox + torso_ox - 4, oy + torso_oy + 3] = scythe_edge
                px[ox + torso_ox + 3, oy + torso_oy + 1] = chitin_mid
                px[ox + torso_ox + 4, oy + torso_oy + 3] = scythe_edge

            # 5. Nerubian Head, Mandibles & Glowing Eyes
            head_y = torso_oy - 5
            draw_im = ImageDraw.Draw(im)
            draw_im.rectangle([ox + torso_ox - 2, oy + head_y - 2, ox + torso_ox + 2, oy + head_y + 1],
                              fill=chitin_dark)
            # Mandibles
            px[ox + torso_ox - 2, oy + head_y + 2] = scythe_edge
            px[ox + torso_ox + 2, oy + head_y + 2] = scythe_edge
            # 4 Glowing green cluster eyes
            px[ox + torso_ox - 1, oy + head_y - 1] = eye_green
            px[ox + torso_ox + 1, oy + head_y - 1] = eye_green
            px[ox + torso_ox, oy + head_y] = eye_green
            px[ox + torso_ox, oy + head_y - 2] = eye_green

    return im


def build_abomination_spritesheet():
    """
    Generate authentic WC3 Abomination sprite sheet:
    - 240x720 (48x48 frames, 5 columns x 15 rows).
    - Massive lumbering stitched meat golem:
      - Bloated sickly corpse flesh (pale greenish-grey).
      - Thick black surgical sutures & metal staples across belly & limbs.
      - Giant butcher cleaver in right hand, iron meat hook with chain in left.
      - Stitched swollen belly with crude staples.
      - Brutal stitched bald head with jagged yellow fangs and dead eyes.
      - Vestigial third skeletal arm protruding from back shoulder.
    """
    im = Image.new("RGBA", (240, 720), (0, 0, 0, 0))
    px = im.load()
    draw = ImageDraw.Draw(im)

    # Colors
    flesh_shadow = (45, 55, 48, 255)
    flesh_dark = (75, 88, 72, 255)
    flesh_mid = (118, 132, 108, 255)
    flesh_high = (165, 180, 150, 255)
    suture_black = (20, 16, 22, 255)
    gore_dark = (95, 20, 28, 255)
    gore_bright = (155, 30, 40, 255)
    cleaver_metal = (185, 190, 200, 255)
    cleaver_dark = (75, 80, 90, 255)
    cleaver_blood = (160, 25, 35, 255)
    hook_rust = (135, 80, 60, 255)
    eye_dead = (220, 235, 140, 255)
    bone_white = (215, 210, 190, 255)

    ref_raider = Image.open(os.path.join(GRAPHICS_DIR, "orc", "units", "raider.png"))
    ref_px = ref_raider.load()

    for row in range(15):
        for col in range(5):
            ox = col * 48
            oy = row * 48

            # Reference bounds
            pts = []
            for y in range(48):
                for x in range(48):
                    p = ref_px[ox + x, oy + y]
                    if p != 255 and p != 0:
                        pts.append((x, y))

            if not pts:
                continue

            cx = sum(p[0] for p in pts) // len(pts)
            cy = sum(p[1] for p in pts) // len(pts)

            is_death = (row in (2, 5, 7, 12, 14))
            is_attack = (row in (8, 9, 10) and col >= 2)

            if is_death:
                # Collapsing grotesque pile of stitched meat & organs
                step = col
                drop = min(8, step * 2)
                # Huge pool of dark blood & gore
                for dy in range(-6, 7):
                    for dx in range(-12, 13):
                        if (dx * dx) / 144.0 + (dy * dy) / 49.0 <= 1.0:
                            px[ox + cx + dx, oy + cy + drop + dy] = gore_bright if (dx + dy) % 3 == 0 else gore_dark
                # Dislodged butcher cleaver lying in blood
                draw.rectangle([ox + cx - 10, oy + cy + drop + 2, ox + cx - 2, oy + cy + drop + 6],
                               fill=cleaver_metal, outline=cleaver_dark)
                # Stitched meat chunks
                for dy in range(-4, 5):
                    for dx in range(-8, 9):
                        if abs(dx) + abs(dy) <= 8:
                            px[ox + cx + dx, oy + cy + drop + dy] = flesh_mid
                # Exposed sutures & bone spikes
                for sx in range(-6, 7, 3):
                    px[ox + cx + sx, oy + cy + drop] = suture_black
                    px[ox + cx + sx, oy + cy + drop - 1] = bone_white
                continue

            # Active Abomination:
            # 1. Stomping Thick Legs
            walk_cycle = (col % 4)
            leg_l_off = (walk_cycle - 2) if row < 5 else 0
            leg_r_off = (2 - walk_cycle) if row < 5 else 0

            # Left leg
            for dy in range(8):
                for dx in range(-4, 5):
                    px[ox + cx - 6 + dx, oy + cy + 8 + dy + leg_l_off] = flesh_dark if dx > 0 else flesh_mid
            # Right leg
            for dy in range(8):
                for dx in range(-4, 5):
                    px[ox + cx + 6 + dx, oy + cy + 8 + dy + leg_r_off] = flesh_shadow if dx > 0 else flesh_dark

            # Crude leather loincloth / apron straps
            draw.rectangle([ox + cx - 7, oy + cy + 7, ox + cx + 7, oy + cy + 11], fill=(45, 30, 25, 255))

            # 2. Massive Bloated Torso & Stitched Belly
            torso_w = 12
            torso_h = 13
            for dy in range(-torso_h, torso_h + 1):
                # Belly bulges wider at bottom
                span = int(torso_w * (1.1 if dy > 0 else 0.9) * math.sqrt(max(0.0, 1.0 - (dy / float(torso_h + 1))**2)))
                for dx in range(-span, span + 1):
                    xx = ox + cx + dx
                    yy = oy + cy + dy
                    lum_bias = dx - dy
                    if lum_bias < -3:
                        px[xx, yy] = flesh_high
                    elif lum_bias <= 2:
                        px[xx, yy] = flesh_mid
                    elif lum_bias <= 6:
                        px[xx, yy] = flesh_dark
                    else:
                        px[xx, yy] = flesh_shadow

            # Prominent Cross-Sutures across the bloated belly
            # Vertical central incision with cross stitches
            for sy in range(cy - 6, cy + 6):
                px[ox + cx, oy + sy] = gore_dark
                if sy % 2 == 0:
                    px[ox + cx - 1, oy + sy] = suture_black
                    px[ox + cx + 1, oy + sy] = suture_black
                    px[ox + cx - 2, oy + sy] = suture_black
                    px[ox + cx + 2, oy + sy] = suture_black
            # Diagonal wound suture across chest
            for d in range(-4, 5):
                px[ox + cx - 5 + d, oy + cy - 6 + d] = suture_black

            # 3. Third Vestigial Arm (skeletal/mutated claw emerging from left shoulder)
            draw.line([(ox + cx - 9, oy + cy - 10), (ox + cx - 14, oy + cy - 14)], fill=flesh_dark, width=2)
            draw.line([(ox + cx - 14, oy + cy - 14), (ox + cx - 18, oy + cy - 12)], fill=bone_white, width=1)
            px[ox + cx - 19, oy + cy - 11] = suture_black  # Claw tip

            # 4. Arms & Weapons
            # Right Arm -> Giant Butcher Cleaver
            cleaver_y_swing = -10 if is_attack else 2
            cleaver_x_swing = -4 if is_attack else 0
            # Arm
            draw.line([(ox + cx + 10, oy + cy - 6), (ox + cx + 16 + cleaver_x_swing, oy + cy + cleaver_y_swing)],
                      fill=flesh_mid, width=4)
            # Cleaver blade
            blade_x = ox + cx + 17 + cleaver_x_swing
            blade_y = oy + cy + cleaver_y_swing - 4
            draw.rectangle([blade_x, blade_y - 8, blade_x + 8, blade_y + 8],
                           fill=cleaver_metal, outline=cleaver_dark)
            # Blood stained blade edge
            draw.line([(blade_x + 8, blade_y - 8), (blade_x + 8, blade_y + 8)], fill=cleaver_blood, width=2)
            # Cleaver wooden handle
            draw.line([(blade_x - 3, blade_y), (blade_x, blade_y)], fill=(65, 40, 25, 255), width=2)

            # Left Arm -> Meat Hook with Chain
            draw.line([(ox + cx - 10, oy + cy - 6), (ox + cx - 16, oy + cy + 3)], fill=flesh_mid, width=3)
            # Hook sickle curve
            hook_x = ox + cx - 18
            hook_y = oy + cy + 4
            draw.arc([hook_x - 3, hook_y, hook_x + 3, hook_y + 7], start=0, end=180, fill=hook_rust, width=2)
            # Chain links
            px[hook_x, hook_y - 1] = (100, 95, 110, 255)
            px[hook_x + 1, hook_y - 2] = (100, 95, 110, 255)

            # 5. Grotesque Stitched Head
            head_x = ox + cx
            head_y = oy + cy - 15
            # Lumpy asymmetrical bald skull
            draw.ellipse([head_x - 5, head_y - 6, head_x + 5, head_y + 3], fill=flesh_mid, outline=flesh_shadow)
            # Stitched seam across brow
            for bx in range(-4, 5):
                if bx % 2 == 0:
                    px[head_x + bx, head_y - 2] = suture_black
            # Vacant sickly dead eye
            px[head_x - 2, head_y - 1] = eye_dead
            px[head_x + 2, head_y - 1] = (30, 25, 20, 255)  # Missing / sewn shut eye socket
            # Crooked jaw with jagged teeth
            draw.rectangle([head_x - 3, head_y + 1, head_x + 3, head_y + 3], fill=(35, 15, 20, 255))
            px[head_x - 2, head_y + 1] = bone_white
            px[head_x, head_y + 1] = bone_white
            px[head_x + 2, head_y + 1] = bone_white

    return im


def build_icon(kind, ref_pal):
    """Generate authentic WC1 27x19 icon for the unit/building."""
    im = Image.new("RGBA", (27, 19), (28, 22, 34, 255))
    draw = ImageDraw.Draw(im)
    px = im.load()

    # Outer border (WC1 stone bezel)
    draw.rectangle([0, 0, 26, 18], outline=(15, 12, 18, 255))
    draw.line([(1, 1), (25, 1)], fill=(85, 80, 95, 255))
    draw.line([(1, 1), (1, 17)], fill=(85, 80, 95, 255))

    if kind == "crypt_fiend":
        # Nerubian Crypt Fiend head & scythes
        # Background dark spiderweb
        draw.line([(4, 4), (22, 14)], fill=(45, 40, 55, 255))
        draw.line([(22, 4), (4, 14)], fill=(45, 40, 55, 255))
        # Nerubian horned helmet / carapace head
        draw.polygon([(13, 3), (8, 9), (13, 14), (18, 9)], fill=(45, 38, 55, 255), outline=(20, 16, 26, 255))
        # Scythe claws flanking
        draw.line([(6, 15), (5, 8)], fill=(185, 195, 210, 255), width=2)
        draw.line([(20, 15), (21, 8)], fill=(185, 195, 210, 255), width=2)
        # 4 Glowing green eyes
        px[11, 8] = (40, 255, 120, 255)
        px[15, 8] = (40, 255, 120, 255)
        px[13, 9] = (40, 255, 120, 255)
        px[13, 7] = (40, 255, 120, 255)
        # Mandibles
        px[11, 12] = (210, 220, 235, 255)
        px[15, 12] = (210, 220, 235, 255)

    elif kind == "abomination":
        # Grotesque stitched Abomination face
        draw.ellipse([7, 3, 19, 15], fill=(118, 132, 108, 255), outline=(45, 55, 48, 255))
        # Sutures across face
        for sx in range(8, 18, 2):
            px[sx, 8] = (20, 16, 22, 255)
            px[sx, 9] = (20, 16, 22, 255)
        # Dead yellowish eye & scarred eye
        px[10, 6] = (220, 235, 140, 255)
        px[16, 6] = (35, 20, 25, 255)
        # Gaping crooked jaw with jagged fangs
        draw.rectangle([10, 11, 16, 13], fill=(45, 18, 22, 255))
        px[11, 11] = (220, 215, 190, 255)
        px[13, 11] = (220, 215, 190, 255)
        px[15, 11] = (220, 215, 190, 255)
        # Butcher cleaver blade in corner
        draw.rectangle([2, 5, 6, 13], fill=(185, 190, 200, 255), outline=(75, 80, 90, 255))
        px[6, 7] = (160, 25, 35, 255)  # Blood on blade

    elif kind == "barracks":
        # Crypt icon
        draw.polygon([(13, 3), (5, 15), (21, 15)], fill=(55, 50, 70, 255), outline=(25, 20, 32, 255))
        # Arched glowing portal
        draw.rectangle([11, 10, 15, 15], fill=(30, 220, 100, 255))
        px[13, 11] = (200, 255, 220, 255)
        # Vaulted rib arches
        draw.arc([6, 5, 20, 15], start=180, end=0, fill=(160, 155, 180, 255))
        stamp_crystal(im, 13, 3, 2, 3)

    elif kind == "lumber_mill":
        # Graveyard icon
        draw.rectangle([8, 6, 18, 14], fill=(52, 48, 64, 255), outline=(24, 20, 30, 255))
        # Pitch roof
        draw.polygon([(7, 6), (13, 2), (19, 6)], fill=(75, 70, 90, 255))
        # Gravestones flanking
        draw.rectangle([4, 10, 6, 14], fill=(110, 105, 125, 255))
        draw.line([(22, 9), (22, 14)], fill=(120, 115, 135, 255))
        draw.line([(21, 11), (23, 11)], fill=(120, 115, 135, 255))
        # Green mist
        px[10, 12] = (50, 230, 120, 255)
        px[15, 12] = (50, 230, 120, 255)

    elif kind == "stable":
        # Sacrificial Pit icon
        draw.ellipse([5, 4, 21, 14], fill=(35, 28, 45, 255), outline=(65, 58, 80, 255))
        draw.ellipse([8, 6, 18, 12], fill=(45, 215, 100, 255))
        px[13, 9] = (210, 255, 210, 255)
        stamp_crystal(im, 13, 3, 2, 3)

    return rgba_to_indexed(im, ref_pal)


def main():
    print("Generating authentic WC3 Scourge buildings, units, and icons...")

    # Load reference palette
    ref_pal = Image.open(os.path.join(GRAPHICS_DIR, "tilesets", "forest", "orc", "buildings", "town_hall.png")).getpalette()

    # 1. Generate Buildings for forest and swamp
    for ts in ("forest", "swamp"):
        out_b_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "forsaken", "buildings")
        orc_b_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "orc", "buildings")
        os.makedirs(out_b_dir, exist_ok=True)

        ref_stone = Image.open(os.path.join(orc_b_dir, "temple.png"))

        # A. Crypt (barracks.png) -> 64x64 & 64x192
        crypt_rgba = build_wc3_crypt(ref_stone)
        crypt_idx = rgba_to_indexed(crypt_rgba, ref_pal)
        crypt_path = os.path.join(out_b_dir, "barracks.png")
        crypt_idx.save(crypt_path)

        c_crypt_rgba = build_construction_sheet(crypt_rgba, os.path.join(orc_b_dir, "barracks_construction.png"), 64, 64)
        c_crypt_idx = rgba_to_indexed(c_crypt_rgba, ref_pal)
        c_crypt_idx.save(os.path.join(out_b_dir, "barracks_construction.png"))
        print(f"[{ts}] Saved authentic Crypt: {crypt_path} (64x64, constr 64x192)")

        # B. Graveyard (lumber_mill.png) -> 64x64 & 64x192 (FIXES 64x48 CRASH!)
        gy_rgba = build_wc3_graveyard()
        gy_idx = rgba_to_indexed(gy_rgba, ref_pal)
        gy_path = os.path.join(out_b_dir, "lumber_mill.png")
        gy_idx.save(gy_path)

        c_gy_rgba = build_construction_sheet(gy_rgba, os.path.join(orc_b_dir, "lumber_mill_construction.png"), 64, 64)
        c_gy_idx = rgba_to_indexed(c_gy_rgba, ref_pal)
        c_gy_idx.save(os.path.join(out_b_dir, "lumber_mill_construction.png"))
        print(f"[{ts}] Saved authentic Graveyard: {gy_path} (64x64, constr 64x192) -> CRASH FIXED!")

        # C. Sacrificial Pit (stable.png) -> 64x64 & 64x192 (FIXES 64x48 CRASH!)
        pit_rgba = build_wc3_sacrificial_pit()
        pit_idx = rgba_to_indexed(pit_rgba, ref_pal)
        pit_path = os.path.join(out_b_dir, "stable.png")
        pit_idx.save(pit_path)

        c_pit_rgba = build_construction_sheet(pit_rgba, os.path.join(orc_b_dir, "kennel_construction.png"), 64, 64)
        c_pit_idx = rgba_to_indexed(c_pit_rgba, ref_pal)
        c_pit_idx.save(os.path.join(out_b_dir, "stable_construction.png"))
        print(f"[{ts}] Saved authentic Sacrificial Pit: {pit_path} (64x64, constr 64x192) -> CRASH FIXED!")

    # 2. Generate Units
    units_dir = os.path.join(GRAPHICS_DIR, "forsaken", "units")
    os.makedirs(units_dir, exist_ok=True)

    # Unit palette reference
    unit_pal = Image.open(os.path.join(GRAPHICS_DIR, "human", "units", "archer.png")).getpalette()

    # A. Crypt Fiend (160x320)
    cf_rgba = build_crypt_fiend_spritesheet()
    cf_idx = rgba_to_indexed(cf_rgba, unit_pal)
    cf_path = os.path.join(units_dir, "crypt_fiend.png")
    cf_idx.save(cf_path)
    print(f"Saved authentic Crypt Fiend sprite sheet: {cf_path} (160x320)")

    # B. Abomination (240x720)
    raider_pal = Image.open(os.path.join(GRAPHICS_DIR, "orc", "units", "raider.png")).getpalette()
    abom_rgba = build_abomination_spritesheet()
    abom_idx = rgba_to_indexed(abom_rgba, raider_pal)
    abom_path = os.path.join(units_dir, "abomination.png")
    abom_idx.save(abom_path)
    print(f"Saved authentic Abomination sprite sheet: {abom_path} (240x720)")

    # 3. Generate Icons (27x19)
    os.makedirs(UI_FORSAKEN_DIR, exist_ok=True)
    icon_map = {
        "icon-crypt-fiend.png": "crypt_fiend",
        "icon-abomination.png": "abomination",
        "icon-forsaken-barracks.png": "barracks",
        "icon-forsaken-lumber-mill.png": "lumber_mill",
        "icon-forsaken-stable.png": "stable",
    }
    for filename, kind in icon_map.items():
        icon_im = build_icon(kind, unit_pal)
        icon_path = os.path.join(UI_FORSAKEN_DIR, filename)
        icon_im.save(icon_path)
        print(f"Saved icon {icon_path} (27x19)")

    print("All Scourge buildings and units generated successfully!")


if __name__ == "__main__":
    main()
