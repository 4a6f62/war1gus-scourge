#!/usr/bin/env python3
"""
Build dedicated Acolyte sprite sheets for War1gus Forsaken mod.
Transforms the worker frames into an authentic Warcraft Undead Acolyte:
- Deep pointed cultist cowl/hood with shadowy interior
- Menacing glowing spectral eyes
- Flowing dark tattered robes covering legs
- Ceremonial ritual blade / dark sickle
- Custom resource sprites (corrupted crystal for gold, blighted timber for wood)
"""

import os
from PIL import Image

BASE_DIR = "/home/smiles/forsaken-mod"
GRAPHICS_DIR = os.path.join(BASE_DIR, "graphics")

def create_acolyte_sheet(src_path, dst_path, resource_type=None):
    base_im = Image.open(src_path)
    pal = base_im.getpalette()
    
    # We will work in indexed mode or RGBA then map back to palette
    # Let's inspect the palette colors
    # Palette 200..207 are player colors
    # 255 is transparent
    
    # Convert base to RGBA for pixel-level artistic surgery
    rgba = base_im.convert("RGBA")
    w, h = rgba.size # 160 x 416 (5 x 13 frames of 32x32)
    pixels = rgba.load()
    
    # Color constants for Acolyte
    c_hood_dark = (35, 25, 45, 255)      # Deep shadow purple/black
    c_hood_mid = (55, 40, 70, 255)       # Robe body
    c_hood_light = (75, 55, 95, 255)     # Robe highlight
    c_shadow = (15, 10, 20, 255)         # Inner hood shadow
    c_eye = (245, 230, 90, 255)          # Glowing yellow cultist eyes
    c_eye_glow = (200, 180, 50, 255)
    c_blade = (210, 215, 225, 255)       # Sacrificial iron dagger
    c_blade_glow = (120, 240, 140, 255)  # Poison edge
    c_crystal = (180, 70, 240, 255)      # Blighted gold crystal
    c_crystal_bright = (230, 150, 255, 255)
    c_blighted_wood = (40, 35, 30, 255)  # Gnarled dark timber
    
    cols = w // 32
    rows = h // 32
    
    for r in range(rows):
        for c in range(cols):
            ox = c * 32
            oy = r * 32
            
            # Find bounds of the character in this 32x32 frame
            char_pixels = []
            for y in range(32):
                for x in range(32):
                    p = pixels[ox + x, oy + y]
                    if p[3] > 0: # Non-transparent
                        char_pixels.append((x, y, p))
            
            if not char_pixels:
                continue
            
            min_x = min(p[0] for p in char_pixels)
            max_x = max(p[0] for p in char_pixels)
            min_y = min(p[1] for p in char_pixels)
            max_y = max(p[1] for p in char_pixels)
            mid_x = (min_x + max_x) // 2
            
            # 1. Sculpt pointed cowl / hood at top
            # Add pointed tip above min_y
            if min_y >= 2:
                pixels[ox + mid_x, oy + min_y - 2] = c_hood_dark
                pixels[ox + mid_x, oy + min_y - 1] = c_hood_mid
                pixels[ox + mid_x - 1, oy + min_y - 1] = c_hood_dark
                pixels[ox + mid_x + 1, oy + min_y - 1] = c_hood_dark
            
            # Recolor head into deep hood and glowing eyes
            head_bottom = min_y + 8
            for y in range(min_y, min(32, head_bottom + 1)):
                for x in range(min_x, max_x + 1):
                    p = pixels[ox + x, oy + y]
                    if p[3] > 0:
                        # Recolor face to dark cowl interior
                        dist_center = abs(x - mid_x)
                        if y >= min_y + 3 and y <= min_y + 6 and dist_center <= 2:
                            # Shadow face interior
                            pixels[ox + x, oy + y] = c_shadow
                        else:
                            # Hood fabric
                            pixels[ox + x, oy + y] = c_hood_mid if dist_center <= 3 else c_hood_dark
            
            # Place glowing eyes
            eye_y = min_y + 4
            if 0 <= eye_y < 32:
                if mid_x - 1 >= 0:
                    pixels[ox + mid_x - 1, oy + eye_y] = c_eye
                if mid_x + 1 < 32:
                    pixels[ox + mid_x + 1, oy + eye_y] = c_eye
            
            # 2. Flowing dark robes: Extend robes over legs down to max_y
            robe_start_y = min_y + 9
            for y in range(robe_start_y, min(32, max_y + 1)):
                for x in range(min_x, max_x + 1):
                    p = pixels[ox + x, oy + y]
                    if p[3] > 0:
                        lum = 0.299*p[0] + 0.587*p[1] + 0.114*p[2]
                        # Don't overwrite player color (blue tones in original footman/peasant)
                        # Original player color in peasant has blue > red and blue > green
                        is_player_color = (p[2] > p[0] + 25 and p[2] > p[1] + 15)
                        if not is_player_color:
                            # Dark cultist robe folds
                            if lum > 100:
                                pixels[ox + x, oy + y] = c_hood_light
                            elif lum > 50:
                                pixels[ox + x, oy + y] = c_hood_mid
                            else:
                                pixels[ox + x, oy + y] = c_hood_dark
                
                # Broaden robe base between legs for a solid robe silhouette
                if y > min_y + 14 and y <= max_y:
                    for x in range(mid_x - 3, mid_x + 4):
                        if 0 <= x < 32:
                            if pixels[ox + x, oy + y][3] == 0:
                                pixels[ox + x, oy + y] = c_hood_dark
            
            # 3. Ritual dagger in hand for attack / harvesting
            # Replace tool pixels with dark sacrificial dagger
            if resource_type is None:
                # Add ceremonial blade glint
                blade_x = max_x + 1 if max_x + 1 < 31 else max_x
                blade_y = min_y + 7
                if 0 <= blade_y < 30:
                    pixels[ox + blade_x, oy + blade_y] = c_blade
                    pixels[ox + blade_x, oy + blade_y + 1] = c_blade
                    pixels[ox + blade_x, oy + blade_y + 2] = c_blade_glow
            
            # 4. Carrying resources
            elif resource_type == "gold":
                # Blighted purple/cyan corrupted crystal
                cx = mid_x
                cy = min_y + 7
                if 0 <= cy < 30 and 0 <= cx < 30:
                    pixels[ox + cx, oy + cy] = c_crystal_bright
                    pixels[ox + cx - 1, oy + cy + 1] = c_crystal
                    pixels[ox + cx + 1, oy + cy + 1] = c_crystal
                    pixels[ox + cx, oy + cy + 2] = c_crystal
                    pixels[ox + cx, oy + cy - 1] = c_crystal_bright
            elif resource_type == "wood":
                # Blighted gnarled timber / bone logs
                bx = mid_x
                by = min_y + 7
                for dx in range(-2, 3):
                    if 0 <= bx + dx < 32 and 0 <= by < 32:
                        pixels[ox + bx + dx, oy + by] = c_blighted_wood
                        pixels[ox + bx + dx, oy + by + 2] = (160, 160, 150, 255) # Bone strip
    
    # Convert RGBA back to palette using original palette so indices match
    # Palette index 255 is transparent
    pal_img = Image.new("P", (w, h))
    pal_img.putpalette(pal)
    
    # Map RGBA pixels back to palette indices
    out = Image.new("P", (w, h), 255)
    out.putpalette(pal)
    out_pixels = out.load()
    
    # Color matcher against the palette
    color_map_cache = {}
    
    def find_best_idx(rgb):
        if rgb in color_map_cache:
            return color_map_cache[rgb]
        best_d = 10000000
        best_idx = 0
        # Don't pick player color slots (200..207) or 255 (transparent)
        for i in range(255):
            if 200 <= i <= 207:
                continue
            pr, pg, pb = pal[i*3], pal[i*3+1], pal[i*3+2]
            d = (pr - rgb[0])**2 + (pg - rgb[1])**2 + (pb - rgb[2])**2
            if d < best_d:
                best_d = d
                best_idx = i
        color_map_cache[rgb] = best_idx
        return best_idx

    # Check original image for player color preservation
    base_pixels = base_im.load()
    for y in range(h):
        for x in range(w):
            p = pixels[x, y]
            orig_idx = base_pixels[x, y]
            if p[3] == 0:
                out_pixels[x, y] = 255
            elif 200 <= orig_idx <= 207:
                # Keep original player color index!
                out_pixels[x, y] = orig_idx
            else:
                idx = find_best_idx(p[:3])
                out_pixels[x, y] = idx
                
    out.info["transparency"] = 255
    out.save(dst_path)
    print(f"Successfully generated: {dst_path}")

