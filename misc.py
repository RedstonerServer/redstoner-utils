#pylint: disable = F0401
from helpers import *
from time import time as now
from time import sleep
from sys import exc_info
import thread
import org.bukkit.inventory.ItemStack as ItemStack
import org.bukkit.Bukkit as Bukkit
from basecommands import simplecommand



@hook.event("player.PlayerJoinEvent", "monitor")
def on_join(event):
    """
    Welcome new players
    """
    player = event.getPlayer()

    # send welcome broadcast
    if not player.hasPlayedBefore():
        broadcast("utils.greet_new", "\n&a&lPlease welcome &f" + player.getDisplayName() + " &a&lto Redstoner!\n")

        # clear out some eventual crap before
        msg(player, " \n \n \n \n \n \n \n \n \n \n \n \n ")
        msg(player, "  &4Welcome to the Redstoner Server!")
        msg(player, "  &6Before you ask us things, take a quick")
        msg(player, "  &6look at &a&nredstoner.com/info")
        msg(player, "  \n&6thank you and happy playing ;)")
        msg(player, " \n \n")

    # teleport to spawn when spawning inside portal
    loginloc = player.getLocation().getBlock().getType()
    headloc = player.getEyeLocation().getBlock().getType()
    if "PORTAL" in [str(headloc), str(loginloc)]:
        msg(player, "&4Looks like you spawned in a portal... Let me help you out")
        msg(player, "&6You can use /back if you &nreally&6 want to go back")
        player.teleport(player.getWorld().getSpawnLocation())

"""
This code fixes /up 0 destroying/replacing blocks in plots that are not yours.
If you use //up, this is caught by plotme and cancelled if you are not allowed to build.
However, if you use //up, WorldEdit does the following on "low" priority:
* Change the command to /up with the same arguments
* Run another event with /up but its cancelled (dunno why it does this)

Keep in mind that, on "lowest" priority, PlotMe might cancel events.


"""
dup = 0 #Used to store when someone used //up

@hook.event("player.PlayerCommandPreprocessEvent", "lowest")
def cmd_event(event):
    global dup
    if event.getMessage().split(" ")[0] in ("//up", "/worldedit:/up"):
        dup = True

@hook.event("player.PlayerCommandPreprocessEvent", "normal")
def cmd_event2(event):
    global dup
    args = event.getMessage().split(" ")
    if args[0].lower() in ("/up", "/worldedit:up"):
        if dup: #If plotme cancelled this, it will not matter. This lets it through but PlotMe doesn't.
            dup = False
        elif not event.isCancelled():
            event.setCancelled(True)
            event.getPlayer().chat("//up " + " ".join(args[1:]))





""" Disabled while builder can't access Trusted
@hook.event("player.PlayerGameModeChangeEvent", "low")
def on_gamemode(event):
    user = event.getPlayer()
    if str(event.getNewGameMode()) != "SPECTATOR" and user.getWorld().getName() == "Trusted" and not user.hasPermission("mv.bypass.gamemode.Trusted"):
        event.setCancelled(True)
"""


@hook.event("player.PlayerBedEnterEvent")
def on_bed_enter(event):
    world = event.getPlayer().getWorld()
    if world.getName() in ("Survival_1", "TrustedSurvival_1"):
        for player in world.getPlayers():
            player.setSleepingIgnored(True)


@hook.event("player.PlayerTeleportEvent")
def on_player_teleport(event):
    """
    Disable spectator teleportation
    """
    player = event.getPlayer()
    if not event.isCancelled() and str(event.getCause()) == "SPECTATE" and not player.hasPermission("utils.tp.spectate"):
        event.setCancelled(True)
        msg(event.getPlayer(), "&cSpectator teleportation is disabled")


@hook.event("block.BlockFromToEvent", "highest")
def on_flow(event):
    if event.isCancelled():
        return
    block = event.getToBlock()
    if block.getWorld().getName() == "Creative" and rs_material_broken_by_flow(str(block.getType())):
        event.setCancelled(True)

def rs_material_broken_by_flow(material):
    if material in ("REDSTONE", "LEVER", "TRIPWIRE"):
        return True
    parts = material.split("_")
    length = len(parts)
    return length > 1 and (parts[0] == "DIODE" or parts[1] in ("TORCH", "WIRE", "BUTTON", "HOOK") or (length == 3 and parts[1] == "COMPARATOR"))

