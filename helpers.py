#pylint: disable = F0401

import org.bukkit as bukkit
import org.bukkit.block as bblock
import org.bukkit.Location as Location
import org.bukkit.event.entity as entity
import org.bukkit.entity.Player as Player
import org.bukkit.command.ConsoleCommandSender
import org.bukkit.event.block.BlockBreakEvent as BlockBreakEvent
import org.bukkit.event.player.PlayerTeleportEvent.TeleportCause as TeleportCause

from re import sub
from thread_utils import *
from player import py_players
from org.bukkit.entity import *
from player import get_py_player
from traceback import format_exc as trace
from java.util.UUID import fromString as juuid
from json import dumps as json_dumps, loads as json_loads

#Imports for async query
import threading
import mysqlhack

from secrets import *
from com.ziclix.python.sql import zxJDBC



shared = {} # this dict can be used to share stuff across modules

server = bukkit.Bukkit.getServer()


def info(text):
    """
    Log info to console
    """
    server.getLogger().info("[RedstonerUtils] %s" % text)


def warn(text):
    """
    Log warning to console
    """
    server.getLogger().warning("[RedstonerUtils] %s" % text)


def error(text):
    """
    Log error to console
    """
    server.getLogger().severe("[RedstonerUtils] %s" % text)


def fine(text):
    """
    Log anything to the logs alone, not the console
    """
    server.getLogger().fine(text)

def msg(player, text, usecolor = True, basecolor = None):
    """
    send a message to player
    the player may be None or offline, which this method just ignores
    unless usecolor is False, &-codes are translated to real color codes
    for that case, basecolor can be useful. basecolor accepts a single character as color code
    """
    if player and (player == server.getConsoleSender() or player.isOnline()): # getPlayer() returns None when offline
        if basecolor:
            if usecolor:
                text = colorify(text)
            player.sendMessage(colorify("&%s" % basecolor) + text)
        else:
            player.sendMessage(colorify(text) if usecolor else text)


def broadcast(perm, text, usecolor = True):
    """
    better than bukkit's broadcast.
    bukkit only works with permissibles that are subscribed to perm
    """
    if usecolor:
        text = colorify(text)
    for recipient in list(server.getOnlinePlayers()) + [server.getConsoleSender()]:
        if not perm or recipient.hasPermission(perm):
            msg(recipient, text, usecolor = False)


def colorify(text):
    """
    replace &-codes with real color codes
    """
    return sub("&" + u"\u00A7", "&", "%s" % sub("&(?=[?\\da-fk-or])", u"\u00A7", "%s" % text))


def stripcolors(text):
    """
    strips all (real) color codes from text
    """
    return sub(u"\u00A7[\\da-fk-or]", "", "%s" % text)


def safetp(player, world, x, y, z, yaw = 0, pitch = 0):
    """
    teleports the player to the given Location
    if the player would spawn inside blocks, the location is escalated until the location is safe
    """
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
    """
    Send the default permission failure message to the player
    """
    msg(player, "&cno permission")


def runas(player, cmd):
    """
    run a command as player
    the cmd should NOT be prefixed with a /
    """
    if is_player(player):
        player.chat("/" + cmd)
    else:
        server.dispatchCommand(player, cmd)


def is_player(obj):
    """
    return True when ob is a bukkit Player
    """
    return (isinstance(obj, Player))


def can_build(player, block):
    """
    return True if the player can change/build at the location of given block
    """
    event = BlockBreakEvent(block, player)
    server.getPluginManager().callEvent(event)
    return not event.isCancelled()


def checkargs(sender, args, amin, amax):
    """
    check if a command has a valid amount of args, otherwise notify the sender
    amin is the minimum amount of args
    amax is the maximum amount of args
    if amax is < 0, infinite args will be accepted
    return True if args has a valid length, False otherwise
    """
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


def is_creative(player):
    """
    returns True if the player is in Creative mode
    """
    return str(player.getGameMode()) == "CREATIVE"


def is_rank(player, rank):
    """
    rank: a string equal to the PEX group name found in /pex groups
    returns True if one of the following conditions are met:
    - the player is of the given rank,
    - their rank inherits the given rank.
    """
    return player.hasPermission("groups." + rank)


def uid(player):
    """
    returns the player's UUID
    """
    return str(player.getUniqueId())


def retrieve_player(uuid_str):
    """
    gets an offline player by UUID string
    the uuid MUST contain dashes
    """
    return server.getOfflinePlayer(juuid(uuid_str))


def known_player(player):
    """
    to be used on OfflinePlayer (which can be online!)
    returns True if the player has been on the server
    this is different to HasPlayedBefore(), which will return False on first join
    """
    return player.hasPlayedBefore()

def open_json_file(filename, default = None):
    """
    opens the given json file and returns an object or returns None on error
    filename is only the name of the file without .json appended.
    """
    try:
        with open("plugins/redstoner-utils.py.dir/files/%s.json" % filename) as obj:
            default = json_loads(obj.read())
    except Exception, e:
        error("Failed to read from %s: %s" % (filename, e))
    return default


def save_json_file(filename, obj):
    """
    saves the given object as json into filename
    filename is only the name of the file without .json appended.
    """
    try:
        with open("plugins/redstoner-utils.py.dir/files/%s.json" % filename, "w") as f:
            f.write(json_dumps(obj))
    except Exception, e:
        error("Failed to write to %s: %s" % (filename, e))


def toggle(player, ls, name = "Toggle", add = None):
    """
    Toggles presence of a player's UUID in a list
    If add is given, True explicitely adds it whereas False removes it
    """
    pid = uid(player)
    if pid in ls or add == False:
        ls.remove(pid)
        msg(player, "&a%s turned off!" % name)
    elif add != False:
        ls.append(pid)
        msg(player, "&a%s turned on!" % name)

def send_JSON_message(playername, message):
    bukkit.Bukkit.getServer().dispatchCommand(bukkit.Bukkit.getServer().getConsoleSender(), "tellraw " + playername + " " + message)


def isIP(tocheck):
    subsets = ["","","",""]
    i = 0
    for j in range(0,len(tocheck)):
        if not (tocheck[j] in "0123456789."):
            return False
        elif tocheck[j] == ".":
            i += 1
            if (i >= 4):
                return False
        else:
            subsets[i] +=  tocheck[j]
    if not (i == 3):
        return False
    for j in range(0,3):
        if not ((int(subsets[j]) >= 0) & (int(subsets[j]) <= 255)):
            return False
    return True
