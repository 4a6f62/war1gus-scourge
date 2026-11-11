#!/usr/bin/env python3
"""
Generate the full 12-mission Scourge Campaign (01 through 12) for War1gus,
and wire all 12 levels into campaigns/forsaken/campaign_titles.lua and scripts/campaigns.lua.
"""

import gzip
import os
import re
import shutil

BASE_DIR = "/home/smiles/forsaken-mod"
ORC_DIR = os.path.join(BASE_DIR, "campaigns", "orc")
HUM_DIR = os.path.join(BASE_DIR, "campaigns", "human")
OUT_DIR = os.path.join(BASE_DIR, "campaigns", "forsaken")
os.makedirs(OUT_DIR, exist_ok=True)

PLAYER0_UNIT_MAP = {
    "unit-orc-town-hall": "unit-forsaken-town-hall",
    "unit-human-town-hall": "unit-forsaken-town-hall",
    "unit-orc-farm": "unit-forsaken-farm",
    "unit-human-farm": "unit-forsaken-farm",
    "unit-orc-barracks": "unit-forsaken-barracks",
    "unit-human-barracks": "unit-forsaken-barracks",
    "unit-orc-lumber-mill": "unit-forsaken-lumber-mill",
    "unit-human-lumber-mill": "unit-forsaken-lumber-mill",
    "unit-orc-blacksmith": "unit-forsaken-blacksmith",
    "unit-human-blacksmith": "unit-forsaken-blacksmith",
    "unit-orc-kennel": "unit-forsaken-stable",
    "unit-human-stable": "unit-forsaken-stable",
    "unit-orc-temple": "unit-forsaken-church",
    "unit-human-church": "unit-forsaken-church",
    "unit-orc-tower": "unit-forsaken-tower",
    "unit-human-tower": "unit-forsaken-tower",
    "unit-orc-blackrock-spire": "unit-forsaken-stormwind-keep",
    "unit-human-stormwind-keep": "unit-forsaken-stormwind-keep",
    "unit-peon": "unit-acolyte",
    "unit-peasant": "unit-acolyte",
    "unit-grunt": "unit-ghoul",
    "unit-footman": "unit-ghoul",
    "unit-spearman": "unit-crypt-fiend",
    "unit-archer": "unit-crypt-fiend",
    "unit-raider": "unit-abomination",
    "unit-knight": "unit-abomination",
    "unit-orc-catapult": "unit-meat-wagon",
    "unit-human-catapult": "unit-meat-wagon",
    "unit-necrolyte": "unit-necromancer",
    "unit-cleric": "unit-necromancer",
    "unit-warlock": "unit-banshee",
    "unit-conjurer": "unit-banshee",
}


def convert_sms_for_scourge(src_sms_gz, mission_id, extra_p0_units=None, replace_p4_garona=False):
    with gzip.open(src_sms_gz, "rt") as f:
        text = f.read()

    text = re.sub(
        r'(Player\(0,\s*"type",\s*"person",\s*"race",\s*")(?:orc|human)(")',
        r'\1forsaken\2',
        text,
    )
    text = text.replace('LoadUI("orc"', 'LoadUI("forsaken"').replace('LoadUI("human"', 'LoadUI("forsaken"')

    def repl_p0(match):
        utype = match.group(1)
        rest = match.group(2)
        new_utype = PLAYER0_UNIT_MAP.get(utype, utype)
        return f'CreateUnit("{new_utype}", 0, {rest}'

    text = re.sub(r'CreateUnit\("([^"]+)",\s*0,\s*(\{[^\}]+\}\))', repl_p0, text)

    if replace_p4_garona:
        text = text.replace('CreateUnit("unit-garona", 4,', 'CreateUnit("unit-sylvanas", 4,')
        text = text.replace('CreateUnit("unit-peon", 4,', 'CreateUnit("unit-acolyte", 4,')

    if extra_p0_units:
        extra_lines = "\n".join(
            f'  unit = CreateUnit("{u}", 0, {{{x}, {y}}})' for (u, x, y) in extra_p0_units
        )
        text = text.replace("local PlaceUnits = function()\n", f"local PlaceUnits = function()\n{extra_lines}\n")

    if mission_id not in ["09", "11", "12"]:
        text = re.sub(
            r'Player\(2,\s*"type"\s*,\s*"computer".*?\)',
            'Player(2, "type", "nobody")',
            text,
            flags=re.DOTALL,
        )
    if mission_id != "12":
        text = re.sub(
            r'Player\(3,\s*"type"\s*,\s*"computer".*?\)',
            'Player(3, "type", "nobody")',
            text,
            flags=re.DOTALL,
        )
    if mission_id != "08":
        text = re.sub(
            r'Player\(4,\s*"type"\s*,\s*"rescue-passive".*?\)',
            'Player(4, "type", "nobody")',
            text,
            flags=re.DOTALL,
        )

    dst_sms = os.path.join(OUT_DIR, f"{mission_id}.sms")
    with open(dst_sms, "w") as f:
        f.write(text)


