from helpers import *

no_cyclers = open_json_file("cycle", [])


@hook.command("cycle")
def on_cycler_command(sender, command, label, args):
    plugin_header(sender, "Cycle")
    if not is_player(sender):
        msg(sender, "&conly players can do this")
        return True
    if not len(args) == 1:
        msg(sender, "&cUsage: /cycle <on|off>")
        return True

    cmd = args[0].lower()
    pid = uid(sender)
    nop = pid in no_cyclers
    if cmd == "on":
        if nop:
            no_cyclers.remove(pid)
            save_cyclers()
            msg(sender, "&aTurned &2on&a inventory cycling!")
        else:
            msg(sender, "&aAlready turned on.")
    elif cmd == "off":
        if not nop:
            no_cyclers.append(pid)
            save_cyclers()
            msg(sender, "&aTurned &coff&a inventory cycling!")
        else:
            msg(sender, "&aAlready turned off.")
    else:
        msg(sender, "&cUsage: /cycle <on|off>")
    return True


@hook.event("player.PlayerItemHeldEvent", "normal")
def on_slot_change(event):
    player    = event.getPlayer()
    if is_creative(player) and uid(player) not in no_cyclers and not player.isSneaking():
        prev_slot = event.getPreviousSlot()
        new_slot  = event.getNewSlot()
        if (prev_slot == 0 and new_slot == 8): # left -> right
            do_cycle(player, True)
        elif (prev_slot == 8 and new_slot == 0): # right -> left
            do_cycle(player, False)

# ITEM SLOTS #
#_____________________________
# | 9|11|12|13|14|15|16|17|18|
# |19|20|21|22|23|24|25|26|27|
# |28|29|30|31|32|33|34|35|36|
#_____________________________
# | 0| 1| 2| 3| 4| 5| 6| 7| 8|

def do_cycle(player, down):
    inv   = player.getInventory()
    items = inv.getStorageContents()
    shift = -9 if down else 9
    shift = shift % len(items)
    for _ in range(4):
        items      = items[shift:] + items[:shift] # shift "around"
        uniq_items = sorted(set(list(items)[:9]))  # get unique inventory
        if uniq_items != [None]: # row not empty
            break
    inv.setStorageContents(items)

def save_cyclers():
    save_json_file("cycle", no_cyclers)