#!/usr/bin/env python3
"""
Build authentic Warcraft III Scourge / Undead unit sprites, buildings, and icons
in Warcraft I's 8-bit paletted pixel-art style:
1. Ghoul (ghoul.png, 160x480): True WC3 Ghoul silhouette — crouched feral posture,
   gaunt pale-green necrotic limbs, hunched arched back with 3 white dorsal spine spikes,
   exposed bloody ribcage, low forward-jutting skull head with fangs & red eyes, and
   huge 3-pronged slashing bone claws.
2. Meat Wagon (meat_wagon.png, 160x320): Bone rib-cage rails, front spiked iron roller,
   pile of bloody corpses/skulls & glowing green plague slime.
3. Banshee (banshee.png, 160x416): Floating spectral female wraith with tapering ghostly
   tail (no walking legs), streaming white-violet hair, wailing face, and spectral hand orbs.
4. Necromancer (necromancer.png, 160x384): Dark cultist robes, white skull mask/cowl,
   long white beard, and skull-topped staff with glowing fel-green orb.
5. Death Knight (death_knight.png, 160x480): Skeletal warhorse with exposed white ribs &
   glowing cyan eyes, horned helm, and glowing cyan Runeblade (Frostmourne).
6. Dark Ranger & Sylvanas (dark_ranger.png, sylvanas.png, 160x320): Pointed dark hood,
   flowing cloak, pale undead skin, glowing red eyes, and curved bone longbow.
7. WC3 Scourge Buildings (Necropolis, Ziggurat, Crypt, Graveyard, Slaughterhouse,
   Sacrificial Pit, Temple of the Damned, Spirit Tower, Black Citadel).
8. WC1-shaded 27x19 Icons.
"""

import os
from PIL import Image

BASE_DIR = "/home/smiles/forsaken-mod"
GRAPHICS_DIR = os.path.join(BASE_DIR, "graphics")
CONTRIB_DIR = os.path.join(BASE_DIR, "contrib", "graphics")


def get_palette_matcher(pal):
    cache = {}

    def find_idx(rgb, allow_pc=False):
        key = (int(rgb[0]), int(rgb[1]), int(rgb[2]), allow_pc)
        if key in cache:
            return cache[key]
        best_d = 10**9
        best_i = 0
        for i in range(255):
            if not allow_pc and (200 <= i <= 207):
                continue
            pr, pg, pb = pal[i * 3], pal[i * 3 + 1], pal[i * 3 + 2]
            d = (pr - key[0]) ** 2 + (pg - key[1]) ** 2 + (pb - key[2]) ** 2
            if d < best_d:
                best_d = d
                best_i = i
        # 176..183 is the original WC1 orc player-color ramp. War1gus only
        # recolors 200..207 (DefinePlayerColorIndex(200, 8)), so pixels left
        # in 176..183 render as fixed red. Vanilla data remaps them to the
        # team ramp; do the same here.
        if 176 <= best_i <= 183:
            best_i += 24
        cache[key] = best_i
        return best_i

    return find_idx


def rgba_to_indexed(rgba_im, ref_pal, orig_indexed_im=None):
    w, h = rgba_im.size
    out = Image.new("P", (w, h), 255)
    out.putpalette(ref_pal)
    src_px = rgba_im.load()
    out_px = out.load()
    orig_px = orig_indexed_im.load() if orig_indexed_im is not None else None
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
                out_px[x, y] = find_idx((r, g, b))

    out.info["transparency"] = 255
    return out


