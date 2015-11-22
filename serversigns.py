from helpers import *
from basecommands import simplecommand, Validate
import org.bukkit.Material as Material
import java.util.UUID as UUID
import org.bukkit.Material as Material
import org.bukkit.block.BlockFace as BlockFace

blocked_cmds = ("pex", "kick", "ban", "tempban", "pyeval", "sudo")

def load_signs():
    signs_obj = open_json_file("serversigns", [])
    loaded = {}
    for entry in signs_obj:
        loaded[tuple(entry[:4])] = list(entry[4:])
    return loaded

def save_signs():
    signs_obj = []
    for key, value in signs.iteritems():
        signs_obj.append(key + tuple(value))
    save_json_file("serversigns", signs_obj)

signs = load_signs() # {("world", x, y, z): ["owner_id", "msg1", "msg2"]}

lines = {} # Accumulated messages so players can have longer messages: {"Dico200": "Message...........", ""}

def fromLoc(bLoc):
    """
      # Returns a tuple containing the (bukkit)location's world's name and its x, y and z coordinates
      # The format for the tuple is ("world_name", x, y, z)
    """
    return (bLoc.getWorld().getName(), bLoc.getBlockX(), bLoc.getBlockY(), bLoc.getBlockZ())

def equals(loc1, loc2):
    """
      # Returns whether loc1 and loc2 represent the same block
    """
    for i in range(4):
        if loc1[i] != loc2[i]:
            return False
    return True

def getOwner(sign):
    """
      # Returns the name of the sign its owner
    """
    return retrieve_player(sign[0]).getName()

def isOwner(sign, player):
    """
      # Returns whether the given player owns the sign
    """ 
    return sign and sign[0] == uid(player)

def canEdit(sign, player):
    """ 
      # Returns whether the given player can edit the sign.
      # Returns False if the sign wasn't claimed.
    """
    return (sign and player.hasPermission("utils.serversigns.admin")) or isOwner(sign, player)

def getSign(locAt):
    """
      # If data was found for a sign at the given location, returns the data.
      # This data follows the format of ["owner_id", "msg1", "msg2"...].
    """
    for loc, sign in signs.iteritems():
        if equals(locAt, loc):
            return sign
    return None

def identifySign(loc):
    """
      # Returns a string from which the user can tell what sign you're talking about.
      # The string follows the format of "sign at (x,y,z) in world_name".
    """
    return "sign at (%s) in %s" % (",".join((str(i) for i in loc[1:])), loc[0])

def signsMsg(msg, colour = '4'):
    """
      # Returns the given msg, prefixed with '[Signs] '.
      # The given colour is after applied to the msg.
      # The colour defaults to 4 (dark red).
    """
    return "&c[Signs] &" + colour + msg


@simplecommand(cmd = "serversigns", aliases = ["svs", "signmsg"],
    description = "Makes something happen when you right click certain signs",
    usage = "[claim|unclaim|add <msg>|remove <line>|clear|info|help]",
    helpNoargs = True,
    senderLimit = 0)
