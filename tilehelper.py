#pylint: disable=F0401
import org.bukkit.event.block.BlockPlaceEvent as BlockPlaceEvent
from helpers import *

tilehelpers = [
  {"owner": "ae795aa8-6327-408e-92ab-25c8a59f3ba1", "area": [[90, 90], [70, 70], [90, 90]], "world": "b0385345-4803-4522-a06a-75fbd692928d", "directions": "neswud"}
]
dirmap = {
  #    [x, y, z]
  "n": [0, 0, -1],
  "e": [+1, 0, 0],
  "s": [0, 0, +1],
  "w": [-1, 0, 0],
  "u": [0, +1, 0],
  "d": [0, -1, 0]
}

# FIXME: disallow multiple regions by single person.
# FIXME: could lead to two regions updating each other forever -> server freezes

@hook.event("block.BlockPlaceEvent", "high")
def onPlaceBlockInRegion(event):
  if not event.isCancelled():
    player = event.getPlayer()
    block  = event.getBlockPlaced()
    for th in tilehelpers:
      area = th.get("area")
      if th.get("owner") == str(player.getUniqueId()) and str(block.getWorld().getUID()) == th.get("world") and block.getX() in range(area[0][0], area[0][1]+1) and block.getY() in range(area[1][0], area[1][1]+1) and block.getZ() in range(area[2][0], area[2][1]+1) and event.canBuild():

        # stack block in directions
        msg(player, "&aplaced block in region")

        for direction in th.get("directions"):
          directions = dirmap[direction]
          size       = [1 + abs(area[0][1] - area[0][0]), 1 + abs(area[1][1] - area[1][0]), 1 + abs(area[2][1] - area[2][0])]
          oldplaced  = event.getBlockAgainst()

          newblock   = block.getWorld().getBlockAt(block.getX() + size[0] * directions[0], block.getY() + size[1] * directions[1], block.getZ() + size[2] * directions[2])
          newplaced  = oldplaced.getWorld().getBlockAt(oldplaced.getX() + size[0] * directions[0], oldplaced.getY() + size[1] * directions[1], oldplaced.getZ() + size[2] * directions[2])
          newstate   = newblock.getState()
          newstate.setType(block.getType())

          event      = BlockPlaceEvent(newblock, block.getState(), newplaced, event.getItemInHand(), player, event.canBuild())
          server.getPluginManager().callEvent(event)
          msg(player, "Direction %s: %s" % (direction, event.isCancelled()))
          if not event.isCancelled():
            newplaced.setType(block.getType())