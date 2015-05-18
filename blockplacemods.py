from helpers import *
from basecommands import simplecommand, Validate, CommandException
from time import sleep
from collections import deque
import thread
import org.bukkit.event.block.BlockBreakEvent as BlockBreakEvent
import org.bukkit.block.Furnace as Furnace
import org.bukkit.inventory.ItemStack as ItemStack
import org.bukkit.Material as Material
import org.bukkit.event.block.Action as Action
import org.bukkit.block.BlockFace as BlockFace
import org.bukkit.scheduler.BukkitRunnable as Runnable

settingInformation = dict( #[setting type, identifying description, detailed description, aliases, (optional) max slot id], setting types: 0 = toggle, default on. 1 = Set your setting to held itemstack, 2 = toggle, default off
    cauldron = [0,
        "easy cauldron water level control",
        "Toggles whether cauldrons auto-fill upon placement and whether right clicking them with redstone dust or empty hand will cycle their water level",
        ["caul", "water"]
    ],
    slab = [0,
        "automatically flipping placed slabs upside-down",
        "Toggles whether slabs/steps which you place should be automatically flipped upside-down",
        ["step"]
    ],
    furnace = [1,
        "automatically filling furnaces upon placement",
        "Sets your preferred default furnace contents to your currently held itemstack. Use an empty hand to empty a slot, or /toggle dropper clear to clear all slots.",
        ["cooker", "fillf"], 2
    ],
    #torch = [0,
    #    "removal of torches you place on redstone blocks",
    #    "Toggles whether redstone torches which you place on redstone blocks will be deleted after a short amount of delay.",
    #    ["redstonetorch", "tor"]
    #],
    piston = [2,
        "rotating pistons, droppers and hoppers to face the block you place them against",
        "Toggles whether pistons or sticky pistons which you place will be rotated to face the block which you placed them against.",
        ["invert", "rp"]
    ],
    dropper = [1,
        "automatically filling droppers upon placement",
        "Sets your preferred default dropper contents to your currently held itemstack. Use an empty hand to empty a slot, or /toggle dropper clear to clear all slots.",
        ["itemshooter", "filld"], 8
    ],
    hopper = [1,
        "automatically filling hoppers upon placement",
        "Sets your preferred default hopper contents to your currently held itemstack. Use an empty hand to empty a slot, or /toggle dropper clear to clear all slots.",
        ["itemtransporter", "fillh"], 4
    ]
)

defaults = {
    0: [], 
    1: {},
    2: []
}

faces = {
    BlockFace.DOWN  : 0,
    BlockFace.UP    : 1,
    BlockFace.NORTH : 2,
    BlockFace.SOUTH : 3,
    BlockFace.WEST  : 4,
    BlockFace.EAST  : 5
}

playerSettings = open_json_file("blockplacemods", {})

for setting, details in settingInformation.iteritems():
    if playerSettings.get(setting) == None:
        playerSettings[setting] = defaults[details[0]]

def get(setting):
    return playerSettings[setting]

def saveSettings():
    save_json_file("blockplacemods", playerSettings)

def getSettingDetails(arg):
    try:
        arg = arg.lower()
        for setting, details in settingInformation.iteritems():
            if setting == arg or arg in details[3]:
                return (setting, details)
    except:
        error(trace())
    raise CommandException(" &cThat setting could not be found.\n For command help, use &o/toggle &cor &o/set")

@simplecommand("toggle",
        aliases = ["setting", "set", "config"], 
        usage = "<setting> [value|info]", 
        description = "Toggles or sets your preferences for our redstone \nutilities. The following settings are available:\n" + ", ".join([x for x in settingInformation]),
        senderLimit = 0,
        helpNoargs = True,
        helpSubcmd = True,
        amax = 2)
