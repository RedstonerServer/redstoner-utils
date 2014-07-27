#pylint: disable = F0401
from re import sub
from java.util.UUID import fromString as juuid
from json import dumps as json_dumps, loads as json_loads
import org.bukkit as bukkit
import org.bukkit.Location as Location
import org.bukkit.entity.Player as Player
import org.bukkit.event.player.PlayerTeleportEvent.TeleportCause as TeleportCause
import org.bukkit.block as bblock


shared = {} # this dict can be used to share stuff across modules

server = bukkit.Bukkit.getServer()


def log(text):
  server.getLogger().info("[RedstonerUtils] %s" % text)


def warn(text):
  server.getLogger().warning("[RedstonerUtils] %s" % text)


def error(text):
  server.getLogger().severe("[RedstonerUtils] %s" % text)


def msg(player, text, usecolor = True, basecolor = None):
  if player and (player == server.getConsoleSender() or player.getPlayer()): # getPlayer() returns None when offline
    if basecolor:
      if usecolor:
        text = colorify(text)
      player.sendMessage(colorify("&%s" % basecolor) + text)
    else:
      player.sendMessage(colorify(text) if usecolor else text)


def broadcast(perm, text):
  """
  better than bukkit's broadcast.
  bukkit only works with permissibles that are subscribed to perm
  """
  text = colorify(text)
  for recipient in list(server.getOnlinePlayers()) + [server.getConsoleSender()]:
    if not perm or recipient.hasPermission(perm):
      msg(recipient, text)


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


def retrieve_player(uuid):
  return server.getOfflinePlayer(juuid(uuid))


def played_before(player):
  if player.getFirstPlayed() == 0:
    return False
  return True


def open_json_file(filename, default):
  """
  opens the given json file and returns an object or returns None on error
  filename is the path + name of the file.
  """
  data = None
  try:
    with open("plugins/redstoner-utils.py.dir/files/%s.json" % filename) as obj:
      data = json_loads(obj.read())
  except Exception, e:
    error("Failed to read from %s: %s" % (filename, e))
  return (default if data is None else data)


def save_json_file(filename, obj):
  """
  saves the given object as json into filename
  filename is the path + name of the file.
  """
  try:
    with open("plugins/redstoner-utils.py.dir/files/%s.json" % filename, "w") as f:
      f.write(json_dumps(obj))
  except Exception, e:
    error("Failed to write to %s: %s" % (filename, e))


def toggle(player, ls, add = None, on = "&aToggle now on!", off = "&cToggle now off!", already = "&cToggle was already %s"):
  """
  Toggle presence of a player's UUID in a list (ls)
  'add' controls if a player should be added(True) or removed(False)
  if 'add' is None, ls will simply be toggled for that player.
  when 'add' is given, but won't change anything, %s in 'already' is replaced with "ON" or "OFF"
  """

  pid     = uid(player)
  enabled = pid in ls

  # Do some checks and remove pid.
  if enabled and add == False:
    ls.remove(pid)
    msg(player, on)

  # Do some checks and append pid.
  elif not enabled and add == True:
    ls.append(pid)
    msg(player, off)

  # Already on/off (optional)
  else:
    msg(player, already % (" ON" if add else " OFF"))
