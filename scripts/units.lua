--       _________ __                 __                               
--      /   _____//  |_____________ _/  |______     ____  __ __  ______
--      \_____  \\   __\_  __ \__  \\   __\__  \   / ___\|  |  \/  ___/
--      /        \|  |  |  | \// __ \|  |  / __ \_/ /_/  >  |  /\___ \ 
--     /_______  /|__|  |__|  (____  /__| (____  /\___  /|____//____  >
--             \/                  \/          \//_____/            \/ 
--  ______________________                           ______________________
--                        T H E   W A R   B E G I N S
--         Stratagus - A free fantasy real time strategy game engine
--
--      units.lua - Define the used unit-types.
--
--      (c) Copyright 1998-2004 by Lutz Sammer and Jimmy Salmon
--
--      This program is free software; you can redistribute it and/or modify
--      it under the terms of the GNU General Public License as published by
--      the Free Software Foundation; either version 2 of the License, or
--      (at your option) any later version.
--  
--      This program is distributed in the hope that it will be useful,
--      but WITHOUT ANY WARRANTY; without even the implied warranty of
--      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--      GNU General Public License for more details.
--  
--      You should have received a copy of the GNU General Public License
--      along with this program; if not, write to the Free Software
--      Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
--
--      $Id$

--=============================================================================
--      Define unit-types.
--

local units = {
   {Names = {neutral = "Brigand"},
    HitPoints = 40,
    Armor = 4,
    PiercingDamage = 1,
    BasicDamage = 9},
   {Names = {neutral = "Daemon"},
    Size = {neutral = {48, 48}},
    HitPoints = 300,
    Armor = 0,
    BasicDamage = 65,
    organic = false},
   {Names = {neutral = "Fire elemental"},
    Size = {neutral = {48, 48}},
    HitPoints = 200,
    Armor = 0,
    Speed = 5,
    BasicDamage = 40,
    Missile = "missile-catapult-rock",
    organic = false},
   {Names = {neutral = "Water elemental"},
    Size = {neutral = {48, 48}},
    HitPoints = 250,
    Armor = 0,
    Speed = 5,
    PiercingDamage = 40,
    BasicDamage = 0,
    MaxAttackRange = 3,
    Missile = "missile-water",
    organic = false},
   {Names = {orc = "Grizelda"},
    Image = {"file", "neutral/units/grizelda,garona.png", "size", {32, 32}},
    HitPoints = 30,
    Armor = 0,
    BasicDamage = 0,
    Coward = true},
   {Names = {orc = "Garona"},
    Image = {"file", "neutral/units/grizelda,garona.png", "size", {32, 32}},
    HitPoints = 30,
    Armor = 0,
    BasicDamage = 0,
    Coward = true},
   {Names = {neutral = "Ogre"},
    HitPoints = 60,
    Armor = 3,
    PiercingDamage = 1,
    BasicDamage = 12,
    Size = {neutral = {48, 48}}},
   {Names = {neutral = "Scorpion"},
    HitPoints = 30,
    Speed = 5,
    Armor = 0,
    PiercingDamage = 3,
    BasicDamage = 0,
    CanCastSpell = {
       neutral = {"spell-poison"},
       },
    organic = false},
   {Names = {neutral = "Skeleton"}, -- "Dungeon Skeleton"
    HitPoints = 30,
    Armor = 2,
    PiercingDamage = 1,
    BasicDamage = 9,
    organic = false},
   {Names = {neutral = "Slime"},
    HitPoints = 150,
    Armor = 10,
    Speed = 2,
    PiercingDamage = 1,
    BasicDamage = 0,
    organic = false},
   {Names = {neutral = "Spider"},
    HitPoints = 30,
    Armor = 0,
    Speed = 5,
    PiercingDamage = 1,
    BasicDamage = 3,
    CanCastSpell = {
       neutral = {"spell-slow" },
       },	
    organic = false},
   {Names = {neutral = "The dead"}, -- "Orc conjured skeleton"
    HitPoints = 40,
    Armor = 1,
    PiercingDamage = 1,
    BasicDamage = 4,
    organic = false},
   {Names = {neutral = "Wounded"},
    HitPoints = 60,
    Corpse = nil},

   {Names = {orc = "Peon", human = "Peasant", forsaken = "Acolyte"},
    Costs = {"time", 75, "gold", 400},
    HitPoints = 40,
    CanAttack = false,
    Coward = true,
    AnnoyComputerFactor = 100,
    Armor = 0,
    RightMouseAction = "harvest",
    RepairRange = 1,
    Sounds = {
       forsaken = {
          "selected", "acolyte-selected-group",
          "acknowledge", "acolyte-acknowledge",
          "ready", "acolyte-ready",
          "help", "forsaken help 3",
          "dead", "acolyte-dead",
          "attack", "acolyte-acknowledge",
       }
    },
    CanGatherResources = {
       {"resource-id", "gold",
        "resource-capacity", 100,
        "wait-at-resource", 300,
        "wait-at-depot", 150},
       {"resource-id", "wood",
        "resource-capacity", 100,
        "resource-step", 2,
        "wait-at-resource", 24,
        "wait-at-depot", 150,
        --"lose-resources",
        "terrain-harvester"},
       {"resource-id", "lumber", -- dungeon's harvest wood outside
        "resource-capacity", 100,
        "wait-at-resource", 1200,
        "wait-at-depot", 150,
        "final-resource", "wood"},
       {"resource-id", "treasure", -- dungeon's have treasure chests to plunder
        "resource-capacity", 100,
        "resource-step", 2,
        "wait-at-resource", 8,
        "wait-at-depot", 150,
        "terrain-harvester",
        "final-resource", "gold"},
      }},
   {Names = {orc = "Grunt", human = "Footman", forsaken = "Ghoul"},
    Costs = {"time", 60, "gold", 400},
    HitPoints = 60,
    Armor = 2,
    AnnoyComputerFactor = 80,
    PiercingDamage = 1,
    BasicDamage = 9,
    Size = {human = {48, 48}},
    Sounds = {
       forsaken = {
          "selected", "ghoul-selected-group",
          "acknowledge", "ghoul-acknowledge",
          "ready", "ghoul-ready",
          "help", "forsaken help 3",
          "dead", "ghoul-dead",
          "attack", "ghoul-acknowledge",
       }
    }},
   {Names = {orc = "Spearman", human = "Archer", forsaken = "Crypt fiend"},
    Costs = {"time", 70, "gold", 450, "wood", 50},
    HitPoints = 60,
    Armor = 1,
	AnnoyComputerFactor = 140,
    PiercingDamage = {orc = 5, human = 4, forsaken = 5},
    BasicDamage = 0,
    Missile = {orc = "missile-arrow", human = "missile-arrow", forsaken = "missile-web"},
    MaxAttackRange = {human = 5, orc = 4, forsaken = 5},
    Dependencies = {orc = {"lumber-mill"}, human = {"lumber-mill"}, forsaken = {"lumber-mill"}},
    Sounds = {
       forsaken = {
          "selected", "crypt-fiend-selected-group",
          "acknowledge", "crypt-fiend-acknowledge",
          "ready", "crypt-fiend-ready",
          "help", "forsaken help 3",
          "dead", "crypt-fiend-dead",
          "attack", "crypt-fiend-acknowledge",
       }
    }},
   {Names = {orc = "Catapult", human = "Catapult", forsaken = "Meat wagon"},
    Costs = {"time", 100, "gold", 900, "wood", 200},
    HitPoints = 120,
    Speed = 2,
    BasicDamage = 255,
	AnnoyComputerFactor = 160,
    MaxAttackRange = 8,
    Armor = 0,
    organic = false,
    Missile = "missile-catapult-rock",
    Dependencies = {orc = {"blacksmith", "lumber-mill"},
                    human = {"blacksmith", "lumber-mill"},
                    forsaken = {"blacksmith", "lumber-mill"}},
    Sounds = {
       forsaken = {
          "selected", "meat-wagon-selected-group",
          "acknowledge", "meat-wagon-acknowledge",
          "ready", "meat-wagon-ready",
          "help", "forsaken help 3",
          "dead", "meat-wagon-dead",
          "attack", "meat-wagon-acknowledge",
       }
    }},
   {Names = {orc = "Warlock", human = "Conjurer", forsaken = "Banshee"},
    Costs = {"time", 90, "gold", 900},
    HitPoints = 40,
    Speed = 3,
    Armor = 0,
    Mana = {Max = 100, Enable = true},
	AnnoyComputerFactor = 200,
    CanCastSpell = {
       human = {
          "spell-summon-scorpions",
          "spell-summon-elemental",
          "spell-rain-of-fire"},
       orc = {
          "spell-summon-spiders",
          "spell-summon-daemon",
          "spell-poison-cloud" },
       forsaken = {
          "spell-summon-spiders",
          "spell-possession",
          "spell-poison-cloud" } },
    Missile = {orc = "missile-fireball", human = "missile-water", forsaken = "missile-fireball"},
    PiercingDamage = 6,
    BasicDamage = 0,
    MaxAttackRange = {human = 3, orc = 2, forsaken = 3},
    Sounds = {
       forsaken = {
          "selected", "banshee-selected-group",
          "acknowledge", "banshee-acknowledge",
          "ready", "banshee-ready",
          "help", "forsaken help 3",
          "dead", "banshee-dead",
          "attack", "banshee-acknowledge",
       }
    }},
   {Names = {orc = "Necrolyte", human = "Cleric", forsaken = "Necromancer"},
    Speed = 3,
    Costs = {"time", 80, "gold", 700},
    HitPoints = 40,
    Armor = 0,
    Coward = true,
    Mana = {Max = 100, Enable = true},
    AnnoyComputerFactor = 180,
    CanCastSpell = {
       human = {
          "spell-healing",
          "spell-far-seeing",
          "spell-invisibility"},
       orc = {
          "spell-raise-dead",
          "spell-dark-vision",
          "spell-unholy-armor" },
       forsaken = {
          "spell-raise-dead",
          "spell-dark-vision",
          "spell-death-coil" } },
    PiercingDamage = 6,
    Missile = "missile-magic-fireball",
    BasicDamage = 0,
    MaxAttackRange = {orc = 2, human = 1, forsaken = 2},
    Sounds = {
       forsaken = {
          "selected", "necromancer-selected-group",
          "acknowledge", "necromancer-acknowledge",
          "ready", "necromancer-ready",
          "help", "forsaken help 3",
          "dead", "necromancer-dead",
          "attack", "necromancer-acknowledge",
       }
    }},

   {Names = {forsaken = "Sylvanas"},
    Size = {forsaken = {32, 32}},
    HitPoints = 120,
    Armor = 4,
    Speed = 5,
    Animations = "animations-sylvanas",
    Mana = {Max = 100, Enable = true},
    Missile = "missile-arrow",
    PiercingDamage = 12,
    BasicDamage = 2,
    MaxAttackRange = 6,
    Sounds = {
       forsaken = {
          "selected", "sylvanas-selected-group",
          "acknowledge", "sylvanas-acknowledge",
          "ready", "sylvanas-ready",
          "help", "forsaken help 3",
          "dead", "sylvanas-dead",
          "attack", "sylvanas-acknowledge",
       }
    },
    CanCastSpell = {
       forsaken = {
          "spell-dark-vision",
          "spell-poison-cloud",
          "spell-raise-dead"
       }
    }},

   {Names = {forsaken = "Varimathras"},
    Size = {forsaken = {48, 48}},
    HitPoints = 300,
    Armor = 2,
    Speed = 4,
    Animations = "animations-varimathras",
    BasicDamage = 55,
    PiercingDamage = 10,
    organic = false,
    Sounds = {
       forsaken = {
          "selected", "varimathras-selected-group",
          "acknowledge", "varimathras-acknowledge",
          "ready", "varimathras-ready",
          "help", "forsaken help 3",
          "dead", "varimathras-dead",
          "attack", "varimathras-acknowledge",
       }
    }},

   {Names = {human = "Lothar"},
    Size = {human = {48, 48}},
    HitPoints = 50,
    Animations = "animations-medivh",
    Armor = 5,
    PiercingDamage = 1,
    BasicDamage = 15},

   {Names = {human = "Wounded Lothar"},
    Name = "Wounded",
    HitPoints = 60,
    Icon = "icon-wounded",
    Image = {
       "file", "neutral/units/wounded.png",
       "size", {32, 32}},
    Animations = "animations-wounded"},

   {Names = {human = "Medivh"},
    HitPoints = 110,
    Armor = 0,
    Mana = {Max = 100, Enable = true},
    Missile = "missile-fireball",
    PiercingDamage = 10,
    BasicDamage = 0,
    MaxAttackRange = 8,
    Mana = {Max = 100, Enable = true},
    CanCastSpell = {
       human = {"spell-summon-spiders",
                "spell-summon-daemon"}}}
}

-- build units from specs
for idx,unit in ipairs(units) do
   DefineUnitFromSpec(unit)
end

local EarlyMount = "blacksmith"           --this is to skip blacksmith req for knights and raiders, if you using Rebalanced stats
if preferences.RebalancedStats then
EarlyMount = "farm"
end

DefineUnitFromSpec({
   Names = {orc = "Raider", human = "Knight", forsaken = "Abomination"},
   Name = {orc = "Raider", human = "Knight", forsaken = "Abomination"},
   Size = {orc = {48, 48}, human = {32, 32}, forsaken = {48, 48}},
   Image = {orc = {"file", "orc/units/raider.png", "size", {48, 48}},
            human = {"file", "human/units/knight.png", "size", {32, 32}},
            forsaken = {"file", "forsaken/units/abomination.png", "size", {48, 48}}},
   Costs = {"time", 80, "gold", 850},
   HitPoints = 100,
   Armor = 4,
   Speed = 4,
   AnnoyComputerFactor = 120,
   PiercingDamage = 2,
   BasicDamage = 14,
   Dependencies = {orc = {EarlyMount, "kennel"},
                   human = {EarlyMount, "stable"},
                   forsaken = {EarlyMount, "stable"}},
   Sounds = {
      forsaken = {
         "selected", "abomination-selected-group",
         "acknowledge", "abomination-acknowledge",
         "ready", "abomination-ready",
         "help", "forsaken help 3",
         "dead", "abomination-dead",
         "attack", "abomination-acknowledge",
      }
   }})

-- Dedicated Death Knight hero / elite unit
DefineUnitType("unit-death-knight", {
   Name = "Death Knight",
   Animations = "animations-death-knight",
   Icon = "icon-death-knight",
   Image = {"file", "forsaken/units/death_knight.png", "size", {32, 32}},
   Costs = {"time", 80, "gold", 850},
   HitPoints = 120,
   Armor = 5,
   Speed = 5,
   BasicDamage = 14,
   PiercingDamage = 3,
   DrawLevel = 60,
   TileSize = {1, 1},
   BoxSize = {15, 15},
   SightRange = 4,
   organic = true,
   Sounds = {
      "selected", "death-knight-selected-group",
      "acknowledge", "death-knight-acknowledge",
      "ready", "death-knight-ready",
      "help", "forsaken help 3",
      "dead", "death-knight-dead",
      "attack", "death-knight-acknowledge",
   }
})

-- Dedicated Dark Ranger hero / elite unit
DefineUnitType("unit-dark-ranger", {
   Name = "Dark Ranger",
   Animations = "animations-dark-ranger",
   Icon = "icon-dark-ranger",
   Image = {"file", "forsaken/units/dark_ranger.png", "size", {32, 32}},
   Costs = {"time", 70, "gold", 450, "wood", 50},
   HitPoints = 75,
   Armor = 2,
   Speed = 4,
   BasicDamage = 2,
   PiercingDamage = 6,
   MaxAttackRange = 5,
   Missile = "missile-arrow",
   DrawLevel = 60,
   TileSize = {1, 1},
   BoxSize = {15, 15},
   SightRange = 5,
   organic = true,
   Sounds = {
      "selected", "dark-ranger-selected-group",
      "acknowledge", "dark-ranger-acknowledge",
      "ready", "dark-ranger-ready",
      "help", "forsaken help 3",
      "dead", "dark-ranger-dead",
      "attack", "dark-ranger-acknowledge",
   }
})

UnitEquivalents.forsaken["unit-dark-ranger"] = "unit-crypt-fiend"
UnitEquivalents.forsaken["unit-death-knight"] = "unit-abomination"

local dead_bodies = { Name = "Dead Body",
  Image = {"file", "neutral/units/dead_bodies.png", "size", {32, 32}},
  Animations = "animations-human-dead-body", Icon = "icon-peasant",
  Speed = 0,
  HitPoints = 255,
  DrawLevel = 30,
  TileSize = {1, 1}, BoxSize = {15, 15},
  SightRange = 1,
  BasicDamage = 0, PiercingDamage = 0, Missile = "missile-none",
  Priority = 0,
  Type = "land",
  Vanishes = true,
  Sounds = {} }
DefineUnitType("unit-human-dead-body", dead_bodies)
dead_bodies.Animations = "animations-orc-dead-body"
DefineUnitType("unit-orc-dead-body", dead_bodies)
dead_bodies.Animations = "animations-forsaken-dead-body"
DefineUnitType("unit-forsaken-dead-body", dead_bodies)
