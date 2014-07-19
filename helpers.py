#pylint: disable = F0401
from re import sub
from java.util.UUID import fromString as id_to_player
import org.bukkit as bukkit
import org.bukkit.Location as Location
import org.bukkit.entity.Player as Player
import org.bukkit.event.player.PlayerTeleportEvent.TeleportCause as TeleportCause
import org.bukkit.block as bblock
from json import dumps as json_dumps, loads as json_loads


shared = {} # this dict can be used to share stuff across modules

server = bukkit.Bukkit.getServer()


def log(text):
  server.getLogger().info("[RedstonerUtils] %s" % colorify(text))


def error(text):
  server.getLogger().severe("[RedstonerUtils] %s" % text)


def msg(player, text, usecolor = True, basecolor = None):
  if player and (player == server.getConsoleSender() or player.getPlayer()): # getPlayer() returns None when offline
    if basecolor:
      player.sendMessage(colorify("&%s" % basecolor) + (colorify(text) if usecolor else text))
    else:
      player.sendMessage(colorify(text) if usecolor else text)


def broadcast(perm, text):
  """
  better than bukkit's broadcast.
  bukkit only works with permissibles that are subscribed to perm
  """
  text = colorify(text)
  for recipient in list(server.getOnlinePlayers()) + [server.getConsoleSender()]:
    (not perm or recipient.hasPermission(perm)) and msg(recipient, text)


def colorify(text):
  return sub("&(?=[?\\da-fk-or])", u"\u00A7", "%s" % text)


def stripcolors(text):
  return sub(u"\u00A7[\\da-fk-or]", "", "%s" % text)


def safetp(player, world, x, y, z, yaw = 0, pitch = 0):
  tpblock = Location(world, x, y, z).getBlock()
  if (tpblock.isEmpty() and tpblock.getRelative(bblock.BlockFace.UP).isEmpty()) or y > 255:
    player.teleport(Location(world, x+0.5, y, z+0.5, yaw, pitch), TeleportCause.COMMAND)
  else:
    safetp(player, world, x, y+1, z, yaw, pitch)


def plugin_header(recipient = None, name="Redstoner Utils"):
  """
  sends the recipient a "Plugin Header", in the format of: --=[ PluginName ]=--
  """

  head = "\n&2--=[ %s ]=--" % name
  msg(recipient, head)
  return head


def noperm(player):
  msg(player, "&cno permission")


def runas(player, cmd):
  server.dispatchCommand(player, cmd)


def is_player(obj):
  return (isinstance(obj, Player))


def checkargs(sender, args, amin, amax):
  if not (len(args) >= amin and (amax < 0 or len(args) <= amax)):
    if amin == amax:
      msg(sender, "&cNeeds " + str(amin) + " arguments!")
      return False
    elif amax < 0:
      msg(sender, "&cNeeds at least " + str(amin) + " arguments!")
      return False
    else:
      msg(sender, "&cNeeds " + str(amin) + " to " + str(amax) + " arguments!")
      return False
  return True


def warp(player, args, warpname):
  if not checkargs(player, args, 0, 1):
    return False # You can check if it worked
  runas(player, "warp %s" % warpname)
  return True
""" Changed to this, from runas(player, " ".join(["warp", warpname])) because it doesnt make sense
to make the player add its own name to the command to warp that name which is the same player """


def is_creative(player):
  return str(player.getGameMode()) == "CREATIVE"


def uid(player):
  return str(player.getUniqueId())


def retrieve_player(uid):
  return server.getOfflinePlayer(id_to_player(uid))


def open_json_file(json_filename): # json file is the path + name to the file
  try:
    with open(json_file) as obj:
      return json_loads(obj.read())
  except Exception, reading_error:
    error("Failed to read from %s: %s" % (json_file, str(reading_error)))


def save_json_file(json_filename, json_object): # json file is the path + name to the file, json_object is the variable you want to write to the file.
  try:
    with open(json_file) as obj:
      obj.write(json_dumps(json_object))
  except Exception, writing_error:
    error("Failed to write to %s: %s" % (json_file, str(writing_error)))