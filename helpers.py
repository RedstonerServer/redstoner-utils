from re import sub
import org.bukkit as bukkit
import org.bukkit.Location as Location
import org.bukkit.entity.Player as Player
import org.bukkit.event.player.PlayerTeleportEvent.TeleportCause as TeleportCause
import org.bukkit.block as block
from java.util.logging import Level

server = bukkit.Bukkit.getServer()

def log(text):
  server.getLogger().info("[RedstonerUtils] %s" % colorify(text))

def error(text):
  server.getLogger().severe("[RedstonerUtils] %s" % text)

def msg(player, text, usecolor=True, basecolor=None):
  if player and (player == server.getConsoleSender() or player.getPlayer()): #getPlayer() returns None when offline
    if basecolor:
      player.sendMessage(colorify("&%s" % basecolor) + (colorify(text) if usecolor else text))
    else:
      player.sendMessage(colorify(text) if usecolor else text)

# better than bukkit's broadcast.
# bukkit only works with permissibles that are subscribed to perm
def broadcast(perm, text):
  try:
    text = colorify(text)
    for recipient in server.getOnlinePlayers().tolist() + [server.getConsoleSender()]:
      (not perm or recipient.hasPermission(perm)) and msg(recipient, text)
  except Exception, e:
    error(e)

def colorify(text):
  return sub("&(?=[?\da-fk-or])", u"\u00A7", "%s" % text)

def safetp(player, world, x, y, z, yaw=0, pitch=0):
  tpblock = Location(world, x, y, z).getBlock()
  if (tpblock.isEmpty() and tpblock.getRelative(block.BlockFace.UP).isEmpty()) or y > 255:
    player.teleport(Location(world, x+0.5, y, z+0.5, yaw, pitch), TeleportCause.COMMAND)
  else:
    safetp(player, world, x, y+1, z, yaw, pitch)

def plugHeader(sender, name):
  msg(sender, "&2--=[ %s ]=--" % name)

def noperm(player):
  msg(player, "&cno permission")

def runas(player, cmd):
  server.dispatchCommand(player, cmd)

def isPlayer(sender):
  return (isinstance(sender, Player))

def checkargs(sender, args, min, max):
  if not (len(args) >= min and (max < 0 or len(args) <= max)):
    if min == max:
      msg(sender, "&cNeeds " + str(min) + " arguments!")
      return False
    elif max < 0:
      msg(sender, "&cNeeds at least " + str(min) + " arguments!")
      return False
    else:
      msg(sender, "&cNeeds " + str(min) + " to " + str(max) + " arguments!")
      return False
  return True


def warp(sender, args, warpname):
  if not checkargs(sender, args, 0, 1):
    return True
  runas(sender, " ".join(["warp", warpname, sender.getName()]))
  return True