sudo_blacklist = ["pyeval", "script_backup_begin", "script_backup_end", "script_backup_error", "script_backup_database_begin", "script_backup_database_dumps", "script_backup_database_end",
"script_backup_database_error", "script_backup_database_abort", "script_trim", "script_trim_result", "script_spigot_update", "script_disk_filled", "script_restart", "script_restart_abort",
"script_stop", "script_stop_abort", "script_shutdown", "stop", "esudo", "essentials:sudo"]

@simplecommand("sudo",
        usage        = "<player> [cmd..]",
        description  = "Makes <player> write [cmd..] in chat",
        amin         = 2,
        helpNoargs   = True)
def on_sudo_command(sender, command, label, args):
    target = args[0]
    cmd    =  " ".join(args[1:])
    msg(sender, "&2[SUDO] &rRunning '&e%s&r' as &3%s" % (cmd, target))
    is_cmd     = cmd[0] == "/"
    is_console = target.lower() in ["server", "console"]
    first_cmd = (args[1])[1:] if is_cmd else None
    if first_cmd in sudo_blacklist and (is_player(sender) and uid(sender) not in pythoners):
        return "&cYou can't sudo this command"
    if is_console:
        server.dispatchCommand(server.getConsoleSender(), cmd[1:] if is_cmd else cmd)
        return None
    target_player = server.getPlayer(target)
    if target_player:
        target_player.chat(cmd)
        return None
    return "&cPlayer %s not found!" % target


container_levels = dict(
    FURNACE = [],
    HOPPER = [],
    CHEST = [],
)


"""
Suggestion by Armadillo28, see thread: http://redstoner.com/forums/threads/2213-putting-the-correct-amount-of-items-in-a-container?page=1#reply-14507
"""
"""
@simplecommand("signalstrength",
        usage = "<signal strength> [item] [data]",
        aliases = ["ss", "level"],
        description = "Fills the targeted container with the correct amount of items to achieve the desired signal strength.",
        amin = 1,
        amax = 3,
        helpNoargs = True,
        helpSubcmd = True,
        senderLimit = 0)
def on_signalstrength_command(sender, command, label, args):
    values = []
    try:
        for i in range(len(args)):
            values[i] = int(args[i])
    except ValueError:
        return "&cYou have to enter a number for the signal strength"


    target_block = sender.getTargetBlock(None, 5)
    Validate.notNone(target_block)
    target_type = str(target_block.getType())
    Validate.isTrue(target_type in container_levels)

    levels = container_levels[target_type]

    item_value = 1
    item_type = Material.REDSTONE
    item_data = 0
    if len(values) > 1:
        item_type = Material.getMaterial(values[1])
        if item_type == None:
            return "&cThat is not an item ID"
        if len(values) == 3:
            item_data = values[2]
            if not (0 <= item_data <= 15):
                return "&cThe data must be a number from 0 to a maximum of 15"
        if values[1] in (items that stack up to 16):
            item_value = 4
        elif values[1] in (items that stack up to 1):
            item_value = 64

    target_strength = values[0]

    item_count = levels[target_strength] / item_value

    if int(item_count) * item_value < levels[target_strength] and (int(item_count) + 1) * item_value >= levels[target_strength + 1]: #if target_strength = 15, first check will always be false, so no IndexError
        return "&cThe desired signal strength could not be achieved with the requested item type"

    item_count = int(item_count)
    if item_count % 1 != 0:
        item_count += 1

    def stack(count):
        return ItemStack(values[1])

    full_stacks = int(item_count / item_value)
    for i in range(0, full_stacks) #amount of full stacks
        target_block.setItem(i, ItemStack())
"""







@simplecommand("me",
        usage        = "[message..]",
        description  = "Sends a message in third person",
        helpNoargs   = True)
def on_me_command(sender, command, label, args):
    text = colorify("&7- %s &7%s " % (sender.getDisplayName() if isinstance(sender, Player) else "&9CONSOLE", u"\u21E6"))
    broadcast("utils.me", text + " ".join(args), usecolor = sender.hasPermission("essentials.chat.color"))
    return None



