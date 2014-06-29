import simplejson as json
from helpers import *

cyclers_file = "plugins/redstoner-utils.py.dir/files/cycle.json"
no_cyclers   = [] # opt-out
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
  if not len(args) == 1:
    msg(sender, "&cUsage: /cycle <on|off>")
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

# ITEM SLOTS #
#_____________________________
# | 9|11|12|13|14|15|16|17|18|
# |19|20|21|22|23|24|25|26|27|
# |28|29|30|31|32|33|34|35|36|
#_____________________________
# | 0| 1| 2| 3| 4| 5| 6| 7| 8|

def doCycle(player, up):
  inv   = player.getInventory()
  items = inv.getContents()
  shift = -9 if up else 9
  shift = shift % len(items)
  for _ in range(4):
    items      = items[shift:] + items[:shift] # shift "around"
    uniq_items = sorted(set(list(items)[:9]))  # get unique inventory
    msg(player, uniq_items)
    if uniq_items != [None]: # row not empty
      msg(player, "not empty, using")
      break
    msg(player, "empty, skipping")
  inv.setContents(items)

def saveCyclers():
  try:
    chatgroups_file = open(cyclers_file, "w")
    chatgroups_file.write(json.dumps(no_cyclers))
    chatgroups_file.close()
  except Exception, e:
    error("Failed to write reports: " + str(e))