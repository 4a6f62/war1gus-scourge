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
--
--  Dead units that still reference themselves crash the game when it ends.
--
--  A worker that is attacked while harvesting flees and keeps its harvest
--  order as CUnit::SavedOrder, and a harvest order holds a reference to its
--  own worker. LetUnitDie() only clears the regular order queue, so a worker
--  killed while fleeing keeps that reference to itself and is never released.
--  When the game ends, CUnit::Release() frees the saved order, which drops the
--  last reference and releases the unit a second time from inside the first
--  release. The unit then sits twice in the unit manager's release list and
--  is deleted twice: heap corruption (0xc0000374) on every victory or defeat
--  in which such a worker died.
--
--  Workaround: every unit type gets an OnDeath callback (called while the
--  unit is still on the map) that gives the dying unit a "stand-ground"
--  order. That clears SavedOrder (and a building's rally point) and only
--  appends to the order queue, which LetUnitDie() clears right afterwards.
--  Saved games made before this fix have the saved order stripped from their
--  dead units when they are loaded.
--
--  This file must be loaded before any unit type is defined.

if not EngineFixesInstalled then
   EngineFixesInstalled = true

   local function ClearDyingUnitOrders(unit)
      pcall(function()
         local x = GetUnitVariable(unit, "PosX")
         local y = GetUnitVariable(unit, "PosY")
         OrderUnit(GetUnitVariable(unit, "Player"), GetUnitVariable(unit, "Ident"),
                   {x, y, x, y}, {x, y}, "stand-ground")
      end)
   end

   --  OnDeath callbacks the game scripts set themselves, by unit type. They
   --  are kept here because a later partial DefineUnitType must not lose them.
   local ScriptOnDeath = {}

   local function OnDeathFor(ident)
      return function(unit, x, y)
         ClearDyingUnitOrders(unit)
         local callback = ScriptOnDeath[ident]
         if callback then
            return callback(unit, x, y)
         end
      end
   end

   local DefineUnitTypeOriginal = DefineUnitType
   DefineUnitType = function(ident, data, ...)
      if type(data) == "table" then
         if data.OnDeath then
            ScriptOnDeath[ident] = data.OnDeath
         end
         data.OnDeath = OnDeathFor(ident)
      end
      return DefineUnitTypeOriginal(ident, data, ...)
   end

   local CopyUnitTypeOriginal = CopyUnitType
   if type(CopyUnitTypeOriginal) == "function" then
      CopyUnitType = function(from, to, ...)
         local result = CopyUnitTypeOriginal(from, to, ...)
         ScriptOnDeath[to] = ScriptOnDeath[from]
         DefineUnitTypeOriginal(to, {OnDeath = OnDeathFor(to)})
         return result
      end
   end

   --  True if the saved unit is dead: destroyed, or playing its death.
   local function IsDeadUnitData(data)
      for i = 1, #data do
         if data[i] == "destroyed" then
            return true
         end
         if data[i] == "orders" and type(data[i + 1]) == "table" then
            local first = data[i + 1][1]
            if type(first) == "table" and first[1] == "action-die" then
               return true
            end
         end
      end
      return false
   end

   local function StripDeadUnitOrders(data)
      if not IsDeadUnitData(data) then
         return
      end
      for i = #data - 1, 1, -1 do
         if (data[i] == "saved-order" or data[i] == "new-order")
            and type(data[i + 1]) == "table" then
            table.remove(data, i + 1)
            table.remove(data, i)
         end
      end
   end

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
         if type(data) == "table" then
            StripDeadUnitOrders(data)
         end
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
