-- Define unit-buttons for the Forsaken race.

-- General movement and commands

DefineButton( { Pos = 1, Level = 0, Icon = "icon-move-forsaken",
  Action = "move",
  Key = "m", Hint = "~!MOVE",
  ForUnit = {"unit-ghoul", "unit-crypt-fiend", "unit-abomination", "unit-dark-ranger", "unit-death-knight",
    "unit-meat-wagon", "unit-acolyte",
    "unit-necromancer", "unit-banshee", "unit-sylvanas", "unit-varimathras",
    "forsaken-group" } } )

DefineButton( { Pos = 1, Level = 0, Icon = "icon-skeletal-steed1",
  Action = "move",
  Allowed = "check-upgrade", AllowArg = {"upgrade-skeletal-steed1"},
  Key = "m", Hint = "~!MOVE",
  ForUnit = { "unit-death-knight", "unit-abomination" } } )

DefineButton( { Pos = 1, Level = 0, Icon = "icon-skeletal-steed2",
  Action = "move",
  Allowed = "check-upgrade", AllowArg = {"upgrade-skeletal-steed2"},
  Key = "m", Hint = "~!MOVE",
  ForUnit = { "unit-death-knight", "unit-abomination" } } )

DefineButton( { Pos = 2, Level = 0, Icon = "icon-carapace1",
  Action = "stop",
  Key = "s", Hint = "~!STOP",
  ForUnit = {"unit-ghoul", "unit-crypt-fiend", "unit-abomination", "unit-dark-ranger", "unit-death-knight",
    "unit-meat-wagon", "unit-acolyte",
    "unit-necromancer", "unit-banshee", "unit-sylvanas", "unit-varimathras",
    "forsaken-group"} } )

DefineButton( { Pos = 2, Level = 0, Icon = "icon-carapace2",
  Action = "stop",
  Allowed = "check-upgrade", AllowArg = {"upgrade-carapace1"},
  Key = "s", Hint = "~!STOP",
  ForUnit = {"unit-ghoul", "unit-crypt-fiend", "unit-abomination", "unit-dark-ranger", "unit-death-knight"} } )

DefineButton( { Pos = 3, Level = 0, Icon = "icon-claws1",
  Action = "attack",
  Key = "a", Hint = "~!ATTACK",
  ForUnit = {"unit-ghoul", "unit-abomination", "unit-death-knight", "unit-varimathras",
    "unit-meat-wagon", "forsaken-group"} } )

DefineButton( { Pos = 3, Level = 0, Icon = "icon-claws2",
  Action = "attack",
  Allowed = "check-upgrade", AllowArg = {"upgrade-claws1"},
  Key = "a", Hint = "~!ATTACK",
  ForUnit = {"unit-ghoul", "unit-abomination", "unit-death-knight"} } )

DefineButton( { Pos = 3, Level = 0, Icon = "icon-dark-arrow1",
  Action = "attack",
  Key = "a", Hint = "~!ATTACK",
  ForUnit = {"unit-crypt-fiend", "unit-dark-ranger", "unit-sylvanas"} } )

DefineButton( { Pos = 3, Level = 0, Icon = "icon-dark-arrow2",
  Action = "attack",
  Allowed = "check-upgrade", AllowArg = {"upgrade-dark-arrow1"},
  Key = "a", Hint = "~!ATTACK",
  ForUnit = {"unit-crypt-fiend", "unit-dark-ranger", "unit-sylvanas"} } )

-- Necromancer specific actions

DefineButton( { Pos = 3, Level = 0, Icon = "icon-shadow-spear",
  Action = "attack",
  Key = "a", Hint = "SHADOW ~!ATTACK",
  ForUnit = {"unit-necromancer"} } )

DefineButton( { Pos = 4, Level = 0, Icon = "icon-raise-dead",
  Action = "cast-spell", Value = "spell-raise-dead",
  Allowed = "check-upgrade", AllowArg = {"upgrade-raise-dead"},
  Key = "r", Hint = "~!RAISE DEAD",
  ForUnit = {"unit-necromancer", "unit-sylvanas"} } )

