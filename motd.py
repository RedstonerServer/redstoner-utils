#pylint: disable = F0401
from helpers import *

motd = server.getMotd()

raise TypeError("testing /modules") # remove this line!

@hook.command("getmotd")
def on_getmotd_command(sender, args):
  plugin_header(sender, "MOTD")
  msg(sender, motd, usecolor = False)


@hook.command("setmotd")
def on_setmotd_command(sender, args):
  global motd
  if sender.hasPermission("utils.setmotd"):
    if not checkargs(sender, args, 1, -1):
      return True

    motd = colorify(" ".join(args).replace("\\n", "\n"))
    broadcast(None, plugin_header(name="MOTD"))
    broadcast(None, "&aNew MOTD:&r\n%s" % motd)
    broadcast(None, " ")
  else:
    noperm(sender)
  return True


@hook.event("server.ServerListPingEvent")
def on_server_ping(event):
  event.setMotd(motd)
