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
@hook.event("player.PlayerCommandPreprocessEvent", "low")
def cmd_event(event):
    args = event.getMessage().split(" ")
    if args[0].lower() in ("/up", "/worldedit:up"):
        event.setMessage("//up " + " ".join(args[1:]))
"""

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
    if is_console:
        server.dispatchCommand(server.getConsoleSender(), cmd[1:] if is_cmd else cmd)
        return None
    target_player = server.getPlayer(target)
    if target_player:
        target_player.chat(cmd)
        return None
    return "&cPlayer %s not found!" % target



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

@simplecommand("pyeval",
        usage       = "[code..]",
        description = "Runs python [code..] and returns the result",
        helpNoargs  = True)
def on_pyeval_command(sender, command, label, args):
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



