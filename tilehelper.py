import org.bukkit as bukkit
import bukkit.event.block.BlockPlaceEvent as BlockPlaceEvent
from helpers import *

tilehelpers = [                                                                                                                                           # Front Right Back  Left  Down   Up
  {"owner": "ae795aa8-6327-408e-92ab-25c8a59f3ba1", "area": [[90, 95], [60, 90], [90, 95]], "world": "b0385345-4803-4522-a06a-75fbd692928d", "directions": [True, True, True, True, False, False]}
]

@hook.event("block.BlockPlaceEvent", "high")
def onPlaceBlock(event):
  if not event.isCancelled():
    player = event.getPlayer()
    block  = event.getBlockPlaced()
    for th in tilehelpers:
      area = th.get("area")
      if th.get("owner") == str(player.getUniqueId()) and str(block.getWorld().getUID()) == th.get("world") and block.getX() in range(area[0][0], area[0][1]+1) and block.getY() in range(area[1][0], area[1][1]+1) and block.getZ() in range(area[2][0], area[2][1]+1) and event.canBuild():

        # stack block in directions
        msg(player, "&ayus")

        event = BlockPlaceEvent(block, block.getState(), event.getBlockAgainst(), event.getItemInHand(), player, event.canBuild())

  #     server.getPluginManager().callEvent(event);
