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


def retrieve_player(uuid):
  return server.getOfflinePlayer(juuid(uuid))


def open_json_file(filename):
  """
  opens the given json file and returns an object or returns None on error
  filename is the path + name of the file.
  """
  try:
    with open(filename) as obj:
      return json_loads(obj.read())
  except Exception, e:
    error("Failed to read from %s: %s" % (filename, e))


def save_json_file(filename, obj):
  """
  saves the given object as json into filename
  filename is the path + name of the file.
  """
  try:
    with open(filename) as fyle:
      fyle.write(json_dumps(obj))
  except Exception, e:
    error("Failed to write to %s: %s" % (filename, e))


def toggle(player, variable, operation = None, messages = ["&aToggle now on!", "&cToggle now off!", "&cToggle was already %s"]):
  """
  Toggles if a player('s id) is in variable.
  messages[0] is displayed when it is turned on, messages[1] when off, and messages[2] when already of/on + "ON!" or "OFF!"
  if operation is True, player will be added, and if already added, it will receive messages[2] and %s will be replaced with "OFF!"
  if operation is False, player will be removed, and if already removed, it will receive messages[2] and %s will be replaced with "OFF"
  if operation is not given or None, variable will simply be toggled for that player.
  messages and operation are completely optional of course. There's a default!

  FYI, I checked in PyScripter if the variables is changed and it seems like it. I'm not entirely sure if it will
  transfer between modules though, but it should.
  http://puu.sh/ahAjr/6862c6e5a6.png Returns ["Hi"]
  """

  pid     = uid(player)
  enabled = pid in variable

  # Do some checks and remove pid.
  if enabled and not operation == True:
    variable.remove(pid)
    msg(player, messages[0])

  # Do some checks and append pid.
  elif not enabled and not operation == False:
    variable.append(pid)
    msg(player, messages[1])

  # Already on/off (optional)
  else:
    msg(player, messages[2] % (" ON" if operation == True else " OFF"))
