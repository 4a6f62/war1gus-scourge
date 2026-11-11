-- =============================================================================
-- Authentic Warcraft III Undead Scourge Sound Definitions
-- =============================================================================

-- Race-wide faction announcements & alerts
MakeSound("forsaken work complete", "forsaken/work_complete.wav")
MakeSound("forsaken ready", "forsaken/ready.wav")
MakeSound("forsaken help 1", "forsaken/help_1.wav")
MakeSound("forsaken help 2", "forsaken/help_2.wav")
MakeSound("forsaken help 3", "forsaken/help_3.wav")
MakeSound("forsaken help 4", "forsaken/help_4.wav")
MakeSound("forsaken dead", "forsaken/dead.wav")

MakeSound("forsaken acknowledge", {
  "forsaken/acknowledgement_1.wav",
  "forsaken/acknowledgement_2.wav",
  "forsaken/acknowledgement_3.wav",
  "forsaken/acknowledgement_4.wav"
})

MakeSound("forsaken annoyed", {
  "forsaken/annoyed_1.wav",
  "forsaken/annoyed_2.wav",
  "forsaken/annoyed_3.wav"
})

MakeSound("forsaken-selected", {
  "forsaken/selected_1.wav",
  "forsaken/selected_2.wav",
  "forsaken/selected_3.wav",
  "forsaken/selected_4.wav",
  "forsaken/selected_5.wav"
})

MakeSoundGroup("forsaken selected", "forsaken-selected", "forsaken annoyed")

MakeSound("forsaken-victory", {
  "forsaken/victory_1.wav",
  "forsaken/victory_2.wav",
  "forsaken/victory_3.wav"
})
MakeSound("forsaken-defeat", { "forsaken/defeat.wav" })

-- -----------------------------------------------------------------------------
-- Scourge Building Selected Sounds (All 9 WC3 Buildings)
-- -----------------------------------------------------------------------------
MakeSound("forsaken-town-hall-selected", "forsaken/buildings/necropolis.wav")
MakeSound("forsaken-farm-selected", "forsaken/buildings/ziggurat.wav")
MakeSound("forsaken-barracks-selected", "forsaken/buildings/crypt.wav")
MakeSound("forsaken-lumber-mill-selected", "forsaken/buildings/graveyard.wav")
MakeSound("forsaken-blacksmith-selected", "forsaken/buildings/slaughterhouse.wav")
MakeSound("forsaken-stable-selected", "forsaken/buildings/sacrificial_pit.wav")
MakeSound("forsaken-church-selected", "forsaken/buildings/temple_of_the_damned.wav")
MakeSound("forsaken-tower-selected", "forsaken/buildings/spirit_tower.wav")
MakeSound("forsaken-stormwind-keep-selected", "forsaken/buildings/citadel.wav")

-- -----------------------------------------------------------------------------
-- 1. ACOLYTE Sounds
-- -----------------------------------------------------------------------------
MakeSound("acolyte-selected", {
  "forsaken/acolyte/selected_1.wav",
  "forsaken/acolyte/selected_2.wav",
  "forsaken/acolyte/selected_3.wav",
  "forsaken/acolyte/selected_4.wav"
})
MakeSound("acolyte-annoyed", {
  "forsaken/acolyte/annoyed_1.wav",
  "forsaken/acolyte/annoyed_2.wav",
  "forsaken/acolyte/annoyed_3.wav"
})
MakeSoundGroup("acolyte-selected-group", "acolyte-selected", "acolyte-annoyed")

MakeSound("acolyte-acknowledge", {
  "forsaken/acolyte/acknowledge_1.wav",
  "forsaken/acolyte/acknowledge_2.wav",
  "forsaken/acolyte/acknowledge_3.wav",
  "forsaken/acolyte/acknowledge_4.wav"
})
MakeSound("acolyte-ready", "forsaken/acolyte/ready.wav")
MakeSound("acolyte-dead", "forsaken/acolyte/dead.wav")

