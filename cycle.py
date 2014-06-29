import simplejson as json
from helpers import *

cyclers_file = "plugins/redstoner-utils.py.dir/files/cycle.json"
no_cyclers   = []
try:
  no_cyclers = json.loads(open(cyclers_file).read())
except Exception, e:
  error("Failed to load no_cyclers: %s" % e)


@hook.command("cycle")
def onCyclerCommand(sender, args):
  plugHeader(sender, "Cycle")
  if not isPlayer(sender):
    msg(sender, "&conly players can do this")
    return True
  if not checkargs(sender, args, 1, 1):
    return True

  cmd = args[0].lower()
  pid = sender.getUniqueId()
  nop = pid in no_cyclers
  if cmd == "on":
    if nop:
      no_cyclers.remove(pid)
      msg(sender, "&aTurned &2on&a inventory cycling!")
    else:
      msg(sender, "&aAlready turned on.")
  elif cmd == "off":
    if not nop:
      no_cyclers.append(pid)
      msg(sender, "&aTurned &coff&a inventory cycling!")
    else:
      msg(sender, "&aAlready turned off.")
  else:
    msg(sender, "&cUsage: /cycle <on|off>")
  return True


@hook.event("player.PlayerItemHeldEvent", "normal")
def onSlotChange(event):
  player    = event.getPlayer()
  if player.getUniqueId() not in no_cyclers:
    prev_slot = event.getPreviousSlot()
    new_slot  = event.getNewSlot()
    if (prev_slot == 0 and new_slot == 8): # left -> right
      doCycle(player, True)
    elif (prev_slot == 8 and new_slot == 0): # right -> left
      doCycle(player, False)


def doCycle(player, up):
  inv   = player.getInventory()
  items = inv.getContents()
  shift = -9 if up else 9
  shift = shift % len(items)
  for _ in range(4):
    uniq_items = sorted(set(list(items)[:shift])) # crazy code
    msg(player, items[:shift])
    items = items[shift:] + items[:shift] # shift "around"
    if uniq_items != [None]: # row not empty
      break

  inv.setContents(items)