DefineButton( { Pos = 5, Level = 0, Icon = "icon-dark-vision",
  Action = "cast-spell", Value = "spell-dark-vision",
  Allowed = "check-upgrade", AllowArg = {"upgrade-dark-vision"},
  Key = "v", Hint = "DARK ~!VISION",
  ForUnit = {"unit-necromancer", "unit-sylvanas"} } )

DefineButton( { Pos = 6, Level = 0, Icon = "icon-death-coil",
  Action = "cast-spell", Value = "spell-death-coil",
  Allowed = "check-upgrade", AllowArg = {"upgrade-unholy-armor"},
  Key = "c", Hint = "DEATH ~!COIL",
  ForUnit = {"unit-necromancer"} } )

-- Banshee specific actions

DefineButton( { Pos = 3, Level = 0, Icon = "icon-elemental-blast",
  Action = "attack",
  Key = "a", Hint = "ETHEREAL ~!BLAST",
  ForUnit = {"unit-banshee"} } )

DefineButton( { Pos = 4, Level = 0, Icon = "icon-spider",
  Action = "cast-spell", Value = "spell-summon-spiders",
  Allowed = "check-upgrade", AllowArg = {"upgrade-spider"},
  Key = "s", Hint = "SUMMON ~!SPIDERS",
  ForUnit = {"unit-banshee"} } )

DefineButton( { Pos = 5, Level = 0, Icon = "icon-poison-cloud",
  Action = "cast-spell", Value = "spell-poison-cloud",
  Allowed = "check-upgrade", AllowArg = {"upgrade-poison-cloud"},
  Key = "p", Hint = "~!PLAGUE CLOUD",
  ForUnit = {"unit-banshee", "unit-sylvanas"} } )

DefineButton( { Pos = 6, Level = 0, Icon = "icon-possession",
  Action = "cast-spell", Value = "spell-possession",
  Allowed = "check-upgrade", AllowArg = {"upgrade-daemon"},
  Key = "o", Hint = "P~!OSSESSION",
  ForUnit = {"unit-banshee"} } )

-- Acolyte worker actions

DefineButton( { Pos = 3, Level = 0, Icon = "icon-repair",
  Action = "repair",
  Key = "r", Hint = "~!REPAIR",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 4, Level = 0, Icon = "icon-harvest",
  Action = "harvest",
  Key = "h", Hint = "~!HARVEST WOOD/MINE GOLD",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 4, Level = 0, Icon = "icon-return-goods",
  Action = "return-goods",
  Key = "t", Hint = "RETURN GOODS TO ~!NECROPOLIS",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 5, Level = 0, Icon = "icon-build-basic",
  Action = "button", Value = 1,
  Key = "b", Hint = "BUILD ~!BASIC STRUCTURE",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 6, Level = 0, Icon = "icon-build-advanced",
  Action = "button", Value = 2,
  Allowed = "check-units-or", AllowArg = {"unit-forsaken-lumber-mill"},
  Key = "a", Hint = "BUILD ~!ADVANCED STRUCTURE",
  ForUnit = {"unit-acolyte"} } )

-- Basic Buildings

DefineButton( { Pos = 1, Level = 1, Icon = "icon-forsaken-farm",
  Action = "build", Value = "unit-forsaken-farm",
  Key = "z", Hint = "BUILD ~!ZIGGURAT",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 2, Level = 1, Icon = "icon-forsaken-lumber-mill",
  Action = "build", Value = "unit-forsaken-lumber-mill",
  Key = "g", Hint = "BUILD ~!GRAVEYARD",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 3, Level = 1, Icon = "icon-forsaken-barracks",
  Action = "build", Value = "unit-forsaken-barracks",
  Key = "c", Hint = "BUILD ~!CRYPT",
  ForUnit = {"unit-acolyte"} } )

if (preferences.AllowMultipleTownHalls) then
  DefineButton( { Pos = 4, Level = 1, Icon = "icon-forsaken-town-hall",
    Action = "build", Value = "unit-forsaken-town-hall",
    Key = "n", Hint = "BUILD ~!NECROPOLIS",
    ForUnit = {"unit-acolyte"} } )
else
  DefineButton( { Pos = 4, Level = 1, Icon = "icon-forsaken-town-hall",
    Action = "build", Value = "unit-forsaken-town-hall",
    Allowed = "check-units-not", AllowArg = {"unit-forsaken-town-hall"},
    Key = "n", Hint = "BUILD ~!NECROPOLIS",
    ForUnit = {"unit-acolyte"} } )