-- -----------------------------------------------------------------------------
-- 2. GHOUL Sounds
-- -----------------------------------------------------------------------------
MakeSound("ghoul-selected", {
  "forsaken/ghoul/selected_1.wav",
  "forsaken/ghoul/selected_2.wav",
  "forsaken/ghoul/selected_3.wav",
  "forsaken/ghoul/selected_4.wav",
  "forsaken/ghoul/selected_5.wav"
})
MakeSound("ghoul-annoyed", {
  "forsaken/ghoul/annoyed_1.wav",
  "forsaken/ghoul/annoyed_2.wav",
  "forsaken/ghoul/annoyed_3.wav"
})
MakeSoundGroup("ghoul-selected-group", "ghoul-selected", "ghoul-annoyed")

MakeSound("ghoul-acknowledge", {
  "forsaken/ghoul/acknowledge_1.wav",
  "forsaken/ghoul/acknowledge_2.wav",
  "forsaken/ghoul/acknowledge_3.wav",
  "forsaken/ghoul/acknowledge_4.wav"
})
MakeSound("ghoul-ready", "forsaken/ghoul/ready.wav")
MakeSound("ghoul-dead", "forsaken/ghoul/dead.wav")

-- -----------------------------------------------------------------------------
-- 3. CRYPT FIEND Sounds
-- -----------------------------------------------------------------------------
MakeSound("crypt-fiend-selected", {
  "forsaken/crypt_fiend/selected_1.wav",
  "forsaken/crypt_fiend/selected_2.wav",
  "forsaken/crypt_fiend/selected_3.wav",
  "forsaken/crypt_fiend/selected_4.wav",
  "forsaken/crypt_fiend/selected_5.wav"
})
MakeSound("crypt-fiend-annoyed", {
  "forsaken/crypt_fiend/annoyed_1.wav",
  "forsaken/crypt_fiend/annoyed_2.wav",
  "forsaken/crypt_fiend/annoyed_3.wav"
})
MakeSoundGroup("crypt-fiend-selected-group", "crypt-fiend-selected", "crypt-fiend-annoyed")

MakeSound("crypt-fiend-acknowledge", {
  "forsaken/crypt_fiend/acknowledge_1.wav",
  "forsaken/crypt_fiend/acknowledge_2.wav",
  "forsaken/crypt_fiend/acknowledge_3.wav",
  "forsaken/crypt_fiend/acknowledge_4.wav"
})
MakeSound("crypt-fiend-ready", "forsaken/crypt_fiend/ready.wav")
MakeSound("crypt-fiend-dead", "forsaken/crypt_fiend/dead.wav")

-- -----------------------------------------------------------------------------
-- 4. ABOMINATION Sounds
-- -----------------------------------------------------------------------------
MakeSound("abomination-selected", {
  "forsaken/abomination/selected_1.wav",
  "forsaken/abomination/selected_2.wav",
  "forsaken/abomination/selected_3.wav",
  "forsaken/abomination/selected_4.wav",
  "forsaken/abomination/selected_5.wav"
})
MakeSound("abomination-annoyed", {
  "forsaken/abomination/annoyed_1.wav",
  "forsaken/abomination/annoyed_2.wav",
  "forsaken/abomination/annoyed_3.wav"
})
MakeSoundGroup("abomination-selected-group", "abomination-selected", "abomination-annoyed")

MakeSound("abomination-acknowledge", {
  "forsaken/abomination/acknowledge_1.wav",
  "forsaken/abomination/acknowledge_2.wav",
  "forsaken/abomination/acknowledge_3.wav",
  "forsaken/abomination/acknowledge_4.wav"
})
MakeSound("abomination-ready", "forsaken/abomination/ready.wav")
MakeSound("abomination-dead", "forsaken/abomination/dead.wav")