def build_mission(
    mission_id,
    src_race_dir,
    tileset_script,
    start_view,
    objective_str,
    intro_text,
    allowed_scourge_units,
    allowed_scourge_spells,
    victory_trigger_lua=None,
    defeat_trigger_lua=None,
    extra_c_sms_before_load="",
    extra_c_sms_after_load="",
    extra_p0_units=None,
    replace_p4_garona=False,
):
    p2_type = "computer" if mission_id in ["09", "11", "12"] else "nobody"
    p3_type = "computer" if mission_id == "12" else "nobody"
    p4_type = "rescue-passive" if mission_id == "08" else "nobody"

    ptypes = [
        '"person"', '"computer"', f'"{p2_type}"', f'"{p3_type}"', f'"{p4_type}"',
        '"nobody"', '"nobody"', '"nobody"', '"nobody"', '"nobody"',
        '"nobody"', '"nobody"', '"nobody"', '"nobody"', '"neutral"'
    ]
    ptypes_str = ", ".join(ptypes)

    with open(os.path.join(OUT_DIR, f"{mission_id}.smp"), "w") as f:
        f.write(
            f'StratagusMap()\n'
            f'DefinePlayerTypes({ptypes_str})\n'
            f'PresentMap("Scourge {mission_id}", 16, 64, 64, {int(mission_id)})\n'
            f'DefineMapSetup("campaigns/forsaken/{mission_id}_c.sms")\n'
        )

    prerun_dst = os.path.join(OUT_DIR, f"{mission_id}_prerun.lua")
    if not os.path.exists(prerun_dst):
        with open(prerun_dst, "w") as f:
            f.write(f"-- Prerun setup for Scourge mission {mission_id}\n")

    with open(os.path.join(OUT_DIR, f"{mission_id}_intro.txt"), "w") as f:
        f.write(intro_text.strip() + "\n")

    wav_dst = os.path.join(OUT_DIR, f"{mission_id}_intro.wav.gz")
    if not os.path.exists(wav_dst):
        shutil.copyfile(os.path.join(BASE_DIR, "sounds", "orc", "temple.wav.gz"), wav_dst)

    base_c2_path = os.path.join(src_race_dir, f"{mission_id}_c2.sms")
    with open(base_c2_path, "r") as f:
        base_c2 = f.read()

    c2_lines = [
        l for l in base_c2.splitlines()
        if not l.startswith("objectives")
        and not l.startswith("currentRace")
        and not l.startswith("currentState")
    ]

    scourge_c2 = [
        f'objectives = {{"{objective_str}"}}',
        "",
        "-- Base Human/Orc allowances for AI opponents",
        *c2_lines,
        "",
        "-- Scourge allowances for Player 0",
        'DefineAllowForsakenUnits("FFFFFFFFFFFFFFFF")',
    ]
    for u in allowed_scourge_units:
        scourge_c2.append(f'DefineAllow("{u}", "AAAAAAAAAAAAAAAA")')

    for upg in [
        "upgrade-claws1", "upgrade-claws2",
        "upgrade-carapace1", "upgrade-carapace2",
        "upgrade-dark-arrow1", "upgrade-dark-arrow2",
        "upgrade-skeletal-steed1", "upgrade-skeletal-steed2",
    ]:
        scourge_c2.append(f'DefineAllow("{upg}", "AAAAAAAAAAAAAAAA")')

    all_spells = [
        "upgrade-forsaken-raise-dead",
        "upgrade-forsaken-dark-vision",
        "upgrade-forsaken-unholy-armor",
        "upgrade-forsaken-spiders",
        "upgrade-forsaken-poison-cloud",
        "upgrade-forsaken-daemon",
    ]
    for sp in all_spells:
        mask = "AAAAAAAAAAAAAAAA" if sp in allowed_scourge_spells else "FFFFFFFFFFFFFFFF"
        scourge_c2.append(f'DefineAllow("{sp}", "{mask}")')

    scourge_c2.append('currentRace = "forsaken"')
    scourge_c2.append(f"currentState = {int(mission_id)}")

    with open(os.path.join(OUT_DIR, f"{mission_id}_c2.sms"), "w") as f:
        f.write("\n".join(scourge_c2) + "\n")

    if victory_trigger_lua is None:
        victory_trigger_lua = """AddTrigger(
  function() return (GetNumOpponents(GetThisPlayer()) == 0) end,
  function() return ActionVictory() end)"""

    if defeat_trigger_lua is None:
        defeat_trigger_lua = """AddTrigger(
  function() return (GetPlayerData(GetThisPlayer(), "TotalNumUnits") == 0) end,
  function() return ActionDefeat() end)"""

    c_sms_text = f"""Load("campaigns/forsaken/{mission_id}_c2.sms")
LoadTileModels("{tileset_script}")
{extra_c_sms_before_load}
Load("campaigns/forsaken/{mission_id}.sms")
{extra_c_sms_after_load}

{victory_trigger_lua}
{defeat_trigger_lua}

SetStartView(0, {start_view[0]}, {start_view[1]})
"""
    with open(os.path.join(OUT_DIR, f"{mission_id}_c.sms"), "w") as f:
        f.write(c_sms_text)

    if mission_id != "01":
        convert_sms_for_scourge(
            os.path.join(src_race_dir, f"{mission_id}.sms.gz"),
            mission_id,
            extra_p0_units=extra_p0_units,
            replace_p4_garona=replace_p4_garona,
        )
    else:
        sms_01 = os.path.join(OUT_DIR, "01.sms")
        if os.path.exists(sms_01):
            with open(sms_01, "r") as f:
                t01 = f.read()
            t01 = re.sub(r'Player\(2,\s*"type"\s*,\s*"computer".*?\)', 'Player(2, "type", "nobody")', t01, flags=re.DOTALL)
            t01 = re.sub(r'Player\(3,\s*"type"\s*,\s*"computer".*?\)', 'Player(3, "type", "nobody")', t01, flags=re.DOTALL)
            t01 = re.sub(r'Player\(4,\s*"type"\s*,\s*"rescue-passive".*?\)', 'Player(4, "type", "nobody")', t01, flags=re.DOTALL)
            with open(sms_01, "w") as f:
                f.write(t01)
    print(f"Built Scourge Mission {mission_id} successfully.")