def toggle_command(sender, command, label, args):
    try:
        setting, details = getSettingDetails(args[0])
        Validate.isAuthorized(sender, "utils.toggle." + setting, "that setting")

        values = get(setting)
        player = server.getPlayer(sender.getName())
        uuid   = uid(player)
        arglen = len(args)

        if details[0] in (0,2): # Toggle
            default = details[0] == 0 # If True: toggle on if list doesn't contain the uuid

            enabled = (uuid not in values) == default #Invert if details[0] == 2 (toggle disabled by default)
            info("Enabled: " + str(enabled))
            new     = None
            if arglen == 1:
                new = not enabled
            else:
                arg2 = args[1].lower()
                if arg2 == "info":
                    return " &aSetting %s:\n &9%s\n &6Accepted arguments: [on|enable|off|disable|toggle|switch|info]\n &6Aliases: %s" % (setting, details[2], ", ".join(details[3]))
                elif arg2 in ("toggle", "switch"):
                    new = not enabled
                elif arg2 in ("on", "enable"):
                    new = True == default
                    info("New: " + str(new))
                elif arg2 in ("off", "disable"):
                    new = False == default
                    info("New: " + str(new))
                else:
                    return " &cArgument '%s' was not recognized. \n Use &o/toggle %s info &cfor more information" % (arg2, setting)
            if enabled == new:
                return " &cAlready %s: &a%s" % ("enabled" if enabled else "disabled", details[1])
            if new == default:
                values.remove(uuid)
            else:
                values.append(uuid)
            saveSettings()
            return (" &aEnabled " if new else " &aDisabled ") + details[1]


        elif details[0] == 1: # Save ItemStack in hand
            arg2 = args[1].lower() if arglen > 1 else ""
            enabled = uuid in values

            if arg2 == "clear":
                if enabled:
                    del values[uuid]
                return " &aDisabled " + details[1]

            if arg2 == "details":
                return " &aSetting %s:\n &9%s \n&6Accepted arguments: [<slot>|clear|details]" % (setting, details[2])

            slot = int(arg2) if arg2.isdigit() else 0 
            if not (0 <= slot <= details[4]):
                return " &cSlot number must be between 1 and %s!" % details[4]

            item = fromStack(player.getItemInHand())
            if item[0] == 0 or item[1] <= 0:
                if enabled: 
                    items = values[uuid]
                    if slot in items:
                        del items[slot]
                        saveSettings()
                        if len(items) == 0:
                            del values[uuid]
                            return " &aDisabled " + details[1]
                        return " &aCleared slot %s of setting %s" % (slot, setting)
                    return " &cSlot %s of setting %s was already cleared!" % (slot, setting)
                return " &cAlready disabled: " + details[1]

            if arglen == 2 and not arg2.isdigit():
                return " &cArgument '%s' was not recognized. \nUse &o/toggle %s details &cfor more detailsrmation." % (arg2, setting)

            if not enabled:
                values[uuid] = {}
            values[uuid][slot] = item
            saveSettings()
            return ((" &aEnabled setting %s, S" % setting) if len(values[uuid]) == 1 else "&as") + "et itemstack in slot %s to item in hand" % (slot)

        return None #This shouldn't happen
    except CommandException, e:
        raise e
    except:
        error(trace())

"""
        if info[0] in (0,2): # Toggle
            default = info[0] == 0

            enabled = (uuid not in values) == default #Invert if info[0] == 2 (toggle disabled by default)
            info("Enabled": True)
            new     = None
            if arglen == 1:
                new = not enabled
            else:
                arg2 = args[1].lower()
                if arg2 == "info":
                    return " &aSetting %s:\n &9%s\n &6Accepted arguments: [on|enable|off|disable|toggle|switch]\n &6Aliases: %s" % (setting, info[2], ", ".join(info[3]))
                elif arg2 in ("toggle", "switch"):
                    new = not enabled
                elif arg2 in ("on", "enable"):
                    new = True == default
                elif arg2 in ("off", "disable"):
                    new = False == default
                else:
                    return " &cArgument '%s' was not recognized. \nUse &o/toggle %s info &cfor more information" % (arg2, setting)
            if enabled == new:
                return " &cAlready %s: &a%s" % ("enabled" if enabled else "disabled", info[1])
            if new:
                values.remove(uuid)
            else:
                values.append(uuid)
            saveSettings()
            return (" &aEnabled " if new else " &aDisabled ") + info[1]
"""



