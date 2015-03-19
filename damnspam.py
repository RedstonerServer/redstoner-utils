#pylint: disable = F0401
from helpers import *
from time import time as now
import org.bukkit.event.block.BlockBreakEvent as BlockBreakEvent

inputs          = open_json_file("damnspam", {}) # format "x;y;z;World"
accepted_inputs = ["WOOD_BUTTON", "STONE_BUTTON", "LEVER"]
changing_input  = False
removing_input  = False


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


@hook.command("damnspam")
def on_dammnspam_command(sender, command, label, args):
    global changing_input

    plugin_header(sender, "DamnSpam")
    if not checkargs(sender, args, 1, 2):
        msg(sender, "&c/damnspam <seconds> &e(Buttons/Levers)")
        msg(sender, "&c/damnspam <seconds after off> <seconds after on> &e(Levers only)")
        return True
        #Gittestlol
        if not is_creative(sender):
            msg(sender, "&cYou can only do this in Creative mode.")
            return True

    # /damnspam <secs>
    if len(args) == 1:
        timeout_on = args[0]
        try:
            timeout_on  = round(float(timeout_on), 2)
            timeout_off = timeout_on
            if 60 >= timeout_on <= -2 or timeout_on == 0:
                timeout_on = False
            if timeout_on == False:
                msg(sender, "&cThe timeout must be within 0-60 or -1.")
                return True
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
            if 60 >= timeout_on <= -2 or timeout_on == 0:
                timeout_on = False
            if 60 >= timeout_off <= -2 or timeout_off == 0:
                timeout_off = False
            if timeout_on == False or timeout_off == False:
                msg(sender, "&cThe timeout must be within 0-60 or -1.")
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

    if location_str(target) in inputs:
        changing_input = True # this input already has a timeout
    # test if player is allowed to build here
    test_event = BlockBreakEvent(target, sender)
    server.getPluginManager().callEvent(test_event)
    changing_input = False
    if test_event.isCancelled():
        msg(sender, "&cYou are not allowed to modify this %s" % str(target.getType()).lower())
        return True

    # add block to inputs
    add_input(sender, target, timeout_off, timeout_on)
    save_inputs()
    msg(sender, "&aSuccessfully set a timeout for this %s." % ttype.lower().replace("_", " "))
    return True


@hook.event("block.BlockBreakEvent", "normal")
def on_block_break(event):
    global removing_input

    if removing_input:
        return True
    sender = event.getPlayer()
    block  = event.getBlock()
    btype  = str(block.getType()).lower()
    if str(block.getType()) in accepted_inputs and not event.isCancelled():
        pos_str = location_str(block)
        if inputs.get(pos_str):
            if sender.isSneaking():
                # test if player is allowed to build here
                removing_input = True
                test_event     = BlockBreakEvent(block, sender)
                server.getPluginManager().callEvent(test_event)
                removing_input = False
                if test_event.isCancelled():
                    event.setCancelled(True)
                    msg(sender, "&cYou are not allowed to remove this %s" % btype)
                    return True
                inputs.pop(pos_str) # remove
                save_inputs()
                msg(sender, "&eSuccessfully removed this %s!" % btype)
                return True
            elif not changing_input:
                event.setCancelled(True)
                msg(sender, "&cYou cannot destroy this %s!" % btype)
                msg(sender, "&c&nSneak&c and break if you want to remove it.")
                return True


@hook.event("player.PlayerInteractEvent", "normal")
def on_interact(event):
    if (str(event.getAction()) == "RIGHT_CLICK_BLOCK") and not event.isCancelled():
        sender  = event.getPlayer()
        block   = event.getClickedBlock()
        btype   = str(block.getType()).lower()
        powered = (block.getData() & 0x8) == 0x8 if btype == "lever" else False # data > 7, but this is how bukkit does it
        pos_str = location_str(block)
        data    = inputs.get(pos_str)
        if data:
            checktime = data["timeout_on"] if powered else data["timeout_off"]
            if checktime == -1:
                event.setCancelled(True)
                plugin_header(sender, "DamnSpam")
                msg(sender, "&cThis %s is locked permanently." % (btype))
            elif data["last_time"] + checktime > now():
                event.setCancelled(True)
                plugin_header(sender, "DamnSpam")
                msg(sender, "&cThis %s has a timeout of %ss." % (btype, checktime))
            else:
                inputs[pos_str]["last_time"] = round(now(), 2)
