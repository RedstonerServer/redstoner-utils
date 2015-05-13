from helpers import *
from basecommands import simplecommand
import org.bukkit.event.block.BlockBreakEvent as BlockBreakEvent
import org.bukkit.block.Furnace as Furnace
import org.bukkit.inventory.ItemStack as ItemStack
import org.bukkit.Material as Material

denyslabcorrection = open_json_file("denyslabcorrection", []) #Players that don't want slabs corrected
denyautofill       = open_json_file("denyautocauldronfill", [])
denyautolevel      = open_json_file("denyautocauldronlevel", [])

def saveslabs():
    save_json_file("denyslabcorrection", denyslabcorrection)
def savecauldrons():
    save_json_file("denyautocauldronfill", denyautofill)
def savelevels():
    save_json_file("denyautocauldronlevel", denyautolevel)

@simplecommand("autofillcauldron",
        aliases     = ["fillcauldronautomatically"],
        usage       = "on/off",
        helpNoargs  = True,
        description = "Sets whether you want placed cauldrons to fill \nautomatically",
        amax        = 1,
        senderLimit = 0)
def autofillcauldron_command(sender, command, label, args):
    uuid = uid(server.getPlayer(sender.getName()))
    if args[0].lower() == "off":
        if uuid in denyautofill:
            return "&cAuto fillment of cauldrons is already disabled"
        denyautofill.append(uuid)
        savecauldrons()
        return "&aFilling cauldrons will no longer happen automatically"
    if args[0].lower() == "on":
        if uuid not in denyautofill:
            return "&cAuto fillment of cauldrons is already enabled"
        denyautofill.remove(uuid)
        savecauldrons()
        return "&aFilling cauldrons will happen automatically from now"
    return "HELP"


@simplecommand("autoflipslab",
        aliases     = ["autoflipstep", "flipslabautomatically", "flipstepautomatically"],
        usage       = "on/off",
        helpNoargs  = True,
        description = "Sets whether you want placed slabs to be turned \nupside-down",
        amax        = 1,
        senderLimit = 0)
def autoflipslab_command(sender, command, label, args):
    uuid = uid(server.getPlayer(sender.getName()))
    if args[0].lower() == "off":
        if uuid in denyslabcorrection:
            return "&cAuto flipping of slabs is already disabled"
        denyslabcorrection.append(uuid)
        saveslabs()
        return "&aFlipping slabs will no longer happen automatically"
    if args[0].lower() == "on":
        if uuid not in denyslabcorrection:
            return "&cAuto flipping of slabs is already enabled"
        denyslabcorrection.remove(uuid)
        saveslabs()
        return "&aFlipping slabs will happen automatically from now"
    return "HELP"


@simplecommand("autotakewater",
        aliases     = ["autocauldronlevel"],
        usage       = "on/off",
        helpNoargs  = True,
        description = "Sets whether you want right clicking cauldrons \nwith empty hand or redstone dust \nto lower water level",
        amax        = 1,
        senderLimit = 0)
def autoflipslab_command(sender, command, label, args):
    uuid = uid(server.getPlayer(sender.getName()))
    if args[0].lower() == "off":
        if uuid in denyautolevel:
            return "&cTaking water with hand/redstone is already disabled"
        denyautolevel.append(uuid)
        savelevels()
        return "&aYou can no longer take water with hand/redstone"
    if args[0].lower() == "on":
        if uuid not in denyautolevel:
            return "&cTaking water with hand/redstone is already enabled"
        denyautolevel.remove(uuid)
        savelevels()
        return "&aYou can take water with hand/redstone from now"
    return "HELP"


@hook.event("block.BlockPlaceEvent", "monitor")
def on_block_place(event):
    if event.isCancelled():
        return
    player = event.getPlayer()
    if player.getWorld().getName() not in ("Creative", "Trusted", "world"):
        return
    uuid = uid(player)
    block = event.getBlockPlaced()
    material = str(block.getType())
    if uuid not in denyslabcorrection and material in ("WOOD_STEP", "STEP") and block.getData() < 8:
        block.setData(block.getData() + 8) # Flip upside down
    elif uuid not in denyautofill and material == "CAULDRON":
        block.setData(3) #3 layers of water, 3 signal strength
    elif material == "FURNACE":
        state = block.getState()
        state.getInventory().setSmelting(ItemStack(Material.REDSTONE))
        state.update()

@hook.event("player.PlayerInteractEvent", "monitor")
def on_interact(event):
    player = event.getPlayer()
    if uid(player) in denyautolevel or player.getWorld().getName() not in ("Creative", "Trusted", "world"):
        return
    if str(event.getAction()) != "RIGHT_CLICK_BLOCK":
        return
    if event.hasItem() and not str(event.getItem().getType()) == "REDSTONE":
        return
    block = event.getClickedBlock()
    if str(block.getType()) != "CAULDRON":
        return
    event2 = BlockBreakEvent(block, player)
    server.getPluginManager().callEvent(event2)
    if not event2.isCancelled():
        data = block.getData()
        block.setData(data - 1 if data > 0 else 3)