def fromStack(itemStack):
    return [itemStack.getTypeId(), itemStack.getAmount(), itemStack.getData().getData()]
def toStack(lst):
    return ItemStack(lst[0], lst[1], lst[2])

def isEnabled(toggleSetting, uuid):
    return (uuid not in get(toggleSetting)) == (settingInformation[toggleSetting][0] == 0) #Invert if off by default



@hook.event("block.BlockPlaceEvent", "monitor")
def on_block_place(event):
    try:
        if event.isCancelled():
            return
        player = event.getPlayer()
        if not is_creative(player):
            return

        uuid     = uid(player)
        block    = event.getBlockPlaced()
        material = block.getType()


        if (material in (Material.WOOD_STEP, Material.STEP) 
            and isEnabled("slab", uuid) 
            and player.hasPermission("utils.toggle.slab") 
            and block.getData() < 8
            ):
            block.setData(block.getData() + 8) # Flip upside down


        elif (material == Material.CAULDRON 
            and isEnabled("cauldron", uuid) 
            and player.hasPermission("utils.toggle.cauldron")
            ):
            block.setData(3) #3 layers of water, 3 signal strength


        elif ((material == Material.FURNACE and player.hasPermission("utils.toggle.furnace"))
            or (material == Material.DROPPER and player.hasPermission("utils.toggle.dropper"))
            or (material == Material.HOPPER and player.hasPermission("utils.toggle.hopper")) 
            ):
            stacks = get(str(material).lower()).get(uuid)
            if stacks != None: # Enabled
                state = block.getState()
                inv = state.getInventory()
                for slot, stack in stacks.iteritems():
                    inv.setItem(int(slot), toStack(stack))
                state.update()

        """
        elif (material == Material.REDSTONE_TORCH_ON
            and event.getBlockAgainst().getType() == Material.REDSTONE_BLOCK
            and isEnabled("torch", uuid) 
            and player.hasPermission("utils.toggle.torch")
            ):
            torches_to_break.append(block)
        """


        if (material in (Material.PISTON_BASE, Material.PISTON_STICKY_BASE) #Not elif because for droppers it can do 2 things
            and isEnabled("piston", uuid)
            and player.hasPermission("utils.toggle.piston")
            ):
            block.setData(faces[block.getFace(event.getBlockAgainst())])
    except:
        error(trace())


@hook.event("player.PlayerInteractEvent", "monitor")
def on_interact(event):
    player = event.getPlayer()
    if (isEnabled("cauldron", uid(player)) 
        and player.hasPermission("utils.toggle.cauldron") 
        and is_creative(player)
        and event.getAction() == Action.RIGHT_CLICK_BLOCK
        and (not event.hasItem() or event.getItem().getType() == Material.REDSTONE)
        and event.getClickedBlock().getType() == Material.CAULDRON
        ):
        block = event.getClickedBlock()
        event2 = BlockBreakEvent(block, player)
        server.getPluginManager().callEvent(event2)
        if not event2.isCancelled():
            block.setData(block.getData() - 1 if block.getData() > 0 else 3)

"""
break_torches = True
torches_to_break = deque()

def stop_breaking_torches():
    break_torches = False
    info("Interrupted torch breaking thread")


class torch_breaker(Runnable):

    def run():
        
        try:
            if break_torches:
                for i in range(len(torches_to_break)):
                    block = torches_to_break.popleft()
                    mat = block.getType()
                    if mat == Material.REDSTONE_TORCH_OFF:
                        block.setTypeId(0)
                    elif mat == Material.REDSTONE_TORCH_ON:
                        torches_to_break.append(block)
        except:
            error(trace())
"""