def build_all_12_missions():
    tier1_units = [
        "unit-acolyte", "unit-ghoul",
        "unit-forsaken-farm", "unit-forsaken-barracks", "unit-forsaken-town-hall",
    ]
    tier2_units = tier1_units + ["unit-crypt-fiend", "unit-dark-ranger", "unit-forsaken-lumber-mill"]
    tier3_units = tier2_units + ["unit-abomination", "unit-death-knight", "unit-forsaken-blacksmith", "unit-forsaken-stable"]
    tier5_units = tier3_units + ["unit-meat-wagon", "unit-necromancer", "unit-forsaken-church"]
    tier7_units = tier5_units + ["unit-banshee", "unit-forsaken-tower", "unit-sylvanas", "unit-varimathras"]

    # Mission 01: Tirisfal Outpost
    build_mission(
        mission_id="01",
        src_race_dir=HUM_DIR,
        tileset_script="scripts/tilesets/forest_campaign.lua",
        start_view=(36, 19),
        objective_str="build:  4 ziggurats  1 crypt",
        intro_text="""The Lich King's dark will echoes across the northern lands! As the Undead Scourge marches forth to spread the plague of undeath, a new Necropolis must be established in the borderlands.

Acolytes, raise your ritual daggers and begin the unholy summoning rites. Harvest gold and timber, and construct no less than 4 Ziggurats and a Crypt to raise our legions of the Scourge.

Beware: hostile forces and feral beasts still prowl the forest. Rally your Ghouls, defend our Necropolis, and claim this land for the Scourge!""",
        allowed_scourge_units=tier1_units,
        allowed_scourge_spells=[],
        victory_trigger_lua="""AddTrigger(
  function() return (GetPlayerData(GetThisPlayer(), "UnitTypesCount", "unit-forsaken-farm") >= 4 and
                     GetPlayerData(GetThisPlayer(), "UnitTypesCount", "unit-forsaken-barracks") >= 1) end,
  function() return ActionVictory() end)""",
    )

    # Mission 02: Blightwater Marsh
    build_mission(
        mission_id="02",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/swamp_campaign.lua",
        start_view=(34, 18),
        objective_str="crush all human opposition",
        intro_text="""With our first Necropolis secured, the Scourge advances into the fetid reaches of Blightwater Marsh. Human scouting parties have established forward camps along the bog roads to halt our spread.

Raise a Graveyard to store harvested timber and unlock Crypt Fiends—chitinous nerubian warriors whose barbed webs ensnare the living from afar.

Sweep across the marshlands and leave no human defender standing!""",
        allowed_scourge_units=tier2_units,
        allowed_scourge_spells=[],
    )

    # Mission 03: Hearthglen Crossroads
    build_mission(
        mission_id="03",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/forest_campaign.lua",
        start_view=(0, 4),
        objective_str="raze the human stronghold",
        intro_text="""The human garrison at Hearthglen Crossroads has fortified a full town across the river to block the Scourge's march southward. Their Clerics and Footmen prepare a counteroffensive against our Necropolis.

Construct a Slaughterhouse to stitch together hulking Abominations and forge carapace armor, and raise a Sacrificial Pit to summon unholy reinforcements.

Cross the river, shatter their defenses, and raze their settlement to the ground!""",
        allowed_scourge_units=tier3_units,
        allowed_scourge_spells=[],
    )

    # Mission 04: Scholomance Catacombs (Dungeon Crawl)
    build_mission(
        mission_id="04",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/dungeon_campaign.lua",
        start_view=(37, 0),
        objective_str="purge the catacombs of all enemies",
        intro_text="""Beneath the ruined estate of Caer Darrow lie the ancient Scholomance Catacombs—a labyrinth teeming with brutish Ogres, subterranean Slimes, and a rogue cultist cabal that refuses to bow to the Lich King.

Lead an elite strike force of Ghouls, Dark Rangers, Death Knights, and Necromancers into the depths. Your Necromancers have mastered the Raise Dead ritual—use the corpses of slain foes to raise skeletal warriors as you advance!

Slay every creature and rebel inside the catacombs!""",
        allowed_scourge_units=tier3_units + ["unit-necromancer"],
        allowed_scourge_spells=["upgrade-forsaken-raise-dead", "upgrade-forsaken-dark-vision"],
    )

    # Mission 05: Sorrow Hill (Unlocks Temple of the Damned, Necromancer, Meat Wagon)
    build_mission(
        mission_id="05",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/swamp_campaign.lua",
        start_view=(37, 60),
        objective_str="crush the human fortifications",
        intro_text="""Emerging victorious from the catacombs of Scholomance, the cult of the Temple of the Damned now pledges its full necromantic power to our campaign at Sorrow Hill.

You may now construct the Temple of the Damned to train Necromancers and research Raise Dead and Dark Vision, as well as assemble bone-framed Meat Wagons at your Crypt to hurl diseased corpses from afar.

March north through the marshes of Sorrow Hill and annihilate the human fortifications!""",
        allowed_scourge_units=tier5_units,
        allowed_scourge_spells=["upgrade-forsaken-raise-dead", "upgrade-forsaken-dark-vision"],
    )

    # Mission 06: Stratholme Outskirts (Unlocks Unholy Armor)
    build_mission(
        mission_id="06",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/forest_campaign.lua",
        start_view=(26, 60),
        objective_str="destroy the stratholme defenders",
        intro_text="""The outer towns of Stratholme stand before us, guarded by heavily armored Human Knights and Conjurers. To break their lines, our Necromancers have uncovered the dark rite of Unholy Armor at the Temple of the Damned.

Build up your Necropolis, besiege the human settlements with Meat Wagons and Death Knights, and claim the outskirts of Stratholme for the Scourge!""",
        allowed_scourge_units=tier5_units,
        allowed_scourge_spells=[
            "upgrade-forsaken-raise-dead",
            "upgrade-forsaken-dark-vision",
            "upgrade-forsaken-unholy-armor",
        ],
    )

    # Mission 07: Plaguewood Bog (Unlocks Spirit Tower, Banshee, Summon Spiders)
    build_mission(
        mission_id="07",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/swamp_campaign.lua",
        start_view=(45, 50),
        objective_str="eradicate the rival warband",
        intro_text="""Deep within Plaguewood Bog, a rival warband challenges the supremacy of the Scourge. From the tormented spirits of the fallen, our Acolytes can now raise Spirit Towers to summon wailing Banshees.

Banshees hurl ethereal blasts and can call forth broods of venomous crypt spiders to overwhelm the living. Crush the enemy warband and expand the blight across Plaguewood!""",
        allowed_scourge_units=tier7_units,
        allowed_scourge_spells=[
            "upgrade-forsaken-raise-dead",
            "upgrade-forsaken-dark-vision",
            "upgrade-forsaken-unholy-armor",
            "upgrade-forsaken-spiders",
        ],
        extra_c_sms_after_load='SetPlayerData(1, "RaceName", "orc")',
    )

    # Mission 08: Dalaran Dungeons (Dungeon Rescue: Varimathras rescues Sylvanas & Acolytes!)
    m8_before = """local oldcu = CreateUnit
function CreateUnit(name, player, pos)
  if (name ~= "unit-archer" and player == 1) then
    return oldcu(name, player+1, pos)
  else
    return oldcu(name, player, pos)
  end
end"""
    m8_after = """CreateUnit = oldcu
unit = CreateUnit("unit-start-location", 0, {33, 61})"""
    m8_victory = """AddTrigger(
  function() return (GetPlayerData(4, "UnitTypesCount", "unit-sylvanas") == 0 and
                     IfRescuedNearUnit("this", ">=", 1, "unit-sylvanas", "unit-start-location")) end,
  function() return ActionVictory() end)"""
    m8_defeat = """AddTrigger(
  function() return (GetPlayerData(GetThisPlayer(), "TotalNumUnits") == 0 or
                     (GetPlayerData(4, "UnitTypesCount", "unit-sylvanas") == 0 and
                      GetPlayerData(GetThisPlayer(), "UnitTypesCount", "unit-sylvanas") == 0)) end,
  function() return ActionDefeat() end)"""
    build_mission(
        mission_id="08",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/dungeon_campaign.lua",
        start_view=(32, 60),
        objective_str="rescue sylvanas and return to the exit",
        intro_text="""Word has reached us that Lady Sylvanas Windrunner and a coven of Acolytes are held captive inside the arcane vaults beneath Dalaran, guarded by dungeon brigands, elemental wardens, and monstrous beasts.

The Dreadlord Varimathras personally leads a strike team of Death Knights, Ghouls, Dark Rangers, and Necromancers into the dungeon.

Carve a path to the northeast prison cell, free Lady Sylvanas, and escort her safely back to the dungeon entrance!""",
        allowed_scourge_units=tier7_units,
        allowed_scourge_spells=[
            "upgrade-forsaken-raise-dead",
            "upgrade-forsaken-dark-vision",
            "upgrade-forsaken-unholy-armor",
            "upgrade-forsaken-spiders",
            "upgrade-forsaken-poison-cloud",
        ],
        victory_trigger_lua=m8_victory,
        defeat_trigger_lua=m8_defeat,
        extra_c_sms_before_load=m8_before,
        extra_c_sms_after_load=m8_after,
        extra_p0_units=[("unit-varimathras", 33, 58)],
        replace_p4_garona=True,
    )

    # Mission 09: Weeping Mire (Unlocks Plague Cloud)
    build_mission(
        mission_id="09",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/swamp_campaign.lua",
        start_view=(48, 7),
        objective_str="conquer the weeping mire",
        intro_text="""With Lady Sylvanas freed from Dalaran, our Banshees and apothecaries have perfected the dreaded Plague Cloud—a choking miasma of undeath that melts enemy formations and structures alike.

Establish your Necropolis on the northern ridge of the Weeping Mire, research Plague Cloud at the Spirit Tower, and lay waste to the human armies below!""",
        allowed_scourge_units=tier7_units,
        allowed_scourge_spells=[
            "upgrade-forsaken-raise-dead",
            "upgrade-forsaken-dark-vision",
            "upgrade-forsaken-unholy-armor",
            "upgrade-forsaken-spiders",
            "upgrade-forsaken-poison-cloud",
        ],
    )

    # Mission 10: Silverpine Forest (Unlocks Summon Daemon — full Scourge tech tree)
    build_mission(
        mission_id="10",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/forest_campaign.lua",
        start_view=(35, 60),
        objective_str="annihilate the silverpine legions",
        intro_text="""The human commanders have marshaled their elite knights and mages in Silverpine Forest for a desperate stand. In answer, our Spirit Towers have unlocked the ultimate dark pact: Summon Daemon.

Every weapon, unit, and unholy spell of the Scourge is now at your disposal. Sweep northward through Silverpine Forest and crush all who oppose us!""",
        allowed_scourge_units=tier7_units,
        allowed_scourge_spells=[
            "upgrade-forsaken-raise-dead",
            "upgrade-forsaken-dark-vision",
            "upgrade-forsaken-unholy-armor",
            "upgrade-forsaken-spiders",
            "upgrade-forsaken-poison-cloud",
            "upgrade-forsaken-daemon",
        ],
    )

    # Mission 11: Tyr's Hand & Light's Hope (Sylvanas leads the assault)
    build_mission(
        mission_id="11",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/forest_campaign.lua",
        start_view=(10, 58),
        objective_str="raze tyr's hand and light's hope",
        intro_text="""Only the twin human citadels of Tyr's Hand and Light's Hope stand between the Scourge and the heart of the kingdom. Lady Sylvanas personally joins your vanguard at the southern Necropolis.

Withstand the dual human assaults, amass an unstoppable legion of Death Knights, Meat Wagons, Necromancers, and Banshees, and burn both towns to ash!""",
        allowed_scourge_units=tier7_units,
        allowed_scourge_spells=[
            "upgrade-forsaken-raise-dead",
            "upgrade-forsaken-dark-vision",
            "upgrade-forsaken-unholy-armor",
            "upgrade-forsaken-spiders",
            "upgrade-forsaken-poison-cloud",
            "upgrade-forsaken-daemon",
        ],
        extra_p0_units=[("unit-sylvanas", 12, 59)],
    )

    # Mission 12: Fall of Capital City (Final Siege with Sylvanas & Varimathras!)
    m12_before = """local oldcu = CreateUnit
function CreateUnit(name, player, pos)
  if (name == "unit-human-stormwind-keep") then
    pos[2] = pos[2] + 2
  end
  return oldcu(name, player, pos)
end"""
    m12_after = "CreateUnit = oldcu"
    build_mission(
        mission_id="12",
        src_race_dir=ORC_DIR,
        tileset_script="scripts/tilesets/forest_campaign.lua",
        start_view=(0, 15),
        objective_str="destroy the royal keep and all defenders",
        intro_text="""At long last, the grand walls of the Capital City rise before the legions of the Undead Scourge! Both Lady Sylvanas Windrunner and the Dreadlord Varimathras take the field alongside your army for the final reckoning.

Build a mighty Necropolis, unleash every dark spell and siege engine at your command, shatter the royal keep, and claim eternal dominion over the realm!""",
        allowed_scourge_units=tier7_units,
        allowed_scourge_spells=[
            "upgrade-forsaken-raise-dead",
            "upgrade-forsaken-dark-vision",
            "upgrade-forsaken-unholy-armor",
            "upgrade-forsaken-spiders",
            "upgrade-forsaken-poison-cloud",
            "upgrade-forsaken-daemon",
        ],
        extra_c_sms_before_load=m12_before,
        extra_c_sms_after_load=m12_after,
        extra_p0_units=[("unit-sylvanas", 5, 17), ("unit-varimathras", 5, 19)],
    )

    # Update campaign_titles.lua with all 12 Scourge missions
    with open(os.path.join(OUT_DIR, "campaign_titles.lua"), "w") as f:
        f.write(
            'campaign_titles = {\n'
            '   "I. Tirisfal Outpost",\n'
            '   "II. Blightwater Marsh",\n'
            '   "III. Hearthglen",\n'
            '   "IV. Scholomance",\n'
            '   "V. Sorrow Hill",\n'
            '   "VI. Stratholme",\n'
            '   "VII. Plaguewood Bog",\n'
            '   "VIII. Dalaran Vaults",\n'
            '   "IX. Weeping Mire",\n'
            '   "X. Silverpine Forest",\n'
            '   "XI. Tyr\'s Hand",\n'
            '   "XII. Capital City",\n'
            '   "Ending"\n'
            '}\n'
        )
    print("All 12 Scourge Campaign missions generated successfully!")


if __name__ == "__main__":
    build_all_12_missions()
