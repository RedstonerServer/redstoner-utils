#pylint: disable = F0401
from re import sub
from java.util.UUID import fromString as juuid
from json import dumps as json_dumps, loads as json_loads
import org.bukkit as bukkit
import org.bukkit.Location as Location
import org.bukkit.entity.Player as Player
import org.bukkit.event.player.PlayerTeleportEvent.TeleportCause as TeleportCause
import org.bukkit.block as bblock
import org.bukkit.event.entity as entity
import org.bukkit.command.ConsoleCommandSender
from org.bukkit.entity import *

from traceback import format_exc as trace


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


def msg(player, text, usecolor = True, basecolor = None):
    """
    send a message to player
    the player may be None or offline, which this method just ignores
    unless usecolor is False, &-codes are translated to real color codes
    for that case, basecolor can be useful. basecolor accepts a single character as color code
    """
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
    """
    replace &-codes with real color codes
    """
    return sub("&(?=[?\\da-fk-or])", u"\u00A7", "%s" % text)


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
    player.chat("/" + cmd)
    

def is_player(obj):
    """
    return True when ob is a bukkit Player
    """
    return (isinstance(obj, Player))


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






"""
Use this instead of @hook.command for your command methods. (@simplecommand(things...))

It will take care of the following things:
- Basic permission check. The default permission is utils.<cmd_name>
- Sender type check. You can pass whether the sender must be a player, a consolesender, or both. (see sender_limit below)
- Minimum and maximum args. Works with checkargs from helpers.py.
- A '/<cmd> help' message containing the description, usage and aliases of the command.

Information about some arguments:
- cmd_name:         The command you type in chat.
- usage:            For example "<player> <other_player" and is part of the help message.
- description:      A brief description of what the command does. (also part of the help message)
- aliases:          A list of aliases for the command
- permission:       The basic permission for the command. Defaults to utils.<cmd>
- sender_limit:     Defines what sendertype can use the command. Leave blank for console & player, 0 for player only, 1 for console only.
- min_args:         The least arguments for the command.
- max_args:         You guessed it right. Defaults to infinity (-1).

*** DISCLAIMER ***

Your command function must take four arguments: sender, command, label, args.

Your function must also not return a boolean like before, but a String instead. The string returned will be sent to the player (&-codes supported).
Use None or "" for no message.

Feel free to edit or give suggestions (but don't break existing commands)

See below for an example command.
"""

def simplecommand(cmd_name, aliases = [], permission = None, usage = None, description = None, sender_limit = -1, min_args = 0, max_args = -1):
    cmd_name = cmd_name.lower()
    if not permission:
        permission = "utils." + cmd_name
    if not usage:
        usage = "[args...]"
    if not description:
        description = "Handles " + cmd_name

    def actualDecorator(function):

        @hook.command(cmd_name, aliases = aliases)
        def __call_func__(sender, command, label, args):
            try:
                message = __run__(sender, command, label, args)
                if message:
                    msg(sender, message)
            except:
                error(trace())

        def __run__(sender, command, label, args):
            isplayer = is_player(sender)
            if not is_sender_valid(isplayer):
                return "&cThis command can only be run from the console" if isplayer else "&cThis command can only be run by players"
            if not sender.hasPermission(permission):
                return "&cYou do not have permission to use this command"
            if not checkargs(sender, args, min_args, max_args):
                return None
            return help_message(sender) if args and args[0].lower() == "help" else function(sender, command, label, args)

        return __call_func__

    def is_sender_valid(isplayer):
        return True if sender_limit == -1 else sender_limit != isplayer

    def help_message(sender):
        """
        Information about command /<cmd>:       #Light green
            description...                      #Blue
            description...                      #Blue

        Syntax: /<cmd> <usage>                  #Light green
        Aliases: alias1, alias2, alias3         #Gold
        """
        try:
            help_msg  = "&aInformation about command /%s:\n    &9%s" % (cmd_name, description.replace("\n", "\n    "))
            help_msg += "\n\n&aSyntax: &o/%s %s" % (cmd_name, usage)
            if aliases:
                help_msg += ("\n&6Aliases: " + "".join([(alias + ", ") for alias in aliases]))[:-2]
            return help_msg
        except:
            error(trace())

    return actualDecorator


"""
@simplecommand("test", usage = "<player>", description = "Kicks a player", aliases = ["kickp", "tek"], permission = "utils.kickuser", sender_limit = 0, min_args = 1, max_args = 2)
def on_test(sender, command, label, args):
    target = server.getPlayer(args[0]);
    if target:
        target.kickPlayer("Kicked from the server")
        return None
    return "&cThat player could not be found"
"""