# ==============================================================================
# 1. TRUE WC3 GHOUL SPRITE SHEET (160x480, 5 cols x 15 rows for frameNumbers_5_5_5_5)
#    Crouched feral cannibal undead with hunched spine spikes, exposed bloody ribs,
#    gaunt pale-green limbs, low grinning fang skull, and huge 3-pronged bone claws!
# ==============================================================================
def draw_ghoul_frame(px, ox, oy, col, anim_type, step):
    """
    Draw a single 32x32 WC3 Ghoul frame at (ox, oy).
    col: 0=N, 1=NE, 2=E, 3=SE, 4=S
    anim_type: 'still', 'move', 'attack', 'death'
    step: 0..4
    """
    # Shaded necrotic Ghoul palette
    skin_shadow = (34, 44, 36, 255)
    skin_dark = (54, 70, 56, 255)
    skin_mid = (82, 106, 80, 255)
    skin_high = (114, 142, 108, 255)
    bone_white = (232, 228, 212, 255)
    bone_mid = (178, 172, 154, 255)
    bone_dark = (124, 118, 104, 255)
    gore_dark = (105, 18, 24, 255)
    gore_bright = (168, 28, 34, 255)
    eye_red = (255, 48, 36, 255)
    eye_glow = (255, 215, 70, 255)
    pc_mid = (254, 0, 205, 255)
    pc_dark = (254, 0, 207, 255)

    def put(x, y, col_rgba):
        if 0 <= x < 32 and 0 <= y < 32:
            px[ox + x, oy + y] = col_rgba

    def disk(cx, cy, rx, ry, c_high, c_mid, c_dark):
        for dy in range(-ry, ry + 1):
            for dx in range(-rx, rx + 1):
                if (dx * dx) / max(1.0, rx * rx + 0.5) + (dy * dy) / max(1.0, ry * ry + 0.5) <= 1.0:
                    if dx + dy < -1:
                        put(cx + dx, cy + dy, c_high)
                    elif dx + dy <= 1:
                        put(cx + dx, cy + dy, c_mid)
                    else:
                        put(cx + dx, cy + dy, c_dark)

    def limb(x0, y0, x1, y1, thick=1):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            lx = int(round(x0 + (x1 - x0) * i / float(steps)))
            ly = int(round(y0 + (y1 - y0) * i / float(steps)))
            put(lx, ly, skin_mid)
            if thick >= 2:
                put(lx - 1, ly, skin_high)
                put(lx, ly + 1, skin_dark)
            else:
                put(lx, ly + 1, skin_shadow)

    # Death animation (collapsing into a bloody skeleton/ribcage corpse)
    if anim_type == "death":
        drop = min(4, step + 1)
        cy = 17 + drop
        # Pool of dark blood & collapsed torso
        disk(16, cy, 5 + step // 2, 3, gore_bright, gore_dark, skin_shadow)
        # Splayed limbs
        limb(11, cy, 7 - step // 2, cy + 2, 1)
        limb(21, cy, 25 + step // 2, cy + 1, 1)
        # Exposed white ribcage arches & spine spikes sticking out of corpse
        for rx_p in range(12, 20, 2):
            put(rx_p, cy - 1, bone_white)
            put(rx_p, cy, bone_mid)
            put(rx_p + 1, cy, gore_bright)
        # Dropped skull & claws
        disk(21 + step // 2, cy, 2, 2, bone_white, bone_mid, skin_dark)
        put(22 + step // 2, cy, eye_red if step < 3 else skin_shadow)
        for c_off in (-1, 1):
            put(6 - step // 2, cy + 1 + c_off, bone_white)
            put(26 + step // 2, cy + c_off, bone_white)
        return

    # Walking / Stalking stride & Attack lunge offsets
    stride = 0
    bob = 0
    lunge_x, lunge_y = 0, 0
    if anim_type == "move":
        stride = (-3, -1, 2, 3)[step % 4]
        bob = (0, -1, 0, 1)[step % 4]
    elif anim_type == "attack":
        lunge_mag = (0, 2, 4, 2, -1)[step % 5]
        bob = (-1, 0, 1, 0, 0)[step % 5]
        if col in (1, 2, 3):
            lunge_x = lunge_mag
        if col in (0, 1):
            lunge_y = -lunge_mag // 2
        elif col in (3, 4):
            lunge_y = lunge_mag // 2

    # Base anchor for the Ghoul's hunched torso
    cx = 15 + lunge_x
    cy = 15 + bob + lunge_y

    # Direction vectors for head vs pelvis (Ghoul is deeply hunched forward!)
    if col == 0:  # North (facing away/up)
        hx, hy = cx, cy - 4
        bx, by = cx, cy - 1
        px_c, py_c = cx, cy + 4
    elif col == 1:  # NE
        hx, hy = cx + 4, cy - 3
        bx, by = cx, cy - 2
        px_c, py_c = cx - 3, cy + 3
    elif col == 2:  # East (side profile: unmistakable hunched Ghoul silhouette!)
        hx, hy = cx + 5, cy - 1
        bx, by = cx, cy - 3
        px_c, py_c = cx - 4, cy + 3
    elif col == 3:  # SE
        hx, hy = cx + 4, cy + 2
        bx, by = cx, cy - 2
        px_c, py_c = cx - 3, cy + 2
    else:  # South (facing camera, hunched low with head slung between shoulders)
        hx, hy = cx, cy + 2
        bx, by = cx, cy - 3
        px_c, py_c = cx, cy + 3

    # 1. Digitigrade crouched hind legs (gaunt, bent knees, clawed feet)
    l_leg_shift = stride
    r_leg_shift = -stride
    # Left leg (knee bends outward/back, then down to foot)
    limb(px_c - 2, py_c, px_c - 4, py_c + 4 + l_leg_shift // 2, 1)
    limb(px_c - 4, py_c + 4 + l_leg_shift // 2, px_c - 3 + l_leg_shift, py_c + 8, 1)
    put(px_c - 4 + l_leg_shift, py_c + 8, bone_mid)
    # Right leg
    limb(px_c + 2, py_c, px_c + 4, py_c + 4 + r_leg_shift // 2, 1)
    limb(px_c + 4, py_c + 4 + r_leg_shift // 2, px_c + 3 + r_leg_shift, py_c + 8, 1)
    put(px_c + 4 + r_leg_shift, py_c + 8, bone_mid)

    # 2. Narrow waist & tattered player-color loincloth
    disk(px_c, py_c, 2, 2, skin_mid, skin_dark, skin_shadow)
    for lx in range(px_c - 2, px_c + 3):
        put(lx, py_c + 1, pc_mid)
        if (lx + col) % 2 == 0:
            put(lx, py_c + 2, pc_dark)

    # 3. Hunched upper ribcage / arched back
    disk(bx, by, 4, 3, skin_high, skin_mid, skin_dark)
    # Carve exposed bloody ribs across torso/flank
    for r_i in (-2, 0, 2):
        rx_p = bx + r_i
        ry_p = by + 1
        put(rx_p, ry_p, bone_white)
        put(rx_p, ry_p + 1, gore_bright)
        put(rx_p + 1, ry_p, gore_dark)

    # 4. Prominent jagged white dorsal spine spikes along the hunched back!
    spine_pts = [
        (bx - (2 if col in (1, 2, 3) else 0), by - 2, 3),
        (bx, by - 3, 4),
        (bx + (2 if col in (1, 2, 3) else 0), by - 2, 2),
        (px_c, py_c - 2, 2),
    ]
    for sx, sy, sh in spine_pts:
        for h_i in range(sh):
            put(sx - (h_i // 2 if col in (1, 2, 3) else 0), sy - h_i, bone_white if h_i == sh - 1 else bone_mid)
            put(sx + 1, sy - h_i + 1, bone_dark)

    # 5. Low forward-slung Ghoul skull head (with gaping bloody jaws, fangs & glowing red eyes)
    disk(hx, hy, 3, 3, skin_high, skin_mid, skin_dark)
    if col != 0:
        # Gaping bloody jaw & white fangs
        for jx in range(hx - 1, hx + 3):
            put(jx, hy + 2, gore_bright)
            if jx % 2 == 0:
                put(jx, hy + 1, bone_white)
                put(jx, hy + 3, bone_white)
        # Glowing red/yellow feral eyes
        if col == 4:  # South: two eyes
            put(hx - 1, hy, eye_red)
            put(hx + 1, hy, eye_red)
            put(hx - 1, hy - 1, bone_mid)
            put(hx + 1, hy - 1, bone_mid)
        else:  # Profile/diagonal: glowing eye + brow ridge
            put(hx + 1, hy - 1, eye_glow)
            put(hx + 2, hy - 1, eye_red)
            put(hx + 1, hy - 2, bone_white)

    # 6. Long sinewy arms & huge 3-pronged curved bone claws!
    # Swing arms with stride or slash wildly during attack!
    slash_swing = 0
    if anim_type == "attack":
        slash_swing = (-4, -2, 3, 5, 1)[step % 5]
    else:
        slash_swing = stride

    # Back/left arm + 3-pronged claw
    la_x = hx - (3 if col in (0, 4) else 1) + slash_swing // 2
    la_y = hy + 4 - slash_swing // 2
    limb(bx - 2, by + 1, la_x, la_y, 2)

    # Front/right arm + 3-pronged claw
    ra_x = hx + (3 if col in (0, 4) else 4) + (2 if anim_type == "attack" else 0)
    ra_y = hy + 3 + slash_swing
    limb(bx + 2, by + 1, ra_x, ra_y, 2)

    # Draw 3-bladed Wolverine/Ghoul claws on both hands
    claw_dir_x = 1 if col in (1, 2, 3) else 0
    claw_dir_y = -1 if col == 0 else (1 if col in (3, 4) else 0)
    if claw_dir_x == 0 and claw_dir_y == 0:
        claw_dir_y = 1

    for hand_idx, (hand_x, hand_y) in enumerate([(la_x, la_y), (ra_x, ra_y)]):
        c_dx = claw_dir_x if claw_dir_x != 0 else (-1 if hand_idx == 0 else 1)
        for blade in (-2, 0, 2):
            for cl in range(1, 6):
                bx_p = hand_x + c_dx * cl + (blade // 2 if claw_dir_x == 0 else 0)
                by_p = hand_y + claw_dir_y * cl + (blade if claw_dir_x != 0 else 0) + (cl // 3)
                if cl == 5:
                    put(bx_p, by_p, gore_bright if anim_type == "attack" else bone_white)
                elif cl >= 2:
                    put(bx_p, by_p, bone_white)
                else:
                    put(bx_p, by_p, bone_mid)

    # During peak attack frames (step 2, 3), draw bright razor slash arcs in front of the claws!
    if anim_type == "attack" and step in (2, 3):
        for s_i in range(-4, 5):
            sx_p = ra_x + c_dx * 4 - abs(s_i) // 2
            sy_p = ra_y + s_i
            put(sx_p, sy_p, bone_white)
            put(sx_p - c_dx, sy_p, gore_bright if s_i % 2 == 0 else bone_mid)


def build_ghoul_sprites():
    ref_im = Image.open(os.path.join(GRAPHICS_DIR, "orc", "units", "grunt.png"))
    pal = ref_im.getpalette()
    dst_path = os.path.join(GRAPHICS_DIR, "forsaken", "units", "ghoul.png")

    # 160x480 (5 cols x 15 rows) for frameNumbers_5_5_5_5:
    # Row 0: Still
    # Rows 3, 6, 9, 12: Move 0..3
    # Rows 1, 4, 7, 10, 13: Attack 0..4
    # Rows 2, 5, 8, 11, 14: Death 0..4
    w, h = 160, 480
    rgba = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = rgba.load()

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
            draw_ghoul_frame(px, c * 32, r * 32, c, atype, step)

    out = rgba_to_indexed(rgba, pal)
    out.save(dst_path)
    print(f"Generated true WC3 Ghoul sprite sheet (160x480): {dst_path}")


# ==============================================================================
# 2. SCULPT OTHER WC3 SCOURGE UNITS (Meat Wagon, Banshee, Necromancer, Death Knight, Dark Ranger)
# ==============================================================================
def build_meat_wagon_sprites():
    """Sculpt WC3 Meat Wagon (bone rib-cage rails, front spiked roller, corpse & skull heap, plague glow)."""
    src_path = os.path.join(GRAPHICS_DIR, "human", "units", "catapult.png")
    dst_path = os.path.join(GRAPHICS_DIR, "forsaken", "units", "meat_wagon.png")
    base_im = Image.open(src_path)
    pal = base_im.getpalette()
    orig_px = base_im.load()
    rgba = base_im.convert("RGBA")
    w, h = rgba.size  # 160x320 (10 rows: 0=still, 3=move, 1,4,6,8,9=attack, 2,5,7=death)
    px = rgba.load()

    death_rows = {2, 5, 7}
    bone_light = (228, 224, 206, 255)
    bone_mid = (170, 165, 148, 255)
    iron_spike = (195, 200, 210, 255)
    gore_red = (155, 26, 32, 255)
    plague_green = (95, 245, 105, 255)
    plague_dark = (40, 145, 52, 255)

    for r in range(h // 32):
        for c in range(5):
            ox, oy = c * 32, r * 32
            for y in range(32):
                for x in range(32):
                    rr, gg, bb, aa = px[ox + x, oy + y]
                    if aa == 0:
                        continue
                    oi = orig_px[ox + x, oy + y]
                    if 200 <= oi <= 207:
                        px[ox + x, oy + y] = (254, 0, oi, 255)
                        continue
                    lum = 0.299 * rr + 0.587 * gg + 0.114 * bb
                    # Dark blighted iron & charred bone frame
                    if rr > bb + 18:
                        px[ox + x, oy + y] = (int(lum * 0.48 + 16), int(lum * 0.40 + 12), int(lum * 0.58 + 24), 255)
                    else:
                        px[ox + x, oy + y] = (int(lum * 0.75 + 18), int(lum * 0.75 + 18), int(lum * 0.72 + 16), 255)

            if r in death_rows:
                continue

            # Add white bone rib-cage rails & corpse/plague pile in the Meat Wagon bed
            for rib_i in (-4, -1, 2, 5):
                if c in (0, 4):  # N / S
                    ry = 15 + rib_i
                    if 4 <= ry < 28:
                        px[ox + 9, oy + ry] = bone_light
                        px[ox + 10, oy + ry] = bone_mid
                        px[ox + 21, oy + ry] = bone_mid
                        px[ox + 22, oy + ry] = bone_light
                else:  # NE / E / SE
                    rx = 15 + rib_i
                    if 4 <= rx < 28:
                        px[ox + rx, oy + 10] = bone_light
                        px[ox + rx, oy + 11] = bone_mid
                        px[ox + rx, oy + 21] = bone_mid
                        px[ox + rx, oy + 22] = bone_light

            # Corpse heap & glowing green plague in center of wagon bed
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    if dx * dx + dy * dy <= 10:
                        if (dx + dy) % 3 == 0:
                            px[ox + 16 + dx, oy + 16 + dy] = gore_red
                        elif (dx * dy) % 2 == 0:
                            px[ox + 16 + dx, oy + 16 + dy] = plague_green if abs(dx) <= 1 else plague_dark
                        else:
                            px[ox + 16 + dx, oy + 16 + dy] = bone_light

            # Front spiked iron meat-grinder roller
            if c == 0:
                for sx in range(10, 22, 2):
                    px[ox + sx, oy + 5] = iron_spike
                    px[ox + sx, oy + 6] = gore_red
            elif c == 4:
                for sx in range(10, 22, 2):
                    px[ox + sx, oy + 26] = iron_spike
                    px[ox + sx, oy + 25] = gore_red
            elif c == 2:
                for sy in range(11, 22, 2):
                    px[ox + 26, oy + sy] = iron_spike
                    px[ox + 25, oy + sy] = gore_red

    out = rgba_to_indexed(rgba, pal, base_im)
    out.save(dst_path)
    print(f"Generated WC3 Meat Wagon sprite sheet: {dst_path}")


def build_banshee_sprites():
    """Sculpt WC3 Banshee (floating female wraith: tapering spectral tail instead of legs, floating hair, glowing orbs)."""
    src_path = os.path.join(GRAPHICS_DIR, "human", "units", "conjurer.png")
    dst_path = os.path.join(GRAPHICS_DIR, "forsaken", "units", "banshee.png")
    base_im = Image.open(src_path)
    pal = base_im.getpalette()
    orig_px = base_im.load()
    rgba = base_im.convert("RGBA")
    w, h = rgba.size  # 160x416 (13 rows for frameNumbers_5_5_4_4: death rows are 2, 5, 8, 11)
    px = rgba.load()

    death_rows = {2, 5, 8, 11}
    wraith_bright = (185, 245, 255, 255)
    wraith_cyan = (95, 195, 235, 255)
    wraith_Mid = (68, 125, 185, 255)
    wraith_dark = (42, 65, 120, 255)
    hair_pale = (215, 225, 250, 255)

    for r in range(h // 32):
        for c in range(5):
            ox, oy = c * 32, r * 32
            pts = []
            for y in range(32):
                for x in range(32):
                    p = px[ox + x, oy + y]
                    if p[3] > 0:
                        pts.append((x, y, p, orig_px[ox + x, oy + y]))
            if not pts:
                continue

            min_x = min(p[0] for p in pts)
            max_x = max(p[0] for p in pts)
            min_y = min(p[1] for p in pts)
            max_y = max(p[1] for p in pts)
            mid_x = (min_x + max_x) // 2

            for x, y, p, oi in pts:
                if 200 <= oi <= 207:
                    px[ox + x, oy + y] = (254, 0, oi, 255)
                    continue
                lum = 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
                # Erase wooden staff on outer side so Banshee casts with ghostly hands
                if abs(x - mid_x) > 6 and p[0] > p[2] + 20:
                    px[ox + x, oy + y] = (0, 0, 0, 0)
                elif lum > 150:
                    px[ox + x, oy + y] = wraith_bright
                elif lum > 100:
                    px[ox + x, oy + y] = wraith_cyan
                elif lum > 55:
                    px[ox + x, oy + y] = wraith_Mid
                else:
                    px[ox + x, oy + y] = wraith_dark

            if r in death_rows:
                continue

            # Replace human legs at bottom (max_y - 6 .. max_y) with a tapering floating spectral tail!
            tail_start = max_y - 6
            for y in range(tail_start, max_y + 1):
                for x in range(32):
                    px[ox + x, oy + y] = (0, 0, 0, 0)
                t_prog = y - tail_start
                half_w = max(0, 3 - t_prog // 2)
                sway = ((r + t_prog) % 3) - 1
                for dx in range(-half_w, half_w + 1):
                    tx = mid_x + sway + dx
                    if 0 <= tx < 32:
                        px[ox + tx, oy + y] = wraith_cyan if abs(dx) < half_w else wraith_dark

            # Streaming spectral white-violet hair floating above head
            for hx_off in range(-2, 3):
                hx_p = mid_x + hx_off
                hy_p = min_y - 1 - (abs(hx_off) % 2)
                if 0 <= hx_p < 32 and 1 <= hy_p < 32:
                    px[ox + hx_p, oy + hy_p] = hair_pale
                    px[ox + hx_p, oy + hy_p - 1] = wraith_bright

            # Glowing eyes & dark wailing Banshee mouth
            if c != 0 and min_y + 4 < 32:
                px[ox + mid_x - 1, oy + min_y + 3] = wraith_bright
                px[ox + mid_x + 1, oy + min_y + 3] = wraith_bright
                px[ox + mid_x, oy + min_y + 5] = (20, 15, 35, 255)  # Open wailing mouth

    out = rgba_to_indexed(rgba, pal, base_im)
    out.save(dst_path)
    print(f"Generated WC3 Banshee sprite sheet: {dst_path}")


def build_necromancer_sprites():
    """Sculpt WC3 Necromancer (dark crimson/obsidian cultist robes, white skull mask, long white beard, green skull staff)."""
    src_path = os.path.join(GRAPHICS_DIR, "human", "units", "cleric.png")
    dst_path = os.path.join(GRAPHICS_DIR, "forsaken", "units", "necromancer.png")
    base_im = Image.open(src_path)
    pal = base_im.getpalette()
    orig_px = base_im.load()
    rgba = base_im.convert("RGBA")
    w, h = rgba.size  # 160x384 (12 rows for frameNumbers_5_5_4_3: death rows are 2, 5, 8)
    px = rgba.load()

    death_rows = {2, 5, 8}
    robe_dark = (32, 20, 42, 255)
    robe_mid = (58, 32, 72, 255)
    robe_trim = (135, 28, 45, 255)
    skull_white = (230, 226, 212, 255)
    beard_silver = (195, 198, 210, 255)
    fel_green = (95, 250, 110, 255)

    for r in range(h // 32):
        for c in range(5):
            ox, oy = c * 32, r * 32
            pts = []
            for y in range(32):
                for x in range(32):
                    p = px[ox + x, oy + y]
                    if p[3] > 0:
                        pts.append((x, y, p, orig_px[ox + x, oy + y]))
            if not pts:
                continue

            min_x = min(p[0] for p in pts)
            max_x = max(p[0] for p in pts)
            min_y = min(p[1] for p in pts)
            mid_x = (min_x + max_x) // 2

            for x, y, p, oi in pts:
                if 200 <= oi <= 207:
                    px[ox + x, oy + y] = (254, 0, oi, 255)
                    continue
                lum = 0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]
                if lum > 155:
                    px[ox + x, oy + y] = skull_white
                elif lum > 100:
                    px[ox + x, oy + y] = robe_trim if p[0] > p[2] + 20 else robe_mid
                elif lum > 50:
                    px[ox + x, oy + y] = robe_mid
                else:
                    px[ox + x, oy + y] = robe_dark

            if r in death_rows:
                continue

            # White skull cowl/mask + glowing green eyes + long silver beard
            for dx in range(-1, 2):
                if 0 <= mid_x + dx < 32 and 0 <= min_y + 2 < 32:
                    px[ox + mid_x + dx, oy + min_y + 2] = skull_white
            if c != 0:
                px[ox + mid_x - 1, oy + min_y + 3] = fel_green
                px[ox + mid_x + 1, oy + min_y + 3] = fel_green
                # Long white Necromancer beard down chest
                for by_off in range(4, 9):
                    if min_y + by_off < 32:
                        px[ox + mid_x, oy + min_y + by_off] = beard_silver
                        if by_off < 7 and mid_x + 1 < 32:
                            px[ox + mid_x + 1, oy + min_y + by_off] = skull_white

            # Skull-topped necromantic staff with glowing fel-green crystal
            staff_x = max_x if c in (1, 2, 3) else min_x
            staff_y = min_y + 3
            if 1 <= staff_x < 31 and 2 <= staff_y < 30:
                px[ox + staff_x, oy + staff_y] = skull_white
                px[ox + staff_x, oy + staff_y - 1] = fel_green
                px[ox + staff_x - 1, oy + staff_y] = fel_green
                px[ox + staff_x + 1, oy + staff_y] = fel_green

    out = rgba_to_indexed(rgba, pal, base_im)
    out.save(dst_path)
    print(f"Generated WC3 Necromancer sprite sheet: {dst_path}")


def build_death_knight_sprites():
    """Sculpt WC3 Death Knight (skeletal horse with exposed white ribs & glowing cyan eyes, horned helm, glowing cyan Runeblade)."""
    src_path = os.path.join(GRAPHICS_DIR, "human", "units", "knight.png")
    dst_path = os.path.join(GRAPHICS_DIR, "forsaken", "units", "death_knight.png")
    base_im = Image.open(src_path)
    pal = base_im.getpalette()
    orig_px = base_im.load()
    rgba = base_im.convert("RGBA")
    w, h = rgba.size  # 160x480 (15 rows for frameNumbers_5_5_5_5: death rows are 2, 5, 8, 11, 14)
    px = rgba.load()

    death_rows = {2, 5, 8, 11, 14}
    bone_white = (228, 224, 208, 255)
    bone_shadow = (38, 34, 48, 255)
    plate_dark = (35, 38, 62, 255)
    plate_mid = (62, 68, 105, 255)
    rune_cyan = (105, 245, 255, 255)
    rune_glow = (195, 255, 255, 255)

    for r in range(h // 32):
        for c in range(5):
            ox, oy = c * 32, r * 32
            pts = []
            for y in range(32):
                for x in range(32):
                    p = px[ox + x, oy + y]
                    if p[3] > 0:
                        pts.append((x, y, p, orig_px[ox + x, oy + y]))
            if not pts:
                continue

            min_x = min(p[0] for p in pts)
            max_x = max(p[0] for p in pts)
            min_y = min(p[1] for p in pts)
            max_y = max(p[1] for p in pts)
            mid_x = (min_x + max_x) // 2
            mid_y = (min_y + max_y) // 2

            for x, y, p, oi in pts:
                if 200 <= oi <= 207:
                    px[ox + x, oy + y] = (254, 0, oi, 255)
                    continue
                rr, gg, bb, _ = p
                lum = 0.299 * rr + 0.587 * gg + 0.114 * bb
                # Weapon / bright steel -> glowing cyan Runeblade (Frostmourne)!
                if lum > 155 and abs(rr - gg) < 25:
                    px[ox + x, oy + y] = rune_glow if lum > 195 else rune_cyan
                # Horse brown body -> skeletal bone & dark rib hollows!
                elif rr > gg + 15 and gg > bb:
                    if y > mid_y and (x + y) % 2 == 0 and abs(x - mid_x) <= 5:
                        px[ox + x, oy + y] = bone_white if lum > 80 else bone_shadow
                    else:
                        px[ox + x, oy + y] = bone_shadow if lum < 90 else (155, 152, 140, 255)
                else:
                    px[ox + x, oy + y] = plate_mid if lum > 85 else plate_dark

            if r in death_rows:
                continue

            # Horned Death Knight helm & glowing cyan eyes
            if min_y >= 1:
                px[ox + max(0, mid_x - 2), oy + min_y] = bone_white
                px[ox + min(31, mid_x + 2), oy + min_y] = bone_white
            if c != 0 and min_y + 3 < 32:
                px[ox + mid_x, oy + min_y + 3] = rune_cyan

    out = rgba_to_indexed(rgba, pal, base_im)
    out.save(dst_path)
    print(f"Generated WC3 Death Knight sprite sheet: {dst_path}")


def build_dark_ranger_sprites():
    """Sculpt WC3 Dark Ranger & Sylvanas (pointed dark hood, flowing cloak, pale undead skin, glowing red eyes, curved bone bow)."""
    src_path = os.path.join(GRAPHICS_DIR, "human", "units", "archer.png")
    base_im = Image.open(src_path)
    pal = base_im.getpalette()
    orig_px = base_im.load()
    w, h = base_im.size  # 160x320 (10 rows for frameNumbers_5_5_2_3: death rows are 2, 5, 7)
    death_rows = {2, 5, 7}

    for mode, dst_name in [("dark_ranger", "dark_ranger.png"), ("sylvanas", "sylvanas.png")]:
        rgba = base_im.convert("RGBA")
        px = rgba.load()
        hood_dark = (32, 22, 48, 255) if mode == "dark_ranger" else (48, 18, 42, 255)
        hood_mid = (58, 42, 85, 255) if mode == "dark_ranger" else (92, 32, 78, 255)
        pale_skin = (185, 195, 215, 255)
        bone_bow = (220, 215, 198, 255)
        eye_red = (255, 42, 48, 255)

        for r in range(h // 32):
            for c in range(5):
                ox, oy = c * 32, r * 32
                pts = []
                for y in range(32):
                    for x in range(32):
                        p = px[ox + x, oy + y]
                        if p[3] > 0:
                            pts.append((x, y, p, orig_px[ox + x, oy + y]))
                if not pts:
                    continue

                min_x = min(p[0] for p in pts)
                max_x = max(p[0] for p in pts)
                min_y = min(p[1] for p in pts)
                mid_x = (min_x + max_x) // 2

                for x, y, p, oi in pts:
                    if 200 <= oi <= 207:
                        px[ox + x, oy + y] = (254, 0, oi, 255)
                        continue
                    rr, gg, bb, _ = p
                    lum = 0.299 * rr + 0.587 * gg + 0.114 * bb
                    # Bow wood -> curved bone bow
                    if abs(x - mid_x) > 4 and rr > bb + 20:
                        px[ox + x, oy + y] = bone_bow
                    elif rr > 110 and gg > 75 and bb < 120:
                        px[ox + x, oy + y] = pale_skin
                    elif lum > 95:
                        px[ox + x, oy + y] = hood_mid
                    else:
                        px[ox + x, oy + y] = hood_dark

                if r in death_rows:
                    continue

                # Pointed Dark Ranger hood & glowing red eyes
                if min_y >= 1:
                    px[ox + mid_x, oy + min_y - 1] = hood_dark
                    px[ox + mid_x, oy + min_y] = hood_mid
                if c != 0 and min_y + 3 < 32:
                    px[ox + mid_x + (1 if c in (1, 2, 3) else -1), oy + min_y + 3] = eye_red
                    if c == 4:
                        px[ox + mid_x + 1, oy + min_y + 3] = eye_red

        out = rgba_to_indexed(rgba, pal, base_im)
        out.save(os.path.join(GRAPHICS_DIR, "forsaken", "units", dst_name))
        print(f"Generated WC3 {mode} sprite sheet: {dst_name}")


# ==============================================================================
# 3. SCULPTED WC1-SHADED SCOURGE BUILDINGS
# ==============================================================================
def recolor_to_obsidian_undead(rgba_im, orig_im=None):
    """Transform a WC1 building's palette into shaded dark obsidian stone, bone, blight & fel-green."""
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
                px[x, y] = (int(lum * 0.45 + 12), int(lum * 0.65 + 18), int(lum * 0.50 + 16), 255)
            elif lum > 145 and abs(r - g) < 35:
                px[x, y] = (min(255, int(lum * 0.95 + 15)), min(255, int(lum * 0.92 + 12)), min(255, int(lum * 0.82 + 5)), 255)
            elif r > g + 35 and r > b + 35:
                px[x, y] = (int(lum * 0.4 + 20), min(255, int(lum * 1.35 + 45)), int(lum * 0.55 + 25), 255)
            elif r > b + 18:
                px[x, y] = (int(lum * 0.58 + 18), int(lum * 0.42 + 10), int(lum * 0.78 + 30), 255)
            else:
                px[x, y] = (int(lum * 0.62 + 14), int(lum * 0.58 + 14), int(lum * 0.80 + 26), 255)
    return out


def stamp_shaded_crystal(rgba_im, cx, cy, rx, ry):
    """Stamp a pixel-shaded 3D floating necrotic green crystal with facet highlights."""
    px = rgba_im.load()
    w, h = rgba_im.size
    for dy in range(-ry, ry + 1):
        span = int(rx * (1.0 - abs(dy) / float(ry + 1)))
        for dx in range(-span, span + 1):
            xx, yy = cx + dx, cy + dy
            if 0 <= xx < w and 0 <= yy < h:
                if abs(dx) + abs(dy) <= 2:
                    px[xx, yy] = (210, 255, 210, 255)
                elif abs(dx) == span or abs(dy) == ry:
                    px[xx, yy] = (22, 75, 34, 255)
                elif dx < 0 and dy < 0:
                    px[xx, yy] = (135, 250, 140, 255)
                elif dx <= 0:
                    px[xx, yy] = (80, 215, 90, 255)
                elif dy < 0:
                    px[xx, yy] = (60, 180, 72, 255)
                else:
                    px[xx, yy] = (35, 125, 48, 255)


def stamp_ziggurat_pyramid(base_rgba, stone_tex_rgba, cx, cy, base_r, tiers=3):
    """Sculpt a genuine pixel-shaded stepped Ziggurat using real WC1 stone texture pixels."""
    px = base_rgba.load()
    tex_px = stone_tex_rgba.load()
    tw, th = stone_tex_rgba.size
    w, h = base_rgba.size

    for t in range(tiers):
        r_x = base_r - t * 5
        r_y = base_r - t * 5
        y_off = cy + (tiers - 1 - t) * 3 - 2
        for dy in range(-r_y, r_y + 1):
            for dx in range(-r_x, r_x + 1):
                if abs(dx) + abs(dy) <= int(r_x * 1.35) and max(abs(dx), abs(dy)) <= r_x:
                    xx, yy = cx + dx, y_off + dy
                    if 0 <= xx < w and 0 <= yy < h:
                        tr, tg, tb, _ = tex_px[(xx * 2 + t * 7) % tw, (yy * 2 + t * 11) % th]
                        lum = 0.299 * tr + 0.587 * tg + 0.114 * tb
                        on_rim = (abs(dx) + abs(dy) >= int(r_x * 1.35) - 1) or (max(abs(dx), abs(dy)) == r_x)
                        if on_rim:
                            if dx + dy < 0:
                                px[xx, yy] = (min(255, int(lum * 0.8 + 55)), min(255, int(lum * 0.7 + 45)), min(255, int(lum * 1.0 + 75)), 255)
                            else:
                                px[xx, yy] = (25, 20, 35, 255)
                        elif dy == r_y - 2 and abs(dx) % 4 <= 1:
                            px[xx, yy] = (95, 245, 110, 255)
                        elif dx + dy < 0:
                            px[xx, yy] = (int(lum * 0.65 + 28), int(lum * 0.52 + 18), int(lum * 0.88 + 44), 255)
                        else:
                            px[xx, yy] = (int(lum * 0.42 + 14), int(lum * 0.35 + 10), int(lum * 0.60 + 24), 255)


def build_forsaken_building(name, ts):
    orc_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "orc", "buildings")
    skull_tower_im = Image.open(os.path.join(orc_dir, "tower.png"))
    skull_rgba = recolor_to_obsidian_undead(skull_tower_im.convert("RGBA"), skull_tower_im)
    temple_im = Image.open(os.path.join(orc_dir, "temple.png"))
    temple_rgba = recolor_to_obsidian_undead(temple_im.convert("RGBA"), temple_im)

    if name == "tower":
        im = skull_rgba.copy()
        px = im.load()
        for y in range(8, 30):
            for x in range(10, 38):
                r, g, b, a = px[x, y]
                if r == 254 and g == 0:
                    px[x, y] = (110, 255, 120, 255)
        stamp_shaded_crystal(im, 24, 7, 5, 6)
        return im

    elif name == "church":
        im = temple_rgba.copy()
        stamp_shaded_crystal(im, 32, 28, 6, 6)
        skull_crop = skull_rgba.crop((10, 4, 38, 28)).resize((18, 15), Image.Resampling.BILINEAR)
        im.paste(skull_crop, (23, 6), skull_crop)
        return im

    elif name == "barracks":
        base_im = Image.open(os.path.join(orc_dir, "barracks.png"))
        im = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
        skull_crop = skull_rgba.crop((6, 2, 42, 38)).resize((30, 28), Image.Resampling.BILINEAR)
        im.paste(skull_crop, (17, 12), skull_crop)
        stamp_shaded_crystal(im, 34, 46, 4, 4)
        return im

    elif name == "farm":
        base_im = Image.open(os.path.join(orc_dir, "farm.png"))
        im = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
        stamp_ziggurat_pyramid(im, temple_rgba, 24, 26, 17, tiers=3)
        stamp_shaded_crystal(im, 24, 10, 6, 7)
        return im

    elif name == "town_hall":
        base_im = Image.open(os.path.join(orc_dir, "town_hall.png"))
        im = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
        px = im.load()
        for y in range(8, 56):
            for x in range(8, 56):
                if 20 <= max(abs(x - 32), abs(y - 32)) <= 23 and px[x, y][3] > 0:
                    px[x, y] = (55, 195, 70, 255) if (x + y) % 2 == 0 else (30, 120, 42, 255)
        stamp_ziggurat_pyramid(im, temple_rgba, 32, 34, 22, tiers=4)
        for ox_p, oy_p in [(8, 12), (48, 12), (8, 44), (48, 44)]:
            stamp_shaded_crystal(im, ox_p + 4, oy_p, 3, 4)
        stamp_shaded_crystal(im, 32, 12, 8, 9)
        return im

    elif name == "lumber_mill":
        base_im = Image.open(os.path.join(orc_dir, "kennel.png"))
        im = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
        px = im.load()
        for gx, gy in [(16, 26), (26, 22), (18, 38), (28, 34), (38, 42)]:
            for dy in range(-5, 3):
                for dx in range(-2, 3):
                    if dy == -5 and abs(dx) == 2:
                        continue
                    xx, yy = gx + dx, gy + dy
                    if 0 <= xx < 64 and 0 <= yy < 64:
                        if dy >= 1:
                            px[xx, yy] = (28, 22, 35, 255)
                        elif dx < 0 or dy == -5:
                            px[xx, yy] = (175, 170, 155, 255)
                        else:
                            px[xx, yy] = (110, 105, 95, 255)
        return im

    elif name == "blacksmith":
        base_im = Image.open(os.path.join(orc_dir, "blacksmith.png"))
        im = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
        stamp_shaded_crystal(im, 14, 24, 4, 4)
        stamp_shaded_crystal(im, 35, 16, 4, 4)
        return im

    elif name == "stable":
        base_im = Image.open(os.path.join(orc_dir, "kennel.png"))
        im = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
        skull_crop = skull_rgba.crop((8, 4, 40, 34)).resize((20, 18), Image.Resampling.BILINEAR)
        im.paste(skull_crop, (36, 10), skull_crop)
        stamp_shaded_crystal(im, 20, 32, 4, 4)
        return im

    elif name == "stormwind_keep":
        base_im = Image.open(os.path.join(orc_dir, "blackrock_spire.png"))
        im = recolor_to_obsidian_undead(base_im.convert("RGBA"), base_im)
        stamp_shaded_crystal(im, 40, 16, 7, 8)
        stamp_shaded_crystal(im, 22, 38, 5, 5)
        stamp_shaded_crystal(im, 58, 38, 5, 5)
        return im


def build_construction_strip(final_rgba, w, h, orc_constr_path):
    orc_c = Image.open(orc_constr_path)
    if orc_c.size != (w, h * 3):
        orc_c = orc_c.resize((w, h * 3), Image.Resampling.NEAREST)
    sheet = recolor_to_obsidian_undead(orc_c.convert("RGBA"), orc_c)
    f2 = final_rgba.copy()
    stamp_shaded_crystal(sheet, w // 2, h // 2, 5, 5)
    stamp_shaded_crystal(sheet, w // 2, h + h // 2, 6, 6)
    sheet.paste(f2, (0, h * 2))
    return sheet


def build_all_buildings():
    specs = [
        ("farm", 48, 48, "farm_construction.png"),
        ("town_hall", 64, 64, "town_hall_construction.png"),
        ("barracks", 64, 64, "barracks_construction.png"),
        ("lumber_mill", 64, 64, "lumber_mill_construction.png"),
        ("blacksmith", 48, 48, "blacksmith_construction.png"),
        ("stable", 64, 64, "kennel_construction.png"),
        ("church", 64, 64, "temple_construction.png"),
        ("tower", 48, 48, "tower_construction.png"),
        ("stormwind_keep", 80, 80, None),
    ]
    for ts in ("forest", "swamp"):
        ref_pal = Image.open(os.path.join(GRAPHICS_DIR, "tilesets", ts, "orc", "buildings", "town_hall.png")).getpalette()
        orc_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "orc", "buildings")
        out_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "forsaken", "buildings")
        os.makedirs(out_dir, exist_ok=True)

        for name, w, h, constr_src in specs:
            b_rgba = build_forsaken_building(name, ts)
            b_idx = rgba_to_indexed(b_rgba, ref_pal)
            b_idx.save(os.path.join(out_dir, f"{name}.png"))

            if constr_src:
                c_rgba = build_construction_strip(b_rgba, w, h, os.path.join(orc_dir, constr_src))
                c_idx = rgba_to_indexed(c_rgba, ref_pal)
                c_idx.save(os.path.join(out_dir, f"{name}_construction.png"))

        print(f"Generated WC1-shaded Scourge buildings for tileset: {ts}")


# ==============================================================================
# 4. AUTHENTIC WC1 27x19 ICONS (Pixel-Sculpted from portrait_icons.png frames!)
# ==============================================================================
def get_wc1_icon_frame(pi_im, frame_idx):
    box = (0, frame_idx * 19, 27, (frame_idx + 1) * 19)
    idx_crop = pi_im.crop(box)
    rgba_crop = idx_crop.convert("RGBA")
    return idx_crop, rgba_crop


def transform_portrait_icon(pi_im, frame_idx, mode_name):
    idx_crop, rgba = get_wc1_icon_frame(pi_im, frame_idx)
    orig_px = idx_crop.load()
    px = rgba.load()

    for y in range(19):
        for x in range(27):
            oi = orig_px[x, y]
            if 200 <= oi <= 207:
                px[x, y] = (254, 0, oi, 255)
                continue

            r, g, b, _ = px[x, y]
            lum = 0.299 * r + 0.587 * g + 0.114 * b

            if mode_name == "acolyte":
                if r > g + 25:
                    px[x, y] = (int(lum * 0.58 + 20), int(lum * 0.40 + 10), int(lum * 0.82 + 35), 255)
                elif g > r + 10:
                    px[x, y] = (int(lum * 0.25 + 8), int(lum * 0.22 + 6), int(lum * 0.32 + 12), 255)
                else:
                    px[x, y] = (int(lum * 0.7), int(lum * 0.7), int(lum * 0.8), 255)

            elif mode_name == "ghoul":
                if lum > 110:
                    px[x, y] = (int(lum * 0.75 + 15), int(lum * 0.92 + 20), int(lum * 0.70 + 10), 255)
                else:
                    px[x, y] = (int(lum * 0.55 + 15), int(lum * 0.68 + 15), int(lum * 0.50 + 12), 255)

            elif mode_name == "dark_ranger":
                if g > r and g > 45:
                    px[x, y] = (min(255, int(lum * 0.95 + 35)), min(255, int(lum * 0.95 + 35)), min(255, int(lum * 1.15 + 50)), 255)
                else:
                    px[x, y] = (int(lum * 0.55 + 18), int(lum * 0.38 + 8), int(lum * 0.80 + 32), 255)

            elif mode_name == "sylvanas":
                if g > r and g > 45:
                    px[x, y] = (min(255, int(lum * 1.0 + 40)), min(255, int(lum * 0.98 + 38)), min(255, int(lum * 1.2 + 55)), 255)
                else:
                    px[x, y] = (min(255, int(lum * 0.85 + 30)), int(lum * 0.32 + 8), min(255, int(lum * 0.75 + 28)), 255)

            elif mode_name == "death_knight":
                if r > g + 20 and g > b:
                    px[x, y] = (min(255, int(lum * 0.95 + 30)), min(255, int(lum * 0.95 + 28)), min(255, int(lum * 0.88 + 20)), 255)
                else:
                    px[x, y] = (int(lum * 0.52 + 12), int(lum * 0.55 + 16), int(lum * 0.82 + 30), 255)

            elif mode_name == "meat_wagon":
                if r > b + 20:
                    px[x, y] = (int(lum * 0.55 + 16), int(lum * 0.48 + 12), int(lum * 0.65 + 22), 255)
                else:
                    px[x, y] = (int(lum * 0.85 + 20), int(lum * 0.85 + 18), int(lum * 0.78 + 12), 255)

            elif mode_name == "necromancer":
                if r > g + 40:
                    px[x, y] = (int(lum * 0.4 + 15), min(255, int(lum * 1.35 + 45)), int(lum * 0.55 + 20), 255)
                elif r > b + 20:
                    px[x, y] = (min(255, int(lum * 0.9 + 25)), min(255, int(lum * 0.95 + 28)), min(255, int(lum * 0.88 + 22)), 255)
                else:
                    px[x, y] = (int(lum * 0.75 + 20), int(lum * 0.68 + 14), int(lum * 0.92 + 32), 255)

            elif mode_name == "banshee":
                px[x, y] = (int(lum * 0.55 + 25), min(255, int(lum * 1.05 + 45)), min(255, int(lum * 1.25 + 60)), 255)

            elif mode_name == "varimathras":
                if r > g + 30:
                    px[x, y] = (int(lum * 0.75 + 28), int(lum * 0.40 + 12), int(lum * 0.88 + 38), 255)
                elif g > r + 10:
                    px[x, y] = (int(lum * 0.5 + 30), min(255, int(lum * 1.4 + 60)), int(lum * 0.6 + 30), 255)

            elif mode_name in ("weapon1", "weapon2"):
                boost = 1.25 if mode_name == "weapon2" else 0.95
                if r > b + 20:
                    px[x, y] = (int(lum * 0.55 + 18), int(lum * 0.45 + 12), int(lum * 0.78 + 30), 255)
                else:
                    px[x, y] = (
                        min(255, int(lum * 0.85 * boost + 15)),
                        min(255, int(lum * 1.05 * boost + 25)),
                        min(255, int(lum * 0.90 * boost + 20)),
                        255,
                    )

    if mode_name == "acolyte":
        px[13, 8] = (255, 235, 85, 255)
        px[14, 8] = (255, 200, 50, 255)
        px[18, 10] = (255, 235, 85, 255)
    elif mode_name == "ghoul":
        px[9, 6] = (255, 60, 40, 255)
        px[10, 6] = (255, 220, 80, 255)
        px[14, 6] = (255, 60, 40, 255)
        px[15, 6] = (255, 220, 80, 255)
        for fx in range(8, 16, 2):
            px[fx, 11] = (235, 230, 210, 255)
            px[fx, 12] = (175, 28, 32, 255)
    elif mode_name in ("dark_ranger", "sylvanas"):
        px[14, 7] = (255, 45, 55, 255)
        px[15, 7] = (255, 120, 120, 255)
        px[19, 8] = (255, 45, 55, 255)
    elif mode_name == "death_knight":
        px[6, 6] = (100, 245, 255, 255)
        px[10, 6] = (100, 245, 255, 255)
    elif mode_name == "meat_wagon":
        for dy in range(1, 6):
            for dx in range(8, 14):
                if (dx - 11) ** 2 + (dy - 3) ** 2 <= 6:
                    px[dx, dy] = (95, 250, 110, 255)

    return rgba


def build_all_icons():
    pi_path = os.path.join(GRAPHICS_DIR, "tilesets", "forest", "portrait_icons.png")
    pi_im = Image.open(pi_path)
    ref_pal = pi_im.getpalette()

    unit_icon_specs = [
        ("icon-acolyte.png", 3, "acolyte"),
        ("icon-ghoul.png", 50, "ghoul"),
        ("icon-dark-ranger.png", 55, "dark_ranger"),
        ("icon-sylvanas.png", 55, "sylvanas"),
        ("icon-death-knight.png", 8, "death_knight"),
        ("icon-meat-wagon.png", 7, "meat_wagon"),
        ("icon-necromancer.png", 54, "necromancer"),
        ("icon-banshee.png", 13, "banshee"),
        ("icon-varimathras.png", 51, "varimathras"),
        ("icon-claws1.png", 69, "weapon1"),
        ("icon-claws2.png", 70, "weapon2"),
        ("icon-carapace1.png", 83, "weapon1"),
        ("icon-carapace2.png", 84, "weapon2"),
        ("icon-dark-arrow1.png", 72, "weapon1"),
        ("icon-dark-arrow2.png", 73, "weapon2"),
        ("icon-skeletal-steed1.png", 77, "death_knight"),
        ("icon-skeletal-steed2.png", 78, "death_knight"),
        ("icon-move-forsaken.png", 34, "acolyte"),
    ]

    for icon_name, frame_idx, mode_name in unit_icon_specs:
        rgba = transform_portrait_icon(pi_im, frame_idx, mode_name)
        idx_out = rgba_to_indexed(rgba, ref_pal)
        idx_out.save(os.path.join(CONTRIB_DIR, "ui", "forsaken", icon_name))
        idx_out.save(os.path.join(GRAPHICS_DIR, "ui", "forsaken", icon_name))

    building_icon_specs = [
        ("icon-forsaken-farm.png", 15, True),
        ("icon-forsaken-town-hall.png", 21, True),
        ("icon-forsaken-barracks.png", 17, False),
        ("icon-forsaken-lumber-mill.png", 25, False),
        ("icon-forsaken-blacksmith.png", 27, True),
        ("icon-forsaken-stable.png", 25, False),
        ("icon-forsaken-church.png", 29, True),
        ("icon-forsaken-tower.png", 19, True),
    ]
    for icon_name, frame_idx, add_crystal in building_icon_specs:
        idx_crop, rgba = get_wc1_icon_frame(pi_im, frame_idx)
        rgba = recolor_to_obsidian_undead(rgba, idx_crop)
        if "farm" in icon_name or "town-hall" in icon_name:
            stamp_ziggurat_pyramid(rgba, rgba, 13, 10, 8, tiers=2)
        if add_crystal:
            stamp_shaded_crystal(rgba, 13, 5, 3, 3)
        idx_out = rgba_to_indexed(rgba, ref_pal)
        idx_out.save(os.path.join(CONTRIB_DIR, "ui", "forsaken", icon_name))
        idx_out.save(os.path.join(GRAPHICS_DIR, "ui", "forsaken", icon_name))

    print("Generated all authentic WC1-shaded 27x19 Scourge icons.")


if __name__ == "__main__":
    build_ghoul_sprites()
    build_meat_wagon_sprites()
    build_banshee_sprites()
    build_necromancer_sprites()
    build_death_knight_sprites()
    build_dark_ranger_sprites()
    build_all_buildings()
    build_all_icons()