def main():
    print("Generating dedicated Acolyte sprite sheets...")
    src_normal = os.path.join(GRAPHICS_DIR, "human", "units", "peasant.png")
    src_gold = os.path.join(GRAPHICS_DIR, "human", "units", "peasant_with_gold.png")
    src_wood = os.path.join(GRAPHICS_DIR, "human", "units", "peasant_with_wood.png")
    
    dst_normal = os.path.join(GRAPHICS_DIR, "forsaken", "units", "acolyte.png")
    dst_gold = os.path.join(GRAPHICS_DIR, "forsaken", "units", "acolyte_with_gold.png")
    dst_wood = os.path.join(GRAPHICS_DIR, "forsaken", "units", "acolyte_with_wood.png")
    
    create_acolyte_sheet(src_normal, dst_normal, resource_type=None)
    create_acolyte_sheet(src_gold, dst_gold, resource_type="gold")
    create_acolyte_sheet(src_wood, dst_wood, resource_type="wood")
    
    # Also generate icon-acolyte.png
    from PIL import ImageDraw
    icon = Image.new("RGBA", (27, 19), (25, 20, 35, 255))
    draw = ImageDraw.Draw(icon)
    draw.rectangle([0, 0, 26, 18], outline=(80, 60, 110))
    # Pointed cultist cowl
    draw.polygon([(7, 16), (13, 2), (19, 16)], fill=(55, 40, 75))
    draw.ellipse([10, 6, 16, 12], fill=(20, 15, 25)) # Shadow interior
    draw.point([12, 9], fill=(250, 230, 80)) # Glowing eye
    draw.point([14, 9], fill=(250, 230, 80)) # Glowing eye
    # Ritual dagger / sickle
    draw.arc([19, 4, 25, 14], start=180, end=0, fill=(180, 230, 200), width=1)
    draw.line([22, 10, 22, 16], fill=(120, 90, 60), width=1)
    
    icon_dst = os.path.join(BASE_DIR, "contrib", "graphics", "ui", "forsaken", "icon-acolyte.png")
    icon.save(icon_dst)
    icon.save(os.path.join(GRAPHICS_DIR, "ui", "forsaken", "icon-acolyte.png"))
    print(f"Successfully generated: {icon_dst}")

if __name__ == "__main__":
    main()
