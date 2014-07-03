#pylint: disable=F0401
from helpers import *

motd = server.getMotd()

@hook.command("getmotd")
def onGetMotdCommand(sender, args):
  plugHeader(sender "MOTD")
  msg(sender, motd, usecolor=False)


@hook.command("setmotd")
def onSetMotdCommand(sender, args):
  global motd
  plugHeader(sender, "MOTD")
  if sender.hasPermission("utils.setmotd"):
    if not checkargs(sender, args, 1, -1):
      return True

    motd = colorify(" ".join(args))
    broadcast(plugHeader(name="MOTD"))
    broadcast("&aNew MOTD:&r\n%s" % motd)
  else:
    noperm(sender)
  return True

@hook.event("server.ServerListPingEvent")
def onServerPing(event):
  event.setMotd(motd)