def svs_command(sender, command, label, args):
    arg1 = args[0].lower()
    Validate.isTrue(arg1 in ("claim", "reset", "add", "remove", "info", "clear", "help", "switch"), signsMsg("That argument could not be recognized, use &o/svs help &4for expected arguments"))
    Validate.isAuthorized(sender, "utils.serversigns." + arg1)

    #-------------------- Sub commands that don't require any conditions -----------------------
    if arg1 == "help":
        admin = sender.hasPermission("utils.serversigns.admin")

        return "&2COMMAND HELP HERE"
    #-------------------------------------------------------------------------------------------

    block = sender.getTargetBlock(None, 5)
    Validate.isTrue(block.getType() in (Material.SIGN_POST, Material.WALL_SIGN), signsMsg("You have to be looking at a sign to use that!"))

    loc      = fromLoc(block.getLocation())
    sign     = getSign(loc)
    signName = identifySign(loc)
    arg2     = args[1].lower() if len(args) > 1 else None
    is_admin = sender.hasPermission("utils.serversigns.admin")

    #------------------------ Sub commands that require the block to be a sign -------------------------------
    if arg1 == "claim":
        target = sender
        if arg2:
            Validate.isTrue(is_admin, signsMsg("You are not authorized to claim signs for other players"))
            target = server.getOfflinePlayer(arg2)
            Validate.notNone(target, signsMsg("That player could not be found"))
            Validate.isTrue(target.isOnline(), signsMsg("The target has to be online"))
        uuid = uid(target)
        if sign != None:
            if sign[0] == uuid:
                return signsMsg("The" + signName + " was already owned by that player")
            else:
                sign[0] = uuid
        else:
            signs[loc] = [uuid]
        save_signs()
        return signsMsg("Claimed the " + signName + ((" for %s" % target.getName()) if (target != sender) else ""), 'a')
    #----------------------------------------------------------------------------------------------------------

    Validate.notNone(sign, signsMsg("The %s has not been claimed" % signName))

    #----------------------Sub commands that require the sign to be claimed as well------------------------------------
    if arg1 == "info":
        sign_lines = ""
        for id, line in enumerate(sign[1:]):
            sign_lines += ("\n &a%s: \"&f%s&a\"" % (id + 1, line))
        return signsMsg("Properties of the %s:\n Owner: %s\n Lines: %s" % (signName, getOwner(sign), sign_lines), 'a')
    #---------------------------------------------------------------------------------------------------------------

    Validate.isTrue(canEdit(sign, sender), signsMsg("You do not own the %s!" % signName))

    #---------------------- Sub commands that require you to own targeted sign as well -------------------------
    if arg1 == "add":
        line = " ".join(args[1:])
        Validate.isTrue(line != "" and line != None, signsMsg("You have to enter a message to add or accumulate"))
        key  = sender.getName()
        global lines
        Validate.isTrue(key in lines or line[:1] != "/" or sender.hasPermission("utils.serversigns.command"), signsMsg("You cannot add commands to a sign!"))
        if line[-2:] == "++":
            if key not in lines:
                lines[key] = ""
            lines[key] += " " + line[:-2]
            return signsMsg("Added given message to the message you're accumulating. \nYour accumulated message is now as follows: \n&f%s" % lines[key], 'a')
        if key in lines:
            line = (lines[key] + " " + line)[1:]
        Validate.isTrue(line[0] != "/" or line.split(" ")[0][1:] not in blocked_cmds, signsMsg("Usage of that command with server signs is prohibited"))
        sign.append(colorify(line) if line[0] != "/" else line)
        save_signs()
        return signsMsg("Added line \"&f%s&a\" to the %s" % (line, signName), 'a')


    if arg1 == "remove":
        Validate.notNone(arg2, signsMsg("You have to enter the ID of the message to remove!"))
        try:
            id = int(arg2)
        except:
            return signsMsg("The ID of the message has to be a number and can be found by using &o/svs info")
        Validate.isTrue(id != 0 and id < len(sign), signsMsg("The %s has no message with an ID of %s, use &o/svs info &4for all messages." % (signName, id)))
        sign.remove(id)
        return signsMsg("Removed message with id %s from the %s" % (id, signName), 'a')


    if arg1 == "switch":
        Validate.isTrue(len(args) == 3, signsMsg("You have to enter the 2 IDs of the lines to switch"))
        try:
            id1 = int(args[1])
            id2 = int(args[2])
        except:
            return signsMsg("The ID of the message has to be a number and can be found by using &o/svs info")
        for id in (id1, id2):
            Validate.isTrue(id != 0 and id < len(sign), signsMsg("The %s has no message with an ID of %s, use &o/svs info &4for all messages." % (signName, id)))
        sign[id1], sign[id2] = sign[id2], sign[id1]
        return signsMsg("Switched the lines with IDs %s and %s of the %s" % (id1, id2, signName), 'a')


    if arg1 == "clear":
        signs[loc] = [sign[0]]
        return signsMsg("Removed all messages from the %s" % signName, 'a')


    if arg1 == "reset":
        del signs[loc]
        return signsMsg("Removed all messages and the owner from the %s, it can now be claimed" % signName, 'a')
    #-------------------------------------------------------------------------------------------------------




@hook.event("player.PlayerInteractEvent")
def on_click(event):
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

# ---------------------------Sign breaking--------------------------------

checking_block = False

faces = {
    BlockFace.NORTH : (0,1,2),
    BlockFace.SOUTH : 3,
    BlockFace.WEST  : 4,
    BlockFace.EAST  : 5
}

@hook.event("block.BlockBreakEvent", "highest")
def on_break(event):
    global checking_block
    if checking_block or event.isCancelled():
        return

    block = event.getBlock()
    if block.getMaterial() in (Material.SIGN_POST, Material.WALL_SIGN):
        check_sign(event, block, attached = False)

    for block_face, data_values in faces.iteritems():
        block2 = block.getRelative(block_face)
        if block2.getData() in data_values:
            check_sign(event, block2)

    block3 = block.getRelative(BlockFace.UP)
    if block3.getMaterial == Material.SIGN_POST:
        check_sign(event, block3)


def check_sign(event, block, attached = True):
    player = event.getPlayer()
    sign = getSign(fromLoc(block.getLocation()))
    if not canEdit(sign, player) and not can_build(player, block.getLocation()):
            event.setCancelled(True)
            msg(event.getPlayer(), signsMsg("You cannot break %s" % ("the sign attached to that block" if attached else "that sign")))


def can_build(player, block):
    global checking_block
    event = BlockBreakEvent(block, player)
    checking_block = True
    server.getPluginManager().callEvent(event)
    checking_block = False
    return not event.isCancelled()