end

DefineButton( { Pos = 6, Level = 1, Icon = "icon-cancel",
  Action = "button", Value = 0,
  Key = "esc", Hint = "~<ESC~> - CANCEL",
  ForUnit = {"unit-acolyte"} } )

-- Advanced Buildings

DefineButton( { Pos = 1, Level = 2, Icon = "icon-forsaken-blacksmith",
  Action = "build", Value = "unit-forsaken-blacksmith",
  Key = "l", Hint = "BUILD S~!LAUGHTERHOUSE",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 2, Level = 2, Icon = "icon-forsaken-church",
  Action = "build", Value = "unit-forsaken-church",
  Key = "t", Hint = "BUILD ~!TEMPLE OF THE DAMNED",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 3, Level = 2, Icon = "icon-forsaken-stable",
  Action = "build", Value = "unit-forsaken-stable",
  Key = "p", Hint = "BUILD SACRIFICIAL ~!PIT",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 4, Level = 2, Icon = "icon-forsaken-tower",
  Action = "build", Value = "unit-forsaken-tower",
  Key = "o", Hint = "BUILD SPIRIT T~!OWER",
  ForUnit = {"unit-acolyte"} } )

DefineButton( { Pos = 6, Level = 2, Icon = "icon-cancel",
  Action = "button", Value = 0,
  Key = "esc", Hint = "~<ESC~> - CANCEL",
  ForUnit = {"unit-acolyte"} } )

-- Necropolis Training

DefineButton( { Pos = 1, Level = 0, Icon = "icon-acolyte",
  Action = "train-unit", Value = "unit-acolyte",
  Allowed = "check-no-research",
  Key = "a", Hint = "TRAIN ~!ACOLYTE",
  ForUnit = {"unit-forsaken-town-hall", "unit-forsaken-stormwind-keep"} } )

-- Crypt Training

DefineButton( { Pos = 1, Level = 0, Icon = "icon-ghoul",
  Action = "train-unit", Value = "unit-ghoul",
  Key = "g", Hint = "TRAIN ~!GHOUL",
  ForUnit = {"unit-forsaken-barracks"} } )

DefineButton( { Pos = 2, Level = 0, Icon = "icon-crypt-fiend",
  Action = "train-unit", Value = "unit-crypt-fiend",
  Key = "c", Hint = "TRAIN ~!CRYPT FIEND",
  ForUnit = {"unit-forsaken-barracks"} } )

DefineButton( { Pos = 3, Level = 0, Icon = "icon-meat-wagon",
  Action = "train-unit", Value = "unit-meat-wagon",
  Key = "m", Hint = "BUILD ~!MEAT WAGON",
  ForUnit = {"unit-forsaken-barracks"} } )

DefineButton( { Pos = 4, Level = 0, Icon = "icon-abomination",
  Action = "train-unit", Value = "unit-abomination",
  Key = "a", Hint = "TRAIN ~!ABOMINATION",
  ForUnit = {"unit-forsaken-barracks"} } )

-- Temple of the Damned Training & Spells

DefineButton( { Pos = 1, Level = 0, Icon = "icon-necromancer",
  Action = "train-unit", Value = "unit-necromancer",
  Key = "n", Hint = "TRAIN ~!NECROMANCER",
  ForUnit = {"unit-forsaken-church"} } )

DefineButton( { Pos = 2, Level = 0, Icon = "icon-raise-dead",
  Action = "research", Value = "upgrade-raise-dead",
  Allowed = "check-single-research",
  Key = "r", Hint = "RESEARCH ~!RAISE DEAD",
  ForUnit = {"unit-forsaken-church"} } )

DefineButton( { Pos = 3, Level = 0, Icon = "icon-dark-vision",
  Action = "research", Value = "upgrade-dark-vision",
  Allowed = "check-single-research",
  Key = "v", Hint = "RESEARCH DARK ~!VISION",
  ForUnit = {"unit-forsaken-church"} } )

