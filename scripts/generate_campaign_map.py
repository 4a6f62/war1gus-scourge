#!/usr/bin/env python3
"""
Generate Forsaken Campaign Mission 1: Tirisfal Awakening
"""

import gzip
import os

CAMPAIGN_DIR = "/home/smiles/forsaken-mod/campaigns/forsaken"
os.makedirs(CAMPAIGN_DIR, exist_ok=True)

# 1. campaign_titles.lua
with open(os.path.join(CAMPAIGN_DIR, "campaign_titles.lua"), "w") as f:
    f.write('''campaign_titles = {
   "I. Tirisfal Awakening",
   "Ending"
}
''')

# 2. 01_intro.txt
with open(os.path.join(CAMPAIGN_DIR, "01_intro.txt"), "w") as f:
    f.write('''The Scourge's telepathic grip has fractured! Under the command of Lady Sylvanas Windrunner, we have reclaimed our free will and cast off the Lich King's tyranny.

Now we must carve out our own sanctuary among the blighted groves of Tirisfal. Acolytes, raise your sickles and begin the unholy rites. Construct no less than 4 Ziggurats and a Crypt to house our growing brotherhood of the Forsaken.

Beware: hostile Scourge stragglers and feral beasts still haunt the wilderness. Rally your Ghouls, protect our fledgling settlement, and secure our future!''')

# 3. ending_1.txt
with open(os.path.join(CAMPAIGN_DIR, "ending_1.txt"), "w") as f:
    f.write('''VICTORY FOR THE FORSAKEN!

The first bastion of our new nation stands proud against the shadows. With the Ziggurats erected and the Crypt consecrated, scores of newly awakened undead flock to Lady Sylvanas's banner.

No longer mind-controlled pawns of the Scourge nor hunted vermin of humanity, we are the Forsaken—and Lordaeron shall be ours!''')

# 4. 01_c2.sms
with open(os.path.join(CAMPAIGN_DIR, "01_c2.sms"), "w") as f:
    f.write('''objectives = {"build:  4 ziggurats  1 crypt"}

-- Allowed units
DefineAllowHumanUnits("FFFFFFFFFFFFFFFF")
DefineAllowOrcUnits("FFFFFFFFFFFFFFFF")
DefineAllowForsakenUnits("FFFFFFFFFFFFFFFF")

DefineAllow("unit-ghoul", "AAAAAAAAAAAAAAAA")
DefineAllow("unit-acolyte", "AAAAAAAAAAAAAAAA")
DefineAllow("unit-forsaken-farm", "AAAAAAAAAAAAAAAA")
DefineAllow("unit-forsaken-barracks", "AAAAAAAAAAAAAAAA")
DefineAllow("unit-forsaken-town-hall", "AAAAAAAAAAAAAAAA")

-- Researched upgrades and spells
DefineAllow("upgrade-claws1", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-claws2", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-carapace1", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-carapace2", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-dark-arrow1", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-dark-arrow2", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-skeletal-steed1", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-skeletal-steed2", "AAAAAAAAAAAAAAAA")
DefineAllow("upgrade-forsaken-raise-dead", "FFFFFFFFFFFFFFFF")
DefineAllow("upgrade-forsaken-dark-vision", "FFFFFFFFFFFFFFFF")
DefineAllow("upgrade-forsaken-unholy-armor", "FFFFFFFFFFFFFFFF")
DefineAllow("upgrade-forsaken-spiders", "FFFFFFFFFFFFFFFF")
DefineAllow("upgrade-forsaken-poison-cloud", "FFFFFFFFFFFFFFFF")
DefineAllow("upgrade-forsaken-daemon", "FFFFFFFFFFFFFFFF")

currentRace = "forsaken"
currentState = 1
''')

# 5. 01_c.sms
with open(os.path.join(CAMPAIGN_DIR, "01_c.sms"), "w") as f:
    f.write('''LoadTileModels("scripts/tilesets/forest_campaign.lua")
Load("campaigns/forsaken/01_c2.sms")
Load("campaigns/forsaken/01.sms")

AddTrigger(
  function() return (GetPlayerData(GetThisPlayer(), "UnitTypesCount", "unit-forsaken-farm") >= 4 and GetPlayerData(GetThisPlayer(), "UnitTypesCount", "unit-forsaken-barracks") >= 1) end,
  function() return ActionVictory() end)
AddTrigger(
  function() return (GetPlayerData(GetThisPlayer(), "TotalNumUnits") == 0) end,
  function() return ActionDefeat() end)

SetStartView(0, 45, 22)
SetPlayerData(0, "Resources", "gold", 1000)
SetPlayerData(0, "Resources", "wood", 400)
''')

