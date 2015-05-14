from helpers import *
from basecommands import simplecommand
import org.bukkit.event.block.BlockBreakEvent as BlockBreakEvent
import org.bukkit.block.Furnace as Furnace
import org.bukkit.inventory.ItemStack as ItemStack
import org.bukkit.Material as Material

settingInformation = {
    "cauldron": [0,
        "easy cauldron water level control",
        "Toggles whether cauldrons auto-fill upon placement and whether right clicking them with redstone dust or empty hand will cycle their water level"
    ],
    "slab":     [0,
        "automatically flipping placed slabs upside-down",
        "Toggles whether slabs/steps which you place should be automatically flipped upside-down"
    ],
    "furnace":  [1,
        "automatically filling furnaces upon placement",
        "Sets your preferred default furnace contents to your currently held itemstack. Use an empty hand to disable this feature. The command is &o/toggle furnace"
    ]
}

defaultPlayerSettings = {
    "cauldron": [], 
    "slab": [], 
    "furnace": {}
}

playerSettings = open_json_file("blockplacemods", defaultPlayerSettings)


#for setting, default in enumerate(defaultPlayerSettings):
#    if playerSettings.get(setting) == None:
#        playerSettings[setting] = default

def get(setting):
    return playerSettings[setting]


def saveSettings():
    save_json_file("blockplacemods", playerSettings)



@simplecommand("toggle",
        aliases = ["set"], 
        usage = "<setting> [value|info]", 
        description = "Toggles or sets your preferences for our redstone \nutilities. The following settings are available:\n" + ", ".join([x for x in settingInformation]),
        senderLimit = 0,
        helpNoargs = True,
        helpSubcmd = True,
        amax = 2)
def toggle_command(sender, command, label, args):
    setting = args[0].lower()
    info = settingInformation.get(setting)
    if info == None:
        return " &cThat setting could not be found.\n For command help, use &o/toggle &cor &o/set"

    values = get(setting)
    player = server.getPlayer(sender.getName())
    uuid   = uid(player)
    arglen = len(args)

    if info[0] == 0: # Toggle
        enabled = uuid not in values
        new     = None
        if arglen == 1:
            new = not enabled
        else:
            arg2 = args[1].lower()
            if arg2 == "info":
                return " &aSetting %s:\n &9%s\n &6Accepted arguments: None or one of the following:\n &oon, enable, off, disable, toggle, switch" % (setting, info[2])
            elif arg2 in ("toggle", "switch"):
                new = not enabled
            elif arg2 in ("on", "enable"):
                new = True
            elif arg2 in ("off", "disable"):
                new = False
            else:
                return " &cArgument '%s' was not recognized. \nTry one of the following: &oon, off, toggle" % arg2
        if enabled == new:
            return " &cAlready %s: &a%s" % ("enabled" if enabled else "disabled", info[1])
        if new:
            values.remove(uuid)
        else:
            values.append(uuid)
        saveSettings()
        return (" &aEnabled " if new else " &aDisabled ") + info[1]

    elif info[0] == 1: # Save ItemStack in hand
        if arglen == 1:
            item = fromStack(player.getItemInHand())
            if 0 in (item[0], item[1]):
                if uuid in values:
                    del values[uuid]
                return " &aDisabled " + info[1]
            values[uuid] = item
            saveSettings()
            return " &aEnabled %s, with currently held itemstack" % info[1]
        arg2 = args[1].lower()
        if arg2 == "info":
            return " &aSetting %s:\n &9%s" % (setting, info[2])
        return " &cArgument '%s' was not recognized. \nUse /toggle %s info for more information." % (arg2, setting)

    return None #This shouldn't happen


def fromStack(itemStack):
    return [itemStack.getTypeId(), itemStack.getAmount(), itemStack.getData().getData()]
def toStack(lst):
    return ItemStack(lst[0], lst[1], lst[2])

def isEnabled(toggleSetting, uuid):
    return uuid not in get(toggleSetting)



@hook.event("block.BlockPlaceEvent", "monitor")
def on_block_place(event):
    if event.isCancelled():
        return
    player = event.getPlayer()
    if not is_creative(player):
        return

    uuid     = uid(player)
    block    = event.getBlockPlaced()
    material = str(block.getType())

    if isEnabled("slab", uuid) and material in ("WOOD_STEP", "STEP") and block.getData() < 8:
        block.setData(block.getData() + 8) # Flip upside down

    elif isEnabled("cauldron", uuid) and material == "CAULDRON":
        block.setData(3) #3 layers of water, 3 signal strength

    elif material == "FURNACE":
        stack = get("furnace").get(uuid)
        if stack == None:
            return
        state = block.getState()
        state.getInventory().setSmelting(toStack(stack))
        state.update()


@hook.event("player.PlayerInteractEvent", "monitor")
def on_interact(event):
    player = event.getPlayer()
    if (isEnabled("cauldron", uid(player)) 
            and is_creative(player)
            and str(event.getAction()) == "RIGHT_CLICK_BLOCK"
            and (not event.hasItem() or str(event.getItem().getType()) == "REDSTONE")
            and str(event.getClickedBlock().getType()) == "CAULDRON"
        ):
        block = event.getClickedBlock()
        event2 = BlockBreakEvent(block, player)
        server.getPluginManager().callEvent(event2)
        if not event2.isCancelled():
            block.setData(block.getData() - 1 if block.getData() > 0 else 3)