-- -----------------------------------------------------------------------------
-- 5. DARK RANGER Sounds
-- -----------------------------------------------------------------------------
MakeSound("dark-ranger-selected", {
  "forsaken/dark_ranger/selected_1.wav",
  "forsaken/dark_ranger/selected_2.wav",
  "forsaken/dark_ranger/selected_3.wav",
  "forsaken/dark_ranger/selected_4.wav"
})
MakeSound("dark-ranger-annoyed", {
  "forsaken/dark_ranger/annoyed_1.wav",
  "forsaken/dark_ranger/annoyed_2.wav",
  "forsaken/dark_ranger/annoyed_3.wav"
})
MakeSoundGroup("dark-ranger-selected-group", "dark-ranger-selected", "dark-ranger-annoyed")

MakeSound("dark-ranger-acknowledge", {
  "forsaken/dark_ranger/acknowledge_1.wav",
  "forsaken/dark_ranger/acknowledge_2.wav",
  "forsaken/dark_ranger/acknowledge_3.wav",
  "forsaken/dark_ranger/acknowledge_4.wav"
})
MakeSound("dark-ranger-ready", "forsaken/dark_ranger/ready.wav")
MakeSound("dark-ranger-dead", "forsaken/dark_ranger/dead.wav")

-- -----------------------------------------------------------------------------
-- 6. SYLVANAS Sounds
-- -----------------------------------------------------------------------------
MakeSound("sylvanas-selected", {
  "forsaken/sylvanas/selected_1.wav",
  "forsaken/sylvanas/selected_2.wav",
  "forsaken/sylvanas/selected_3.wav",
  "forsaken/sylvanas/selected_4.wav"
})
MakeSound("sylvanas-annoyed", {
  "forsaken/sylvanas/annoyed_1.wav",
  "forsaken/sylvanas/annoyed_2.wav",
  "forsaken/sylvanas/annoyed_3.wav"
})
MakeSoundGroup("sylvanas-selected-group", "sylvanas-selected", "sylvanas-annoyed")

MakeSound("sylvanas-acknowledge", {
  "forsaken/sylvanas/acknowledge_1.wav",
  "forsaken/sylvanas/acknowledge_2.wav",
  "forsaken/sylvanas/acknowledge_3.wav",
  "forsaken/sylvanas/acknowledge_4.wav"
})
MakeSound("sylvanas-ready", "forsaken/sylvanas/ready.wav")
MakeSound("sylvanas-dead", "forsaken/sylvanas/dead.wav")

-- -----------------------------------------------------------------------------
-- 7. DEATH KNIGHT Sounds
-- -----------------------------------------------------------------------------
MakeSound("death-knight-selected", {
  "forsaken/death_knight/selected_1.wav",
  "forsaken/death_knight/selected_2.wav",
  "forsaken/death_knight/selected_3.wav",
  "forsaken/death_knight/selected_4.wav"
})
MakeSound("death-knight-annoyed", {
  "forsaken/death_knight/annoyed_1.wav",
  "forsaken/death_knight/annoyed_2.wav",
  "forsaken/death_knight/annoyed_3.wav"
})
MakeSoundGroup("death-knight-selected-group", "death-knight-selected", "death-knight-annoyed")

MakeSound("death-knight-acknowledge", {
  "forsaken/death_knight/acknowledge_1.wav",
  "forsaken/death_knight/acknowledge_2.wav",
  "forsaken/death_knight/acknowledge_3.wav",
  "forsaken/death_knight/acknowledge_4.wav"
})
MakeSound("death-knight-ready", "forsaken/death_knight/ready.wav")
MakeSound("death-knight-dead", "forsaken/death_knight/dead.wav")

-- -----------------------------------------------------------------------------
-- 8. MEAT WAGON Sounds
-- -----------------------------------------------------------------------------
MakeSound("meat-wagon-selected", {
  "forsaken/meat_wagon/selected_1.wav",
  "forsaken/meat_wagon/selected_2.wav",
  "forsaken/meat_wagon/selected_3.wav"
})
MakeSound("meat-wagon-annoyed", {
  "forsaken/meat_wagon/annoyed_1.wav",
  "forsaken/meat_wagon/annoyed_2.wav"
})
MakeSoundGroup("meat-wagon-selected-group", "meat-wagon-selected", "meat-wagon-annoyed")