DefineButton( { Pos = 4, Level = 0, Icon = "icon-death-coil",
  Action = "research", Value = "upgrade-unholy-armor",
  Allowed = "check-single-research",
  Key = "c", Hint = "RESEARCH DEATH ~!COIL",
  ForUnit = {"unit-forsaken-church"} } )

-- Spire of Torment Training & Spells

DefineButton( { Pos = 1, Level = 0, Icon = "icon-banshee",
  Action = "train-unit", Value = "unit-banshee",
  Key = "b", Hint = "TRAIN ~!BANSHEE",
  ForUnit = {"unit-forsaken-tower"} } )

DefineButton( { Pos = 2, Level = 0, Icon = "icon-spider",
  Action = "research", Value = "upgrade-spider",
  Allowed = "check-single-research",
  Key = "s", Hint = "RESEARCH SUMMON ~!SPIDERS",
  ForUnit = {"unit-forsaken-tower"} } )

DefineButton( { Pos = 3, Level = 0, Icon = "icon-poison-cloud",
  Action = "research", Value = "upgrade-poison-cloud",
  Allowed = "check-single-research",
  Key = "p", Hint = "RESEARCH ~!PLAGUE CLOUD",
  ForUnit = {"unit-forsaken-tower"} } )

DefineButton( { Pos = 4, Level = 0, Icon = "icon-possession",
  Action = "research", Value = "upgrade-daemon",
  Allowed = "check-single-research",
  Key = "o", Hint = "RESEARCH P~!OSSESSION",
  ForUnit = {"unit-forsaken-tower"} } )

-- Apothecary Upgrades

DefineButton( { Pos = 1, Level = 0, Icon = "icon-claws1",
  Action = "research", Value = "upgrade-claws1",
  Allowed = "check-single-research",
  Key = "c", Hint = "UPGRADE ~!CLAWS STRENGTH",
  ForUnit = {"unit-forsaken-blacksmith"} } )

DefineButton( { Pos = 1, Level = 0, Icon = "icon-claws2",
  Action = "research", Value = "upgrade-claws2",
  Allowed = "check-single-research",
  Key = "c", Hint = "UPGRADE ~!CLAWS STRENGTH",
  ForUnit = {"unit-forsaken-blacksmith"} } )

DefineButton( { Pos = 2, Level = 0, Icon = "icon-carapace1",
  Action = "research", Value = "upgrade-carapace1",
  Allowed = "check-single-research",
  Key = "a", Hint = "UPGRADE ~!CARAPACE ARMOR",
  ForUnit = {"unit-forsaken-blacksmith"} } )

DefineButton( { Pos = 2, Level = 0, Icon = "icon-carapace2",
  Action = "research", Value = "upgrade-carapace2",
  Allowed = "check-single-research",
  Key = "a", Hint = "UPGRADE ~!CARAPACE ARMOR",
  ForUnit = {"unit-forsaken-blacksmith"} } )

-- Graveyard Upgrades

DefineButton( { Pos = 1, Level = 0, Icon = "icon-dark-arrow1",
  Action = "research", Value = "upgrade-dark-arrow1",
  Allowed = "check-single-research",
  Key = "d", Hint = "UPGRADE ~!DARK ARROWS",
  ForUnit = {"unit-forsaken-lumber-mill"} } )

DefineButton( { Pos = 1, Level = 0, Icon = "icon-dark-arrow2",
  Action = "research", Value = "upgrade-dark-arrow2",
  Allowed = "check-single-research",
  Key = "d", Hint = "UPGRADE ~!DARK ARROWS",
  ForUnit = {"unit-forsaken-lumber-mill"} } )

-- Skeletal Stables Upgrades

DefineButton( { Pos = 1, Level = 0, Icon = "icon-skeletal-steed1",
  Action = "research", Value = "upgrade-skeletal-steed1",
  Allowed = "check-single-research",
  Key = "s", Hint = "BREED FASTER SKELETAL ~!STEEDS",
  ForUnit = {"unit-forsaken-stable"} } )

DefineButton( { Pos = 1, Level = 0, Icon = "icon-skeletal-steed2",
  Action = "research", Value = "upgrade-skeletal-steed2",
  Allowed = "check-single-research",
  Key = "s", Hint = "BREED FASTER SKELETAL ~!STEEDS",
  ForUnit = {"unit-forsaken-stable"} } )