@hook.command("pluginversions")
def on_pluginversions_command(sender, command, label, args):
    """
    /pluginversions
    print all plugins + versions; useful when updating plugins
    """
    try:
        plugin_header(sender, "Plugin versions")
        plugins = [pl.getDescription() for pl in list(ArrayList(java_array_to_list(server.getPluginManager().getPlugins())))]
        info(type(plugins[0]).__name__)
        plugins.sort(key = lambda pl: pl.getDescription().getName())
        msg(sender, "&3Listing all " + str(len(plugins)) + " plugins and their version:")
        for plugin in plugins:
            msg(sender, "&6" + pl.getDescription().getName() + "&r: &e" + pl.getDescription().getVersion())
        return True
    except:
        error(trace())


@hook.command("echo")
def on_echo_command(sender, command, label, args):
    """
    /echo
    essentials echo sucks and prints mail alerts sometimes
    """
    msg(sender, " ".join(args).replace("\\n", "\n"))



def eval_thread(sender, code):
    """
    /pyeval
    run python ingame
    """
    try:
        result = eval(code)
        msg(sender, ">>> %s: %s" % (colorify("&3") + type(result).__name__, colorify("&a") + unicode(result) + "\n "), usecolor = False)
    except:
        e = exc_info()[1]
        try:
            eclass = e.__class__
        except AttributeError:
            eclass = type(e)
        msg(sender, ">>> %s: %s" % (eclass.__name__, e) + "\n ", False, "c")
    thread.exit()

pythoners = [
"e452e012-2c82-456d-853b-3ac8e6b581f5", # Nemes
"ae795aa8-6327-408e-92ab-25c8a59f3ba1", # jomo
"305ccbd7-0589-403e-a45b-d791dcfdee7d"  # PanFritz
]

@simplecommand("pyeval",
        usage       = "[code..]",
        description = "Runs python [code..] and returns the result",
        helpNoargs  = True)
def on_pyeval_command(sender, command, label, args):
    if is_player(sender) and uid(sender) not in pythoners:
        return noperm(sender)
    msg(sender, " ".join(args), False, "e")
    thread.start_new_thread(eval_thread, (sender, " ".join(args)))
    return None



@simplecommand("tempadd",
        usage       = "<user> <group> [duration]",
        description = "Temporarily adds <user> to <group> for \n[duration] minutes. Defaults to 1 week.",
        helpNoargs  = True,
        helpSubcmd  = True,
        amin        = 2,
        amax        = 3)
def tempadd_command(sender, command, label, args):
    if not sender.hasPermission("permissions.manage.membership." + args[1]):
        return "&cYou do not have permission to manage that group!"
    if len(args) == 3:
        if not args[2].isdigit():
            return "&cThats not a number!"
        duration = int(args[2]) * 60
    else:
        duration = 604800
    if duration <= 0:
        return "&cThats too short!"
    cmd = "pex user %s group add %s * %s" % (args[0], args[1], duration)
    runas(sender, cmd)

    m, s = divmod(duration, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    return "&aAdded to group for %dd%dh%dm" % (d, h, m)



@hook.command("modules")
def on_modules_command(sender, command, label, args):
    """
    /modules
    list all modules, unloaded modules in red
    """
    plugin_header(sender, "Modules")
    msg(sender, ", ".join([(("&a" if mod in shared["modules"] else "&c") + mod) for mod in shared["load_modules"]]))


@simplecommand("warn",
        usage       = "",
        description = "Warns everybody on the server that you will cause lag shortly",
        amax        = 0,
        helpSubcmd  = True)
def warn_command(sender, command, label, args):
    broadcast(None, " &b= &2&lLag incoming! &r-%s" % sender.getDisplayName())


@simplecommand("warnp",
        usage       = "",
        description = "Warns everybody on the server that you might cause lag shortly",
        amax        = 0,
        helpSubcmd  = True)
def warnp_command(sender, command, label, args):
    broadcast(None, " &b= &2&lPossible lag incoming! &r-%s" % sender.getDisplayName())



""" Something I'm planning for schematics
@hook.event("player.PlayerCommandPreprocessEvent", "low")
def on_command(event):
    msg = " ".split(event.getMessage())
    if len(msg) < 3:
        return
    if msg[0].lower() not in ("/schematic", "/schem"):
        return
    if msg[1].lower() not in ("save", "load"):
        return
    msg[2] = event.getPlayer().getName() + "/" + msg[2]
"""



