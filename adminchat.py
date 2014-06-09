#pylint: disable=F0401
from helpers import *

ac_permission  = "utils.ac"
ac_key         = ","
ac_toggle_list = []


def adminchat(sender, msg):
  name = "&7{unknown}"
  try:
    name = sender.getDisplayName()
  except:
    name = sender.getName()
  broadcast(ac_permission, "&8[&bAC&8] &9%s&8: &b%s" % (name, msg))


# ac toggle
@hook.command("act")
def onActCommand(sender, args):
  if sender.hasPermission(ac_permission):
    p = sender.getName()
    if p in ac_toggle_list:
      ac_toggle_list.remove(p)
      msg(sender, "&8[&bAC&8] &aAC toggle: off")
    else:
      ac_toggle_list.append(p)
      msg(sender, "&8[&bAC&8] &aAC toggle: on")
  else:
    noperm(sender)
  return True


@hook.command("ac")
def onAcCommand(sender, args):
  if sender.hasPermission(ac_permission):
    if not checkargs(sender, args, 1, -1):
      return True
    adminchat(sender, " ".join(args))
  else:
    noperm(sender)
  return True


@hook.event("player.PlayerChatEvent", "normal")
def onChat(event):
  sender = event.getPlayer()
  msg = event.getMessage()
  if sender.hasPermission(ac_permission) and not event.isCancelled():
    if msg[:len(ac_key)] == ac_key:
      adminchat(sender, msg[1:])
      event.setCancelled(True)
    elif sender.getName() in ac_toggle_list:
      adminchat(sender, msg)
      event.setCancelled(True)
