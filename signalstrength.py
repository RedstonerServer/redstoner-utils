from helpers import *
import org.bukkit.inventory.ItemStack as ItemStack
import org.bukkit.Material as Material
from math import ceil
from basecommands import simplecommand, Validate, CommandException

""" Suggestion by Armadillo28, see thread: http://redstoner.com/forums/threads/2213?page=1#reply-14507 """

disallowed_item_types = (
    Material.getMaterial(0),
    Material.getMaterial(175),
    Material.getMaterial(383),
)

default_args = open_json_file("signalstrengthdefaults", {})

def save_defaults():
    save_json_file("signalstrengthdefaults", default_args)


def item_name(item_type, remove_underscores = True):
    typ = str(item_type).lower()
    return typ.replace("_", "") if remove_underscores else typ


def item_type_allowed(item_type):
    return not item_type in disallowed_item_types


def required_item_count(strength, stack_size, slot_count):
    if strength == 0:
        item_count = 0
    elif strength == 1:
        item_count = 1
    else:
        item_count = int(ceil(slot_count * stack_size / 14.0 * (strength - 1)))

    resulting_strength = 0 if item_count == 0 else int(1 + 14.0 * item_count / stack_size / slot_count)
    #Clarification on these formulas at http://minecraft.gamepedia.com/Redstone_Comparator#Containers

    return item_count if resulting_strength == strength else None


def get_data(player, args):
    uuid = uid(player)
    if uuid in default_args:
        strength, item_type, item_data = default_args[uuid]
        item_type = Material.getMaterial(item_type)
    else:
        strength  = 1
        item_type = Material.REDSTONE
        item_data = 0

    if len(args) > 0:
        Validate.isTrue(args[0].isdigit() and 0 <= int(args[0]) <= 15, "&cThe signal strength has to be a value from 0 to 15")
        strength = int(args[0])

    if len(args) > 1:
        if args[1].isdigit():
            item_type = Material.getMaterial(int(args[1]))
        else:
            item_type = Material.matchMaterial(args[1])
        Validate.notNone(item_type, "&cThat item type could not be found")
        Validate.isTrue(item_type not in disallowed_item_types, "&cThat item type may not be used")

    if len(args) > 2:
        Validate.isTrue(args[2].isdigit() and 0 <= int(args[2]) <= 15, "&cThe data has to be a value from 0 to 15")
        item_data = int(args[2])

    return (strength, item_type, item_data)


def get_inventory(block):
    try:
        return block.getState().getInventory()
    except AttributeError:
        return None


def get_entire_container(container):
    container_blocks = [container]
    container_type = container.getType()
    if container_type in (Material.CHEST, Material.TRAPPED_CHEST):
        loc = container.getLocation()
        x = loc.getBlockX()
        y = loc.getBlockY()
        z = loc.getBlockZ()
        world = loc.getWorld()

        container_blocks += [
            block for block in (
                world.getBlockAt(x + 1, y, z), 
                world.getBlockAt(x - 1, y, z), 
                world.getBlockAt(x, y, z + 1), 
                world.getBlockAt(x, y, z - 1),
            ) if block.getType() == container_type
        ]

    return container_blocks



@simplecommand("signalstrength",
        usage = "(default) [signalstrength] [item] [data]",
        aliases = ["ss", "level"],
        description = "Fills the targeted container with the correct amount of items to achieve the desired signal strength.",
        amin = 0,
        amax = 4,
        helpSubcmd = True,
        senderLimit = 0)
def on_signalstrength_command(sender, command, label, args):
    if len(args) > 0 and args[0].lower() in ("default", "defaults", "setdefaults"):
        strength, item_type, item_data = get_data(sender, args[1:])

        uuid = uid(sender)
        if strength == 1 and item_type == Material.REDSTONE and item_data == 0:
            if uuid in default_args:
                del default_args[uuid]
                save_defaults()
        else:
            default_args[uuid] = (strength, str(item_type), item_data)
            save_defaults()

        return "&aSet your signal strength defaults to (%s, %s, %s)" % (strength, item_name(item_type, False), item_data)

    Validate.isTrue(len(args) <= 3, "&cExpected at most 3 arguments")

    target_block = sender.getTargetBlock(None, 5)
    Validate.notNone(target_block, "&cThat command can only be used when a container is targeted")

    inventory = get_inventory(target_block)
    Validate.notNone(inventory, "&cThat command can only be used if a container is targeted")

    strength, item_type, item_data = get_data(sender, args)

    #--------Get the stack size and required amount of items to achieve the desired signal strength---------
    stack_size = item_type.getMaxStackSize()
    slot_count = inventory.getSize()

    item_count = required_item_count(strength, stack_size, slot_count)
    Validate.notNone(item_count, "&cThe desired signal strength could not be achieved with the requested item type")

    #--------Add the other side of the chest if target is a double chest and check if player can build---------
    container_blocks = get_entire_container(target_block)
    for block in container_blocks:
        Validate.isTrue(can_build(sender, block), "&cYou do not have permission to do that here")

    #----------------Insert items-------------
    full_stack_count, remaining = divmod(item_count, stack_size)
    for block in container_blocks:
        inv = block.getState().getInventory()
        inv.clear()
        for i in range(full_stack_count):
            inv.setItem(i, ItemStack(item_type, stack_size, item_data))
        if remaining > 0:
            inv.setItem(full_stack_count, ItemStack(item_type, remaining, item_data))

    return "&aComparators attached to that %s will now put out a signal strength of %s" % (item_name(target_block.getType()), strength)