# 6. 01.smp
with open(os.path.join(CAMPAIGN_DIR, "01.smp"), "w") as f:
    f.write('''-- Stratagus Map Presentation
DefinePlayerTypes("person", "computer", "computer", "computer", "neutral", "nobody", "nobody", "nobody", "nobody", "nobody", "nobody", "nobody", "nobody", "nobody", "neutral")
PresentMap("Tirisfal Awakening", 16, 64, 64, 1)
DefineMapSetup("campaigns/forsaken/01_c.sms")
''')

# 7. 01.sms: Load terrain from human 01.sms.gz but configure for Forsaken
with gzip.open("/home/smiles/forsaken-mod/campaigns/human/01.sms.gz", "rt") as f:
    lines = f.readlines()

new_lines = []
# Replace player 0 setup
new_lines.append('''Player(0,
             "type", "person",
             "race", "forsaken",
             "color", { 158, 66, 178 })
Player(1,
            "type","computer",
            "race", "orc",
            "ai-name", "camp01",
            "color", { 255, 0, 0 },
            "resources", {"gold", 2000, "wood", 2000})
Player(2,
            "type","computer",
            "race", "orc",
            "ai-name", "camp01",
            "color", { 255, 0, 0 },
            "resources", {"gold", 2000, "wood", 2000})
Player(3,
            "type","computer",
            "race", "orc",
            "ai-name", "camp01",
            "color", { 255, 0, 0 },
            "resources", {"gold", 2000, "wood", 2000})
Player(4,
             "type", "rescue-passive",
             "race", "neutral",
             "ai-name", "rescue-passive",
             "color", { 200, 200, 200 },
             "allied", "+")
Player(5, "type","nobody")
Player(6, "type","nobody")
Player(7, "type","nobody")
Player(8, "type","nobody")
Player(9, "type","nobody")
Player(10, "type","nobody")
Player(11, "type","nobody")
Player(12, "type","nobody")
Player(13, "type","nobody")
Player(15,
             "race", "neutral",
             "color", { 100, 100, 100 })
LoadUI("forsaken", Video.Width, Video.Height)

-- Resources
SetPlayerData(0, "Resources", "wood", 400)
SetPlayerData(0, "Resources", "gold", 1000)
''')

# Extract all SetTile lines across all 64 rows
tile_lines = [line for line in lines if line.startswith("SetTile")]

new_lines.extend(tile_lines)

# Custom Forsaken starting units & roads
new_lines.append('''
if (MapUnitsInit ~= nil) then MapUnitsInit() end
local PlaceUnits = function()
  unit = CreateUnit("unit-gold-mine", 15, {49, 20})
  SetResourcesHeld(unit, 3000)
  unit = CreateUnit("unit-gold-mine", 15, {14, 8})
  SetResourcesHeld(unit, 10000)
  unit = CreateUnit("unit-gold-mine", 15, {22, 37})
  SetResourcesHeld(unit, 10000)
  unit = CreateUnit("unit-gold-mine", 15, {50, 50})
  SetResourcesHeld(unit, 10000)
  -- Player 0 Forsaken base
  unit = CreateUnit("unit-forsaken-town-hall", 0, {41, 22})
  unit = CreateUnit("unit-forsaken-farm", 0, {41, 19})
  unit = CreateUnit("unit-ghoul", 0, {40, 18})
  unit = CreateUnit("unit-ghoul", 0, {39, 24})
  unit = CreateUnit("unit-ghoul", 0, {45, 21})
  unit = CreateUnit("unit-acolyte", 0, {41, 21})
  -- Hostile Scourge stragglers
  unit = CreateUnit("unit-grunt", 1, {35, 10})
  unit = CreateUnit("unit-grunt", 1, {22, 20})
  unit = CreateUnit("unit-grunt", 1, {56, 31})
  unit = CreateUnit("unit-grunt", 1, {27, 36})
  unit = CreateUnit("unit-grunt", 1, {44, 49})
  unit = CreateUnit("unit-spearman", 1, {46, 50})
  unit = CreateUnit("unit-spearman", 1, {15, 55})
  unit = CreateUnit("unit-spearman", 1, {6, 10})
end
CreateRoads({
{player = 0, x = 40, y = 21},
{player = 0, x = 41, y = 21},
{player = 0, x = 42, y = 21},
{player = 0, x = 43, y = 21},
{player = 0, x = 44, y = 21},
{player = 0, x = 40, y = 18},
{player = 0, x = 40, y = 19},
{player = 0, x = 40, y = 20},
{player = 0, x = 40, y = 21},
{player = 0, x = 40, y = 22},
{player = 0, x = 40, y = 23},
{player = 0, x = 40, y = 24},
})
CreateWalls({
})
PlaceUnits()
''')

with open(os.path.join(CAMPAIGN_DIR, "01.sms"), "w") as f:
    f.writelines(new_lines)

print("Forsaken Campaign Mission 1 generated successfully!")
