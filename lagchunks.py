#pylint: disable=F0401
import org.bukkit as bukkit
from helpers import *

lagchunks = []

def printHelp(sender):
  msg(sender, " &b/lagchunks <amount> &eList chunks where #entities >= <amount>")
  msg(sender, " &b/lagchunks list     &eShow list again")
  msg(sender, " &b/lagchunks tp <num> &eTeleport to chunk <num> from list")

def scanChunks(amount):
  try:
    global lagchunks
    chunks = []
    for world in bukkit.Bukkit.getServer().getWorlds():
      for chunk in world.getLoadedChunks():
        if len(chunk.getEntities()) >= amount:
          ents = chunk.getEntities()
          #                [0]world           [1]X                                [2]Y                               [3]Z                               [4]amount
          chunks.append([chunk.getWorld(), int(ents[-1].getLocation().getX()), int(ents[0].getLocation().getY()), int(ents[0].getLocation().getZ()), len(ents)])
    chunks.sort(key=lambda entry: entry[4], reverse=True)
    lagchunks = chunks
  except Exception, e:
    error(e)

def listChunks(sender):
  for id, chunk in enumerate(lagchunks):
    msg(sender, "&b%s&a: (&b%s&a) %s&7, &a%s &7(%s)" % (id, chunk[4], chunk[1], chunk[3], chunk[0].getName()))
  msg(sender, "&2------------------")


def tpChunk(sender, id):
  chunk = lagchunks[id]
  safetp(sender, chunk[0], chunk[1], chunk[2], chunk[3])
  msg(sender, "&aTeleported to &b%s&a, &b%s&a in &7%s&a with &b%s&a entities nearby." % (chunk[1], chunk[3], chunk[0].getName(), chunk[4]))

@hook.command("lagchunks")
def onLagchunksCommand(sender, args):
  try:
    if sender.hasPermission("utils.lagchunks"):
      plugHeader(sender, "Lagchunks")
      global lagchunks
      if len(args) == 1 and args[0].isdigit() and int(args[0]) > 0:
        amount = args[0]
        msg(sender, "&aChunks with at least &b%s &aentities:" % amount, )
        scanChunks(int(amount))
        listChunks(sender)
      elif len(args) == 1 and args[0].lower() == "list":
        listChunks(sender)
      elif len(args) == 2 and args[0].lower() == "tp" and args[1].isdigit() and int(args[1]) <= len(lagchunks)-1:
        if isinstance(sender, Player):
          tpChunk(sender, int(args[1]))
        else:
          msg(sender, "&cOnly players can do this!")
      else:
        printHelp(sender)
    else:
      noperm(sender)
    return True
  except Exception, e:
    error(e)