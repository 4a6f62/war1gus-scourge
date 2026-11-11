--      engine_fixes.lua - Lua-side workarounds for Stratagus engine bugs.
--
--  Rally points pointing at a dead unit crash the game when it ends.
--
--  A building's rally point (CUnit::NewOrder) keeps a reference to its goal.
--  Rallying a town hall onto a gold mine and letting the mine run dry leaves
--  the rally order pointing at a destroyed unit. When the game ends,
--  CleanUnits() frees that destroyed mine first and the rally order later,
--  which then dereferences freed memory: "double free or corruption" (or the
--  assert "Release: !GameCycle || !Refs" when started with -a). This happens in
--  Stratagus 3.3.2 and in current upstream master.
--
--  Workaround: right before any game ends, reset every building's rally point
--  with the "stand-ground" order. For buildings this only replaces NewOrder;
--  it does not touch training or construction queues.

if not EngineFixesInstalled then
   EngineFixesInstalled = true

   local function ClearRallyPoints()
      pcall(function()
         local w = Map.Info.MapWidth
         local h = Map.Info.MapHeight
         if w and h and w > 0 and h > 0 then
            OrderUnit("any", "buildings", {0, 0, w - 1, h - 1}, {0, 0}, "stand-ground")
         end
      end)
   end

   --  Saves store each unit's spell cooldowns as a list with one entry per
   --  spell slot, and the engine refuses a list of the wrong length. Saves
   --  made with a different spell list (before spells.lua added NewSpellSlots)
   --  get their list fixed up so they still load.
   local UnitOriginal = Unit
   if type(UnitOriginal) == "function" then
      Unit = function(slot, data)
         if type(data) == "table" and SpellCount and NewSpellSlots then
            for i = 1, #data - 1 do
               local cooldowns = data[i + 1]
               if data[i] == "spell-cooldown" and type(cooldowns) == "table"
                  and #cooldowns ~= SpellCount then
                  -- Normalize to the pre-NewSpellSlots length (cooldowns are
                  -- only timers, so dropping or zeroing extras is harmless),
                  -- then insert zeros at the new spells' slots.
                  local base = SpellCount - #NewSpellSlots
                  while #cooldowns > base do table.remove(cooldowns) end
                  while #cooldowns < base do table.insert(cooldowns, 0) end
                  local sorted = {}
                  for _, s in ipairs(NewSpellSlots) do table.insert(sorted, s) end
                  table.sort(sorted)
                  for _, s in ipairs(sorted) do
                     table.insert(cooldowns, s + 1, 0)
                  end
               end
            end
         end
         return UnitOriginal(slot, data)
      end
   end

   for _, name in ipairs({"StopGame", "ActionVictory", "ActionDefeat", "ActionDraw", "Exit"}) do
      local original = _G[name]
      if type(original) == "function" then
         _G[name] = function(...)
            ClearRallyPoints()
            return original(...)
         end
      end
   end
end
