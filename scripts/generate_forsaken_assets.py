#!/usr/bin/env python3
"""
Generate Forsaken assets for War1gus mod.
Recolors and styles units, buildings, UI, and icons to match the Undead/Forsaken lore
while maintaining Warcraft 1 8-bit palette and pixel-art aesthetic.
"""

import os
from PIL import Image, ImageDraw, ImageEnhance, ImageOps

BASE_DIR = "/home/smiles/forsaken-mod"
GRAPHICS_DIR = os.path.join(BASE_DIR, "graphics")
CONTRIB_DIR = os.path.join(BASE_DIR, "contrib", "graphics")

def ensure_dirs():
    dirs = [
        os.path.join(GRAPHICS_DIR, "forsaken", "units"),
        os.path.join(GRAPHICS_DIR, "tilesets", "forest", "forsaken", "buildings"),
        os.path.join(GRAPHICS_DIR, "tilesets", "swamp", "forsaken", "buildings"),
        os.path.join(GRAPHICS_DIR, "ui", "forsaken"),
        os.path.join(CONTRIB_DIR, "ui", "forsaken"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

def recolor_palette(im, color_fn):
    """
    Recolor an indexed image while preserving transparency (index 255)
    and player colors (indices 200..207).
    """
    if im.mode != "P":
        im = im.convert("RGBA")
        data = list(im.getdata())
        new_data = []
        for item in data:
            if item[3] == 0:
                new_data.append(item)
            else:
                r, g, b = item[:3]
                nr, ng, nb = color_fn(r, g, b)
                new_data.append((int(nr), int(ng), int(nb), item[3]))
        out = Image.new("RGBA", im.size)
        out.putdata(new_data)
        return out

    pal = im.getpalette()
    new_pal = list(pal)
    for i in range(256):
        if 200 <= i <= 207 or i == 255:
            continue
        r, g, b = pal[i*3], pal[i*3+1], pal[i*3+2]
        nr, ng, nb = color_fn(r, g, b)
        new_pal[i*3] = max(0, min(255, int(nr)))
        new_pal[i*3+1] = max(0, min(255, int(ng)))
        new_pal[i*3+2] = max(0, min(255, int(nb)))
    out = im.copy()
    out.putpalette(new_pal)
    return out

# --- Unit Color Functions ---

def fn_ghoul(r, g, b):
    # Rotting undead greenish-grey flesh, stained dark rags
    lum = 0.299*r + 0.587*g + 0.114*b
    # If bone / skin tones
    if lum > 100 and r > b:
        return (lum * 0.75, lum * 0.88 + 15, lum * 0.7)
    # Dark rags / leather
    return (lum * 0.5 + 15, lum * 0.45 + 10, lum * 0.6 + 25)

def fn_dark_ranger(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Skin (peach/tan) -> pale alabaster elven skin
    if r > 110 and g > 75 and b < 120 and r >= g:
        return (lum * 0.9 + 25, lum * 0.95 + 25, lum * 1.05 + 35)
    # Hair / feathers -> silver / pale lilac
    if r > 160 and g > 130:
        return (lum * 0.95 + 30, lum * 0.95 + 30, lum * 1.1 + 40)
    # Armor / leather -> obsidian with purple tones
    return (lum * 0.45 + 15, lum * 0.35 + 5, lum * 0.65 + 30)

def fn_forsaken_peasant(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Skin -> pale necrotic grey-green
    if r > 100 and g > 70 and b < 110:
        return (lum * 0.8 + 10, lum * 0.9 + 15, lum * 0.85 + 15)
    # Clothes -> dark tattered cowl & tunic
    return (lum * 0.5 + 20, lum * 0.45 + 15, lum * 0.65 + 35)

def fn_death_knight(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Horse flesh / brown -> skeletal bone white / dark ribs
    if r > g and g > b and lum > 50:
        return (lum * 0.85 + 25, lum * 0.9 + 25, lum * 0.95 + 30)
    # Armor (steel) -> blackened unholy iron with dark purple/cyan highlights
    if abs(r - g) < 25 and abs(g - b) < 25:
        return (lum * 0.55 + 10, lum * 0.5 + 15, lum * 0.75 + 30)
    return (lum * 0.6 + 10, lum * 0.5 + 10, lum * 0.7 + 25)

def fn_meat_wagon(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Wood -> decayed blighted dark timber
    if r > b:
        return (lum * 0.5 + 15, lum * 0.45 + 10, lum * 0.55 + 20)
    # Metal / wheels -> corroded iron & bone
    return (lum * 0.7 + 10, lum * 0.75 + 15, lum * 0.7 + 15)

def fn_necromancer(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Robes -> royal dark purple and obsidian
    if lum < 140:
        return (lum * 0.6 + 25, lum * 0.35 + 5, lum * 0.8 + 40)
    # Face / bone staff -> pale skull white
    return (lum * 0.9 + 25, lum * 0.92 + 25, lum * 0.95 + 25)

def fn_banshee(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Spectral cyan / ghostly lavender glow
    return (lum * 0.5 + 20, lum * 0.85 + 35, lum * 0.95 + 50)

def fn_sylvanas(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Skin -> ethereal pale banshee skin
    if r > 110 and g > 75 and b < 120:
        return (lum * 0.85 + 35, lum * 0.92 + 35, lum * 1.05 + 45)
    # Cloak / Armor -> deep regal maroon & midnight purple
    if lum > 80:
        return (lum * 0.8 + 30, lum * 0.4 + 10, lum * 0.85 + 40)
    return (lum * 0.45 + 20, lum * 0.25 + 5, lum * 0.6 + 30)

def generate_units():
    unit_map = [
        ("neutral/units/the_dead.png", "forsaken/units/ghoul.png", fn_ghoul),
        ("human/units/archer.png", "forsaken/units/dark_ranger.png", fn_dark_ranger),
        ("human/units/peasant.png", "forsaken/units/forsaken-peasant.png", fn_forsaken_peasant),
        ("human/units/peasant_with_gold.png", "forsaken/units/forsaken-peasant_with_gold.png", fn_forsaken_peasant),
        ("human/units/peasant_with_wood.png", "forsaken/units/forsaken-peasant_with_wood.png", fn_forsaken_peasant),
        ("human/units/knight.png", "forsaken/units/death_knight.png", fn_death_knight),
        ("human/units/catapult.png", "forsaken/units/meat_wagon.png", fn_meat_wagon),
        ("human/units/cleric.png", "forsaken/units/necromancer.png", fn_necromancer),
        ("human/units/conjurer.png", "forsaken/units/banshee.png", fn_banshee),
        ("human/units/archer.png", "forsaken/units/sylvanas.png", fn_sylvanas),
        ("neutral/units/daemon.png", "forsaken/units/varimathras.png", fn_sylvanas),
        ("neutral/units/dead_bodies.png", "forsaken/units/dead_body.png", fn_ghoul),
    ]
    for src, dst, fn in unit_map:
        src_path = os.path.join(GRAPHICS_DIR, src)
        dst_path = os.path.join(GRAPHICS_DIR, dst)
        if os.path.exists(src_path):
            im = Image.open(src_path)
            out = recolor_palette(im, fn)
            out.save(dst_path)
            print(f"Generated unit sprite: {dst}")

# --- Building Color Functions ---

def fn_forsaken_building(r, g, b):
    # Dark gothic slate stone with unholy purple runes and mossy green undertones
    lum = 0.299*r + 0.587*g + 0.114*b
    # If warm roof / wood / gold tones
    if r > b and lum > 60:
        return (lum * 0.55 + 25, lum * 0.4 + 10, lum * 0.75 + 40)
    # If stone
    return (lum * 0.7 + 10, lum * 0.7 + 15, lum * 0.85 + 25)

def generate_buildings():
    buildings = [
        "barracks.png", "barracks_construction.png",
        "blacksmith.png", "blacksmith_construction.png",
        "church.png", "church_construction.png",
        "farm.png", "farm_construction.png",
        "lumber_mill.png", "lumber_mill_construction.png",
        "stable.png", "stable_construction.png",
        "stormwind_keep.png",
        "tower.png", "tower_construction.png",
        "town_hall.png", "town_hall_construction.png",
    ]
    tilesets = ["forest", "swamp"]
    for ts in tilesets:
        src_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "human", "buildings")
        dst_dir = os.path.join(GRAPHICS_DIR, "tilesets", ts, "forsaken", "buildings")
        os.makedirs(dst_dir, exist_ok=True)
        for b in buildings:
            src_path = os.path.join(src_dir, b)
            dst_path = os.path.join(dst_dir, b)
            if os.path.exists(src_path):
                im = Image.open(src_path)
                out = recolor_palette(im, fn_forsaken_building)
                out.save(dst_path)
                print(f"Generated building [{ts}]: {b}")

# --- UI Color Functions ---

def fn_forsaken_ui(r, g, b):
    lum = 0.299*r + 0.587*g + 0.114*b
    # Dark purple/slate gothic UI frames
    if lum > 140:
        return (lum * 0.7 + 25, lum * 0.6 + 15, lum * 0.85 + 40)
    return (lum * 0.55 + 15, lum * 0.45 + 10, lum * 0.75 + 30)

def generate_ui():
    ui_files = [
        "minimap.png", "minimap_2.png",
        "left_panel.png", "right_panel.png",
        "bottom_panel.png", "top_resource_bar.png",
        "icon_border.png", "icon_selection_boxes.png",
        "briefing.png", "victory_1.png"
    ]
    src_dir = os.path.join(GRAPHICS_DIR, "ui", "human")
    dst_dir = os.path.join(GRAPHICS_DIR, "ui", "forsaken")
    for f in ui_files:
        src_path = os.path.join(src_dir, f)
        dst_path = os.path.join(dst_dir, f)
        if os.path.exists(src_path):
            im = Image.open(src_path)
            out = recolor_palette(im, fn_forsaken_ui)
            out.save(dst_path)
            print(f"Generated UI: {f}")
    
    # Also save top_resource_bar.png in contrib/graphics/ui/forsaken/
    contrib_dst = os.path.join(CONTRIB_DIR, "ui", "forsaken", "top_resource_bar.png")
    bar_src = os.path.join(dst_dir, "top_resource_bar.png")
    if os.path.exists(bar_src):
        im = Image.open(bar_src)
        im.save(contrib_dst)

# --- Icons Generation ---

def create_pixel_icon(name, bg_color, border_color, draw_fn):
    """Create a 27x19 pixel-art icon"""
    im = Image.new("RGBA", (27, 19), (0, 0, 0, 255))
    draw = ImageDraw.Draw(im)
    
    # Background
    draw.rectangle([0, 0, 26, 18], fill=bg_color)
    
    # Border
    draw.rectangle([0, 0, 26, 18], outline=border_color)
    
    # Custom pixel art
    draw_fn(draw)
    
    dst_path = os.path.join(CONTRIB_DIR, "ui", "forsaken", name)
    im.save(dst_path)
    # Also copy to graphics/ui/forsaken
    g_dst = os.path.join(GRAPHICS_DIR, "ui", "forsaken", name)
    im.save(g_dst)
    print(f"Generated Icon: {name}")

def draw_ghoul_icon(draw):
    # Ghoul silhouette: pale head, red eyes, sharp fangs
    draw.ellipse([8, 3, 18, 13], fill=(130, 160, 130)) # Pale green head
    draw.point([11, 7], fill=(240, 30, 30)) # Left red eye
    draw.point([15, 7], fill=(240, 30, 30)) # Right red eye
    # Vicious jaws / claws
    draw.line([10, 11, 16, 11], fill=(20, 20, 20), width=1)
    draw.point([11, 12], fill=(230, 230, 220)) # Fang
    draw.point([15, 12], fill=(230, 230, 220)) # Fang
    # Claws below
    draw.line([5, 15, 8, 13], fill=(210, 210, 200))
    draw.line([18, 13, 21, 15], fill=(210, 210, 200))

def draw_dark_ranger_icon(draw):
    # Dark hood with silver elven hair and red glowing eyes
    draw.polygon([(7, 15), (13, 2), (19, 15)], fill=(45, 20, 60)) # Hood
    draw.ellipse([10, 6, 16, 12], fill=(200, 210, 225)) # Pale face
    draw.point([12, 9], fill=(255, 40, 50)) # Crimson eye
    draw.point([14, 9], fill=(255, 40, 50)) # Crimson eye
    draw.line([8, 8, 9, 13], fill=(220, 225, 240)) # Silver hair locks
    draw.line([17, 8, 18, 13], fill=(220, 225, 240))
    # Bow curve on side
    draw.arc([19, 3, 24, 16], start=270, end=90, fill=(160, 140, 80))

def draw_peasant_icon(draw):
    # Hooded acolyte
    draw.polygon([(7, 16), (13, 3), (19, 16)], fill=(50, 45, 65))
    draw.ellipse([10, 7, 16, 13], fill=(150, 165, 155)) # Necrotic face
    draw.point([12, 10], fill=(220, 220, 120)) # Yellow eye
    draw.point([14, 10], fill=(220, 220, 120))
    # Pickaxe / shovel
    draw.line([4, 15, 9, 10], fill=(130, 100, 60))
    draw.line([8, 9, 10, 11], fill=(180, 180, 190))

def draw_death_knight_icon(draw):
    # Horned helm with glowing cyan eyes
    draw.polygon([(8, 14), (13, 3), (18, 14)], fill=(40, 45, 55)) # Helm
    draw.line([7, 3, 9, 7], fill=(160, 165, 175), width=1) # Horn left
    draw.line([19, 3, 17, 7], fill=(160, 165, 175), width=1) # Horn right
    draw.point([11, 8], fill=(40, 230, 230)) # Cyan eye
    draw.point([15, 8], fill=(40, 230, 230)) # Cyan eye
    draw.rectangle([11, 11, 15, 13], fill=(20, 25, 30)) # Visor grill

def draw_meat_wagon_icon(draw):
    # Spiked wooden catapult cart with skull
    draw.rectangle([5, 10, 21, 15], fill=(70, 50, 35))
    draw.ellipse([4, 13, 8, 17], fill=(30, 30, 30)) # Wheel
    draw.ellipse([18, 13, 22, 17], fill=(30, 30, 30)) # Wheel
    draw.line([13, 10, 8, 4], fill=(110, 80, 50), width=2) # Arm
    draw.ellipse([6, 3, 10, 7], fill=(220, 220, 200)) # Skull ammo
    draw.point([7, 4], fill=(10, 10, 10))
    draw.point([9, 4], fill=(10, 10, 10))

def draw_necromancer_icon(draw):
    # Cowl and skull staff
    draw.polygon([(8, 15), (13, 3), (18, 15)], fill=(60, 20, 75)) # Cowl
    draw.ellipse([11, 8, 15, 12], fill=(225, 225, 215)) # Skull face
    draw.point([12, 9], fill=(80, 240, 100)) # Green eye
    draw.point([14, 9], fill=(80, 240, 100))
    # Staff with green orb
    draw.line([21, 4, 21, 16], fill=(120, 100, 70))
    draw.ellipse([19, 2, 23, 6], fill=(50, 240, 120))

def draw_banshee_icon(draw):
    # Ghostly wailing apparition
    draw.ellipse([9, 3, 17, 11], fill=(140, 220, 230)) # Ghostly head
    draw.point([11, 6], fill=(20, 50, 70))
    draw.point([15, 6], fill=(20, 50, 70))
    draw.ellipse([12, 8, 14, 11], fill=(20, 50, 70)) # Wailing mouth
    # Ethereal trailing shroud
    draw.polygon([(9, 11), (13, 17), (17, 11)], fill=(100, 180, 210))

def draw_sylvanas_icon(draw):
    # Regal Dark Lady: elven cowl, silver hair, crimson eyes, golden circlet
    draw.polygon([(6, 16), (13, 2), (20, 16)], fill=(50, 15, 45))
    draw.ellipse([10, 6, 16, 12], fill=(210, 220, 235))
    draw.point([12, 9], fill=(255, 30, 30))
    draw.point([14, 9], fill=(255, 30, 30))
    draw.line([11, 5, 15, 5], fill=(240, 200, 60)) # Golden circlet
    draw.line([7, 8, 9, 14], fill=(235, 240, 255)) # Silver locks
    draw.line([17, 8, 19, 14], fill=(235, 240, 255))

def draw_necropolis_icon(draw):
    # Stepped dark citadel with purple crystal
    draw.rectangle([5, 10, 21, 16], fill=(50, 50, 65))
    draw.rectangle([8, 6, 18, 10], fill=(65, 65, 80))
    draw.polygon([(10, 6), (13, 2), (16, 6)], fill=(160, 50, 200)) # Purple crystal
    draw.rectangle([11, 12, 15, 16], fill=(15, 15, 20)) # Gate

def draw_ziggurat_icon(draw):
    # Tiered pyramid
    draw.polygon([(4, 16), (13, 4), (22, 16)], fill=(60, 55, 75))
    draw.polygon([(8, 11), (13, 4), (18, 11)], fill=(80, 75, 100))
    draw.polygon([(11, 6), (13, 2), (15, 6)], fill=(180, 60, 220))

def draw_crypt_icon(draw):
    # Mausoleum with iron arch
    draw.rectangle([5, 7, 21, 16], fill=(55, 55, 65))
    draw.polygon([(4, 7), (13, 2), (22, 7)], fill=(75, 75, 90))
    draw.arc([9, 9, 17, 16], start=180, end=0, fill=(180, 180, 190))
    draw.rectangle([10, 12, 16, 16], fill=(15, 15, 20))

def draw_graveyard_icon(draw):
    # Tombstone and bone fence
    draw.rectangle([6, 6, 12, 16], fill=(90, 90, 100)) # Tombstone
    draw.polygon([(6, 6), (9, 3), (12, 6)], fill=(90, 90, 100))
    draw.line([8, 7, 10, 7], fill=(30, 30, 35)) # Cross
    draw.line([9, 6, 9, 10], fill=(30, 30, 35))
    draw.line([14, 10, 22, 10], fill=(140, 130, 120)) # Fence
    draw.line([16, 8, 16, 15], fill=(180, 175, 160)) # Bones
    draw.line([20, 8, 20, 15], fill=(180, 175, 160))

def draw_apothecary_icon(draw):
    # Alembic / bubbling cauldron with plague green fumes
    draw.ellipse([8, 9, 18, 16], fill=(45, 45, 55)) # Pot
    draw.ellipse([9, 9, 17, 12], fill=(60, 230, 80)) # Green liquid
    draw.line([10, 6, 12, 4], fill=(70, 240, 100)) # Fume 1
    draw.line([14, 5, 16, 3], fill=(70, 240, 100)) # Fume 2

def draw_stables_icon(draw):
    # Skeletal horse skull over stall
    draw.rectangle([5, 8, 21, 16], fill=(60, 45, 35))
    draw.polygon([(4, 8), (13, 3), (22, 8)], fill=(80, 60, 45))
    draw.ellipse([11, 7, 15, 12], fill=(215, 215, 200)) # Skull
    draw.point([12, 9], fill=(20, 20, 20))
    draw.point([14, 9], fill=(20, 20, 20))

def draw_temple_icon(draw):
    # Gothic cathedral with violet stained glass
    draw.rectangle([6, 6, 20, 16], fill=(50, 45, 60))
    draw.polygon([(5, 6), (13, 1), (21, 6)], fill=(70, 60, 80))
    draw.arc([10, 8, 16, 14], start=180, end=0, fill=(200, 60, 240)) # Violet window

def draw_tower_icon(draw):
    # Spire with necrotic glowing sphere
    draw.polygon([(9, 16), (11, 5), (15, 5), (17, 16)], fill=(55, 55, 70))
    draw.ellipse([10, 1, 16, 7], fill=(180, 50, 220)) # Purple orb

def draw_claws_icon(draw, tier=1):
    # Bone / iron claws
    draw.line([7, 14, 11, 4], fill=(200, 200, 210), width=2)
    draw.line([13, 14, 13, 3], fill=(200, 200, 210), width=2)
    draw.line([19, 14, 15, 4], fill=(200, 200, 210), width=2)
    if tier == 2:
        draw.point([11, 4], fill=(60, 240, 90)) # Poison tip
        draw.point([13, 3], fill=(60, 240, 90))
        draw.point([15, 4], fill=(60, 240, 90))

def draw_carapace_icon(draw, tier=1):
    # Bone shield / necrotic carapace
    draw.polygon([(7, 4), (19, 4), (19, 11), (13, 16), (7, 11)], fill=(70, 70, 85))
    draw.line([13, 5, 13, 14], fill=(160, 50, 180), width=1)
    if tier == 2:
        draw.polygon([(9, 6), (17, 6), (17, 10), (13, 14), (9, 10)], outline=(80, 240, 120))

def draw_dark_arrow_icon(draw, tier=1):
    # Dark arrow with violet / shadow fletching
    draw.line([6, 13, 19, 5], fill=(140, 110, 80), width=1)
    draw.polygon([(18, 4), (22, 3), (20, 7)], fill=(60, 230, 100) if tier == 2 else (180, 60, 220))
    draw.line([5, 12, 7, 15], fill=(160, 50, 200))

def draw_steed_icon(draw, tier=1):
    # Skeletal horseshoe / steed
    draw.arc([7, 4, 19, 15], start=45, end=315, fill=(210, 210, 220), width=2)
    if tier == 2:
        draw.point([13, 9], fill=(60, 230, 230))

def generate_icons():
    dark_bg = (25, 20, 35)
    border = (80, 60, 110)
    
    icons_list = [
        ("icon-ghoul.png", draw_ghoul_icon),
        ("icon-dark-ranger.png", draw_dark_ranger_icon),
        ("icon-forsaken-peasant.png", draw_peasant_icon),
        ("icon-death-knight.png", draw_death_knight_icon),
        ("icon-meat-wagon.png", draw_meat_wagon_icon),
        ("icon-necromancer.png", draw_necromancer_icon),
        ("icon-banshee.png", draw_banshee_icon),
        ("icon-sylvanas.png", draw_sylvanas_icon),
        ("icon-varimathras.png", draw_death_knight_icon),
        
        ("icon-forsaken-town-hall.png", draw_necropolis_icon),
        ("icon-forsaken-farm.png", draw_ziggurat_icon),
        ("icon-forsaken-barracks.png", draw_crypt_icon),
        ("icon-forsaken-lumber-mill.png", draw_graveyard_icon),
        ("icon-forsaken-blacksmith.png", draw_apothecary_icon),
        ("icon-forsaken-stable.png", draw_stables_icon),
        ("icon-forsaken-church.png", draw_temple_icon),
        ("icon-forsaken-tower.png", draw_tower_icon),
        
        ("icon-claws1.png", lambda d: draw_claws_icon(d, 1)),
        ("icon-claws2.png", lambda d: draw_claws_icon(d, 2)),
        ("icon-carapace1.png", lambda d: draw_carapace_icon(d, 1)),
        ("icon-carapace2.png", lambda d: draw_carapace_icon(d, 2)),
        ("icon-dark-arrow1.png", lambda d: draw_dark_arrow_icon(d, 1)),
        ("icon-dark-arrow2.png", lambda d: draw_dark_arrow_icon(d, 2)),
        ("icon-skeletal-steed1.png", lambda d: draw_steed_icon(d, 1)),
        ("icon-skeletal-steed2.png", lambda d: draw_steed_icon(d, 2)),
        ("icon-move-forsaken.png", draw_peasant_icon),
    ]
    
    for name, fn in icons_list:
        create_pixel_icon(name, dark_bg, border, fn)

def main():
    print("Starting Forsaken Asset Generation...")
    ensure_dirs()
    generate_units()
    generate_buildings()
    generate_ui()
    generate_icons()
    print("All Forsaken Assets Generated Successfully!")

if __name__ == "__main__":
    main()
