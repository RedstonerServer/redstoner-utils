from helpers import *
from basecommands import simplecommand, Validate
import org.bukkit.Material as Material
import java.util.UUID as UUID
import org.bukkit.Material as Material
import java.util.HashSet as JSet


cmd_use_perm = "utils.svs.cmd"
msg_use_perm = "utils.svs.msg"

signs = open_json_file("serversigns", {}) # {("world", x, y, z): ["owner_id", "msg1", "msg2"]}

lines = {} #Accumulated messages so players can have longer messages: {"Dico200": "Message...........", ""}

transparent_blocks_set = JSet([Material.AIR, Material.GLASS, Material.STAINED_GLASS]) #used in sender.getTargetBlock()

@simplecommand(cmd = "serversigns", aliases = ["svs", "signmsg"],
    description = "Makes something happen when you right click certain signs",
    usage = "[claim|unclaim|add <msg>|remove <line>|clear|info|help]",
    helpNoargs = True,
    senderLimit = 0)
def svs_command(sender, command, label, args):
    try:
        arg1 = args[0].lower()
        if arg1 not in ("add", "remove", "clear", "claim", "unclaim", "help"):
            return "&4That argument could not be recognized, use &o/svs &4help for more information"

        sender = server.getPlayer(sender.getName())
        block = sender.getTargetBlock(transparent_blocks_set, 8)
        info("Block type: " + str(block.getType()))
        if block.getType() not in (Material.SIGN_POST, Material.WALL_SIGN):
            return "&4You have to be looking at a sign to use that!"

        loc      = fromLoc(block.getLocation())
        sign     = getSign(loc)
        arglen   = len(args)
        arg2 = args[1].lower() if arglen > 1 else None


        if arg1 == "claim":
            Validate.isAuthorized(sender, "utils.serversigns.claim")
            target = sender
            if arg2:
                Validate.isAuthorized(sender, "utils.serversigns.admin")
                target = server.getOfflinePlayer(arg2)
                Validate.notNone(target, signsMsg("That player could not be found", '4'))

            Validate.isPlayer(target)
            uuid = uid(sender)
            if sign != None:
                if sign[0] == uuid:
                    return signsMsg(identifySign(loc, True) + " was already owned by that player", '4')
                else:
                    sign[0] = uuid
            else:
                signs[loc] = [uuid]

            return signsMsg("Claimed " + identifySign(loc))


        elif arg1 == "unclaim":
            Validate.isAuthorized(sender, "utils.serversigns.unclaim")
            Validate.isTrue(canEdit(sign, sender), signsMsg("You cannot unclaim the %s!" % identifySign(loc)), '4')

            if not (("-c" in args) and sender.hasPermission("utils.serversigns.admin")):
                del signs[locAt]
                return signsMsg("The %s was reset successfully" % identifySign(loc))
            sign[0] = ""
            return signsMsg("The %s had its owner removed successfully" % identifySign(loc))


        elif arg1 == "help":
            admin = sender.hasPermission("utils.serversigns.admin")

            return


        elif arg1 == "add":
            Validate.isTrue(canEdit(sign, sender), signsMsg("You cannot edit the %s!" % identifySign(loc)), '4')
            line = " ".join(args[1:])
            Validate.isTrue(line != "" and line != None, signsMsg("You have to enter a message to add or accumulate!", '4'))
            key  = sender.getName()

            Validate.isTrue(key in lines or line[:1] != "/" or sender.hasPermission("utils.serversigns.command"), signsMsg("You cannot add commands to a sign!", '4'))

            if line[-2:] == "++":
                if key not in lines:
                    lines[key] = ""
                lines[key] += " " + line[:-2]
            elif key in lines:
                line = lines[key] + " " + line
            sign.append(colorify(line) if line[0] != "/" else line)
            return signsMsg("Added line \"%s&a\" to the %s" % (line, identifySign(loc)))


        elif arg1 == "info":
            Validate.notNone(sign, signsMsg("The %s has not been claimed" % identifySign(loc), '4'))
            lines = ""
            for id, line in enumerate(sign[1:]):
                lines += ("\n &a%s: \"%s&a\"" % (id + 1, line))
            msg = signsMsg("Some information about the %s:\n Owner: %s\n Lines: %s" % identifySign(loc), getOwner(sign), lines)


        elif arg1 == "remove":
            Validate.notNone(arg2, signsMsg("You have to enter the ID of the message to remove!", '4'))
            try:
                id = int(arg2)
            except:
                return signsMsg("The ID of the message has to be a number and can be found by using &o/svs info", '4')
            Validate.isTrue(id != 0 and id < len(sign), signsMsg("The %s has no message with an ID of %s, use &o/svs info &4for all messages." % (identifySign(loc), id), '4'))
            sign.remove(id)
            return signsMsg("Removed message with id %s from the %s" % (id, identifySign(loc)))
    except:
        error(trace())



@hook.event("player.PlayerInteractEvent")
def onClick(event):
    if str(event.getAction()) != "RIGHT_CLICK_BLOCK":
        return
    block = event.getClickedBlock()
    if block.getType() not in (Material.WALL_SIGN, Material.SIGN_POST):
        return
    sign = getSign(fromLoc(block.getLocation()))
    if sign != None:
        player = event.getPlayer()
        for message in sign[1:]:
            if message[:1] == "/":
                server.dispatchCommand(player, message[1:])
            else:
                msg(player, message, usecolor = False)

def fromLoc(bLoc): #Bukkit Location to ("world", x, y, z)
    return (bLoc.getWorld().getName(), bLoc.getBlockX(), bLoc.getBlockY(), bLoc.getBlockZ())

def equals(loc1, loc2):
    for i in range(4):
        if loc1[i] != loc2[i]:
            return False
    return True

def getOwner(sign):
    return retrieve_player(sign[0]).getName()

def isOwner(sign, player):
    return sign and sign[0] == uid(player)

def canEdit(sign, player):
    return player.hasPermission("utils.serversigns.admin") or isOwner(sign, player)

def getSign(locAt):
    for loc, sign in signs.iteritems():
        if equals(locAt, loc):
            return sign
    return None

def identifySign(loc, capital = False):
    return "%sign at (%s) in %s" % ("S" if capital else "s", ",".join(loc[1:]), loc[0])

def signsMsg(msg, colour = 'a'):
    return "&c[Signs] &" + colour + msg






"""
def eventhook(event, priority = "normal"):

    if "." not in event:
        word = ""
        for s in event:
            if word != "" and s in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
                break;
            word += s.lower()
        event = "%s.%s" % (word, event)

    def decorator(function):

        @hook.event(event, priority)
        def hook(event):
            try:
                function(event)
            except EventException, e:
                pass

        return hook

    return decorator

class EventException(Exception):
    def __init__(self, msg):
        self.msg = msg

""
@eventhook("PlayerInteractEvent")
def x(event):

    p = event.getPlayer()
    if p == None:
        raise EventException(Stuff)
""
"""















