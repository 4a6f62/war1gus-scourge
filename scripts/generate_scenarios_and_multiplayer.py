#!/usr/bin/env python3
"""
Generate custom Scourge Single-Player Scenarios & Multiplayer Skirmish Maps in maps/:
1. Scourge_Invasion(2).smp/.sms/.png: 2-Player Forest Scenario (Scourge vs Human with bases)
2. Blight_of_Black_Morass(2).smp/.sms/.png: 2-Player Swamp Scenario (Scourge vs Orc with bases)
3. War_of_Three_Races(4).smp/.sms/.png: 4-Player Forest Multiplayer/Skirmish (Scourge, Human, Orc, Scourge)
4. Plague_of_Lordaeron(4).smp/.sms/.png: 4-Player Swamp Multiplayer/Scenario with bases
"""

import gzip
import os
import shutil

BASE_DIR = "/home/smiles/forsaken-mod"
MAPS_DIR = os.path.join(BASE_DIR, "maps")


def extract_set_tiles(gz_path):
    with gzip.open(gz_path, "rt") as f:
        return [l for l in f.read().splitlines() if l.startswith("SetTile")]


def write_map_pair(base_name, description, num_players, tileset_lua, tile_lines, player_specs, unit_lines, road_coords=None):
    smp_path = os.path.join(MAPS_DIR, f"{base_name}.smp")
    sms_path = os.path.join(MAPS_DIR, f"{base_name}.sms")
    png_path = os.path.join(MAPS_DIR, f"{base_name}.png")

    ptypes = ", ".join('"person"' for _ in range(num_players))
    with open(smp_path, "w") as f:
        f.write(
            f'-- Stratagus Map Presentation\n'
            f'DefinePlayerTypes({ptypes})\n'
            f'PresentMap("{description}", {num_players}, 64, 64, 1)\n'
        )

    sms = [
        "-- Stratagus Map Setup",
        f'LoadTileModels("{tileset_lua}")',
    ]
    for p_idx, race, sx, sy, gold, wood in player_specs:
        sms.extend([
            f'Player({p_idx}, "ai-name", "wc1-land-attack")',
            f"SetStartView({p_idx}, {sx}, {sy})",
            f'SetPlayerData({p_idx}, "Resources", "gold", {gold})',
            f'SetPlayerData({p_idx}, "Resources", "wood", {wood})',
            f'SetPlayerData({p_idx}, "Resources", "lumber", 0)',
            f'SetAiType({p_idx}, "wc1-land-attack")',
            f'SetPlayerData({p_idx}, "RaceName", "{race}")',
        ])
    sms.extend([
        'SetPlayerData(15, "RaceName", "neutral")',
        "",
        *tile_lines,
        "",
        "if (MapUnitsInit ~= nil) then MapUnitsInit() end",
        *unit_lines,
    ])
    if road_coords:
        sms.append("CreateRoads({")
        for p_idx, rx, ry in road_coords:
            sms.append(f"  {{player = {p_idx}, x = {rx}, y = {ry}}},")
        sms.append("})")

    with open(sms_path, "w") as f:
        f.write("\n".join(sms) + "\n")

    src_png = os.path.join(MAPS_DIR, "RushHour(4).png")
    if os.path.exists(src_png):
        shutil.copyfile(src_png, png_path)
    print(f"Generated Scenario / Multiplayer map: {base_name} ({len(tile_lines)} tiles)")


def base_roads_around(p_idx, tx, ty):
    """Generate a perimeter road ring around a 3x3 Town Hall/Necropolis at (tx, ty)."""
    coords = []
    for dx in range(-1, 4):
        coords.append((p_idx, tx + dx, ty - 1))
        coords.append((p_idx, tx + dx, ty + 3))
    for dy in range(0, 3):
        coords.append((p_idx, tx - 1, ty + dy))
        coords.append((p_idx, tx + 3, ty + dy))
    return coords