MakeSound("meat-wagon-acknowledge", {
  "forsaken/meat_wagon/acknowledge_1.wav",
  "forsaken/meat_wagon/acknowledge_2.wav",
  "forsaken/meat_wagon/acknowledge_3.wav"
})
MakeSound("meat-wagon-ready", "forsaken/meat_wagon/ready.wav")
MakeSound("meat-wagon-dead", "forsaken/meat_wagon/dead.wav")

-- -----------------------------------------------------------------------------
-- 9. NECROMANCER Sounds
-- -----------------------------------------------------------------------------
MakeSound("necromancer-selected", {
  "forsaken/necromancer/selected_1.wav",
  "forsaken/necromancer/selected_2.wav",
  "forsaken/necromancer/selected_3.wav",
  "forsaken/necromancer/selected_4.wav"
})
MakeSound("necromancer-annoyed", {
  "forsaken/necromancer/annoyed_1.wav",
  "forsaken/necromancer/annoyed_2.wav",
  "forsaken/necromancer/annoyed_3.wav"
})
MakeSoundGroup("necromancer-selected-group", "necromancer-selected", "necromancer-annoyed")

MakeSound("necromancer-acknowledge", {
  "forsaken/necromancer/acknowledge_1.wav",
  "forsaken/necromancer/acknowledge_2.wav",
  "forsaken/necromancer/acknowledge_3.wav",
  "forsaken/necromancer/acknowledge_4.wav"
})
MakeSound("necromancer-ready", "forsaken/necromancer/ready.wav")
MakeSound("necromancer-dead", "forsaken/necromancer/dead.wav")

-- -----------------------------------------------------------------------------
-- 10. BANSHEE Sounds
-- -----------------------------------------------------------------------------
MakeSound("banshee-selected", {
  "forsaken/banshee/selected_1.wav",
  "forsaken/banshee/selected_2.wav",
  "forsaken/banshee/selected_3.wav",
  "forsaken/banshee/selected_4.wav"
})
MakeSound("banshee-annoyed", {
  "forsaken/banshee/annoyed_1.wav",
  "forsaken/banshee/annoyed_2.wav"
})
MakeSoundGroup("banshee-selected-group", "banshee-selected", "banshee-annoyed")

MakeSound("banshee-acknowledge", {
  "forsaken/banshee/acknowledge_1.wav",
  "forsaken/banshee/acknowledge_2.wav",
  "forsaken/banshee/acknowledge_3.wav",
  "forsaken/banshee/acknowledge_4.wav"
})
MakeSound("banshee-ready", "forsaken/banshee/ready.wav")
MakeSound("banshee-dead", "forsaken/banshee/dead.wav")

-- -----------------------------------------------------------------------------
-- 11. VARIMATHRAS Sounds
-- -----------------------------------------------------------------------------
MakeSound("varimathras-selected", {
  "forsaken/varimathras/selected_1.wav",
  "forsaken/varimathras/selected_2.wav",
  "forsaken/varimathras/selected_3.wav",
  "forsaken/varimathras/selected_4.wav"
})
MakeSound("varimathras-annoyed", {
  "forsaken/varimathras/annoyed_1.wav",
  "forsaken/varimathras/annoyed_2.wav",
  "forsaken/varimathras/annoyed_3.wav"
})
MakeSoundGroup("varimathras-selected-group", "varimathras-selected", "varimathras-annoyed")

MakeSound("varimathras-acknowledge", {
  "forsaken/varimathras/acknowledge_1.wav",
  "forsaken/varimathras/acknowledge_2.wav",
  "forsaken/varimathras/acknowledge_3.wav",
  "forsaken/varimathras/acknowledge_4.wav"
})
MakeSound("varimathras-ready", "forsaken/varimathras/ready.wav")
MakeSound("varimathras-dead", "forsaken/varimathras/dead.wav")
