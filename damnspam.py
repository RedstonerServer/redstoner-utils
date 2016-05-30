#pylint: disable = F0401
from helpers import *
from time import time as now
import org.bukkit.Material as Material
import org.bukkit.block.BlockFace as BlockFace

inputs          = open_json_file("damnspam", {}) # format "x;y;z;World"
accepted_inputs = ["WOOD_BUTTON", "STONE_BUTTON", "LEVER"]
changing_input  = False
removing_input  = False
max_timeout     = 240
timeout_error_str = "&cThe timeout must be -1 or within 0 and %d" % max_timeout


def save_inputs():
    save_json_file("damnspam", inputs)


def location_str(block):
    return ";".join([block.getWorld().getName(), str(block.getX()), str(block.getY()), str(block.getZ())])


def add_input(creator, block, timeout_off, timeout_on):
    inputs[location_str(block)] = {
        "creator"     : uid(creator),
        "timeout_off" : timeout_off,
        "timeout_on"  : timeout_on,
        "last_time"   : 0
    }


def is_acceptable_timeout(timeout):
    return (0 < timeout <= max_timeout) or timeout == -1


@hook.command("damnspam")
def on_dammnspam_command(sender, command, label, args):
    plugin_header(sender, "DamnSpam")

    if not checkargs(sender, args, 1, 2):
        msg(sender, "&c/damnspam <seconds> &e(Buttons/Levers)")
        msg(sender, "&c/damnspam <seconds after off> <seconds after on> &e(Levers only)")
        return True
        #Gittestlol
    if not is_creative(sender):
        msg(sender, "&cYou can only do this in Creative mode")
        return True

    # /damnspam <secs>
    destroying_input = False # if both timeouts are 0, the plugin will attempt to remove the protection
    if len(args) == 1:
        timeout_on = args[0]
        try:
            timeout_on  = round(float(timeout_on), 2)
            if timeout_on == 0:
                destroying_input = True
            elif not is_acceptable_timeout(timeout_on):
                msg(sender, "&cThe timeout must be -1 or within 0 and %d" % max_timeout)
                return True
            timeout_off = timeout_on
        except ValueError:
            msg(sender, "&cThe timeout must be a number")
            return True

    # /damnspam <off> <on>
    elif len(args) == 2:
        timeout_on  = args[0]
        timeout_off = args[1]
        try:
            timeout_on  = round(float(timeout_on), 2)
            timeout_off = round(float(timeout_off), 2)
            if timeout_on == 0 and timeout_off == 0:
                destroying_input = True
            elif not (is_acceptable_timeout(timeout_on) and is_acceptable_timeout(timeout_off)):
                msg(sender, "&cThe timeout must be -1 or within 0 and %d" % max_timeout)
                return True
        except ValueError:
            msg(sender, "&cThe timeout must be a number")
            return True

    # get the block we're looking at
    target = sender.getTargetBlock(None, 10)
    ttype  = str(target.getType())
    if ttype not in accepted_inputs:
        msg(sender, "&cPlease look at a button or lever while executing this command!")
        return True

    global changing_input
    target_loc_str = location_str(target)
    if target_loc_str in inputs:
        changing_input = True # this input already has a timeout

    type_str = ttype.lower().replace("_", " ")

    # test if player is allowed to build here
    build_check = can_build(sender, target)
    changing_input = False
    if not build_check:
        msg(sender, "&cYou are not allowed to modify this %s" % type_str)
        return True

    # add block to inputs
    if destroying_input:
        if target_loc_str not in inputs:
            msg(sender, "&cThere is no timeout to remove on this %s (by setting the timeout to 0)" % type_str)
            return True
        del inputs[target_loc_str]
        msg(sender, "&aSuccessfully removed the timeout for this %s" % type_str)
    else:
        add_input(sender, target, timeout_off, timeout_on)
        msg(sender, "&aSuccessfully set a timeout for this %s" % type_str)
    save_inputs()
    return True


def check_block_break(break_event, block):
    if str(block.getType()) not in accepted_inputs:
        return
    pos_str = location_str(block)
    if pos_str not in inputs:
        return
    sender = break_event.getPlayer()
    input_str = ("this %s" if block is break_event.getBlock() else "the %s attached to that block") % str(block.getType()).lower().replace("_", " ")
    if not sender.isSneaking():
        msg(sender, "&cYou cannot destroy " + input_str)
        msg(sender, "&c&nSneak&c and break or set the timeout to 0 if you want to remove it.")
        break_event.setCancelled(True)
        return
    global removing_input
    removing_input = True
    success = can_build(sender, block)
    removing_input = False
    if success:
        del inputs[pos_str]
        save_inputs()
        msg(sender, "&aSuccessfully removed %s!" % input_str)
    else:
        msg(sender, "&cYou are not allowed to remove " + input_str)
        break_event.setCancelled(True)


# a dict for levers and buttons, with a tuple of tuples as value. The tuples in the tuple represent
# the data values which the block must have if the block were placed towards the linked blockface to be affected.
# The order is DOWN, UP, NORTH, SOUTH, WEST, EAST
attached_blocks = {

    Material.LEVER: ((0, 7, 8, 15), (5, 6, 13, 14), (4, 12), (3, 11), (2, 10), (1, 9)),
    Material.STONE_BUTTON: ((0, 8), (5, 6, 7, 13, 14, 15), (4, 12), (3, 11), (2, 10), (1, 9)),
    Material.WOOD_BUTTON: ((0, 8), (5, 6, 7, 13, 14, 15), (4, 12), (3, 11), (2, 10), (1, 9)),

}

# returns a generator containing the levers or buttons that would be broken if this block were broken
def get_attached_blocks(block):
    for i, face in ((0, BlockFace.DOWN), (1, BlockFace.UP), (2, BlockFace.NORTH), (3, BlockFace.SOUTH), (4, BlockFace.WEST), (5, BlockFace.EAST)):
        side = block.getRelative(face)
        dvalues = attached_blocks.get(side.getType())
        if dvalues is not None and side.getData() in dvalues[i]:
            yield side


@hook.event("block.BlockBreakEvent", "highest")
def on_block_break(event):
    try:
        if removing_input or changing_input or event.isCancelled():
            return
        block = event.getBlock()
        check_block_break(event, event.getBlock())
        for affected_block in get_attached_blocks(block):
            check_block_break(event, affected_block)
    except:
        error(trace())


@hook.event("player.PlayerInteractEvent", "normal")
def on_interact(event):
    if (str(event.getAction()) == "RIGHT_CLICK_BLOCK") and not event.isCancelled():
        sender = event.getPlayer()
        if sender.isSneaking():
            return
        block   = event.getClickedBlock()
        pos_str = location_str(block)
        data    = inputs.get(pos_str)
        if data:
            sender = event.getPlayer()
            btype  = str(block.getType()).lower().replace("_", " ")
            if btype == "lever" and block.getData() < 8:
                checktime = data["timeout_off"]
            else:
                checktime = data["timeout_on"]
            time_left = data["last_time"] + checktime - now()

            if checktime == -1:
                event.setCancelled(True)
                msg(sender, "&cThis %s is locked permanently by /damnspam." % (btype))
            elif time_left > 0:
                event.setCancelled(True)
                msg(sender, "&cThis %s has a damnspam timeout of %.2fs, with %.2fs left." % (btype, checktime, time_left))
            else:
                data["last_time"] = round(now(), 2)