def main():
    forest_tiles = extract_set_tiles(os.path.join(MAPS_DIR, "forest1.sms.gz"))
    swamp_tiles = extract_set_tiles(os.path.join(MAPS_DIR, "swamp1.sms.gz"))

    mines_4 = [
        'unit = CreateUnit("unit-gold-mine", 15, {16, 16})',
        "SetResourcesHeld(unit, 45000)",
        'unit = CreateUnit("unit-gold-mine", 15, {16, 48})',
        "SetResourcesHeld(unit, 45000)",
        'unit = CreateUnit("unit-gold-mine", 15, {48, 16})',
        "SetResourcesHeld(unit, 45000)",
        'unit = CreateUnit("unit-gold-mine", 15, {48, 48})',
        "SetResourcesHeld(unit, 45000)",
    ]

    # 1. Scourge_Invasion(2): 2-Player Forest Scenario (Scourge vs Human with starting bases)
    write_map_pair(
        base_name="Scourge_Invasion(2)",
        description="Scourge Invasion (Scourge vs Human)",
        num_players=2,
        tileset_lua="scripts/tilesets/forest_campaign.lua",
        tile_lines=forest_tiles,
        player_specs=[
            (0, "forsaken", 12, 12, 5000, 2500),
            (1, "human", 44, 44, 5000, 2500),
        ],
        unit_lines=mines_4 + [
            'unit = CreateUnit("unit-forsaken-town-hall", 0, {11, 15})',
            'unit = CreateUnit("unit-forsaken-farm", 0, {11, 12})',
            'unit = CreateUnit("unit-acolyte", 0, {14, 16})',
            'unit = CreateUnit("unit-acolyte", 0, {14, 17})',
            'unit = CreateUnit("unit-ghoul", 0, {15, 14})',
            'unit = CreateUnit("unit-ghoul", 0, {15, 18})',
            'unit = CreateUnit("unit-human-town-hall", 1, {43, 47})',
            'unit = CreateUnit("unit-human-farm", 1, {43, 44})',
            'unit = CreateUnit("unit-peasant", 1, {46, 48})',
            'unit = CreateUnit("unit-peasant", 1, {46, 49})',
            'unit = CreateUnit("unit-footman", 1, {42, 47})',
            'unit = CreateUnit("unit-footman", 1, {42, 50})',
        ],
        road_coords=base_roads_around(0, 11, 15) + base_roads_around(1, 43, 47),
    )

    # 2. Blight_of_Black_Morass(2): 2-Player Swamp Scenario (Scourge vs Orc with starting bases)
    write_map_pair(
        base_name="Blight_of_Black_Morass(2)",
        description="Blight of Black Morass (Scourge vs Orc)",
        num_players=2,
        tileset_lua="scripts/tilesets/swamp_campaign.lua",
        tile_lines=swamp_tiles,
        player_specs=[
            (0, "forsaken", 12, 12, 5000, 2500),
            (1, "orc", 44, 44, 5000, 2500),
        ],
        unit_lines=mines_4 + [
            'unit = CreateUnit("unit-forsaken-town-hall", 0, {11, 15})',
            'unit = CreateUnit("unit-forsaken-farm", 0, {11, 12})',
            'unit = CreateUnit("unit-acolyte", 0, {14, 16})',
            'unit = CreateUnit("unit-acolyte", 0, {14, 17})',
            'unit = CreateUnit("unit-ghoul", 0, {15, 14})',
            'unit = CreateUnit("unit-ghoul", 0, {15, 18})',
            'unit = CreateUnit("unit-orc-town-hall", 1, {43, 47})',
            'unit = CreateUnit("unit-orc-farm", 1, {43, 44})',
            'unit = CreateUnit("unit-peon", 1, {46, 48})',
            'unit = CreateUnit("unit-peon", 1, {46, 49})',
            'unit = CreateUnit("unit-grunt", 1, {42, 47})',
            'unit = CreateUnit("unit-grunt", 1, {42, 50})',
        ],
        road_coords=base_roads_around(0, 11, 15) + base_roads_around(1, 43, 47),
    )

    # 3. War_of_Three_Races(4): 4-Player Classic Melee / Multiplayer (Scourge, Human, Orc, Scourge)
    write_map_pair(
        base_name="War_of_Three_Races(4)",
        description="War of Three Races (Scourge, Human, Orc)",
        num_players=4,
        tileset_lua="scripts/tilesets/forest_campaign.lua",
        tile_lines=forest_tiles,
        player_specs=[
            (0, "forsaken", 16, 16, 10000, 3000),
            (1, "human", 48, 48, 10000, 3000),
            (2, "orc", 16, 48, 10000, 3000),
            (3, "forsaken", 48, 16, 10000, 3000),
        ],
        unit_lines=mines_4 + [
            'unit = CreateUnit("unit-acolyte", 0, {15, 15})',
            'unit = CreateUnit("unit-peasant", 1, {47, 47})',
            'unit = CreateUnit("unit-peon", 2, {15, 47})',
            'unit = CreateUnit("unit-acolyte", 3, {47, 15})',
        ],
    )

    # 4. Plague_of_Lordaeron(4): 4-Player Swamp Multiplayer / Scenario with Full Bases
    write_map_pair(
        base_name="Plague_of_Lordaeron(4)",
        description="Plague of Lordaeron (4P Bases)",
        num_players=4,
        tileset_lua="scripts/tilesets/swamp_campaign.lua",
        tile_lines=swamp_tiles,
        player_specs=[
            (0, "forsaken", 12, 12, 6000, 3000),
            (1, "human", 44, 44, 6000, 3000),
            (2, "orc", 12, 44, 6000, 3000),
            (3, "forsaken", 44, 12, 6000, 3000),
        ],
        unit_lines=mines_4 + [
            'unit = CreateUnit("unit-forsaken-town-hall", 0, {11, 15})',
            'unit = CreateUnit("unit-forsaken-farm", 0, {11, 12})',
            'unit = CreateUnit("unit-acolyte", 0, {14, 16})',
            'unit = CreateUnit("unit-ghoul", 0, {15, 15})',
            'unit = CreateUnit("unit-human-town-hall", 1, {43, 47})',
            'unit = CreateUnit("unit-human-farm", 1, {43, 44})',
            'unit = CreateUnit("unit-peasant", 1, {46, 48})',
            'unit = CreateUnit("unit-footman", 1, {42, 47})',
            'unit = CreateUnit("unit-orc-town-hall", 2, {11, 47})',
            'unit = CreateUnit("unit-orc-farm", 2, {11, 44})',
            'unit = CreateUnit("unit-peon", 2, {14, 48})',
            'unit = CreateUnit("unit-grunt", 2, {15, 47})',
            'unit = CreateUnit("unit-forsaken-town-hall", 3, {43, 15})',
            'unit = CreateUnit("unit-forsaken-farm", 3, {43, 12})',
            'unit = CreateUnit("unit-acolyte", 3, {46, 16})',
            'unit = CreateUnit("unit-ghoul", 3, {42, 15})',
        ],
        road_coords=(
            base_roads_around(0, 11, 15)
            + base_roads_around(1, 43, 47)
            + base_roads_around(2, 11, 47)
            + base_roads_around(3, 43, 15)
        ),
    )


if __name__ == "__main__":
    main()
