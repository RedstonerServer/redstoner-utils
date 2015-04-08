#pylint: disable = F0401
from helpers import *
from time import time as now
from sys import exc_info
import thread
import org.bukkit.inventory.ItemStack as ItemStack
import org.bukkit.Bukkit as Bukkit
import org.bukkit.event.player.PlayerChatEvent as PlayerChatEvent
import basecommands
from basecommands import simplecommand

"""
@advancedcommand("hi", aliases = ["hu"], description = "Says hi!", subCommands = [
    subcommand("server", aliases = ["serv"], amin = 1, amax = 4, usage = "[msg..]", senderLimit = 0),
    subcommand("me", aliases = ["meu"], amin = 2, amax = 5, usage = "[MESSAGE]")
    ])
def on_hi_command():

    def server(sender, command, label, args):
        server.dispatchCommand(server.getConsoleSender(), "say " + " ".join(args[1:]))
        return "Success!"
    def me(sender, command, label, args):
        target = server.getPlayer(args[1])
        if target:
            target.chat(" ".join(args[2:]))
            return None
        return "No target found"
"""


@hook.event("player.PlayerJoinEvent", "monitor")
def on_join(event):
    """
    Welcome new players
    """
    player = event.getPlayer()

    # send welcome broadcast
    if not player.hasPlayedBefore():
        broadcast("utils.greet_new", "")
        broadcast("utils.greet_new", "&a&lPlease welcome &f" + player.getDisplayName() + " &a&lto Redstoner!")
        broadcast("utils.greet_new", "")

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
    is_console = target.lower() == "server" or target.lower() == "console"
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
    broadcast("utils.me", "&7- %s &7%s %s" % (sender.getDisplayName() if isinstance(sender, Player) else "&9CONSOLE", u"\u21E6", " ".join(args)))
    return None

"""
@basecommands.command("damnyou", aliases = ["dam"])
def damnyou_command():

	@basecommands.subcommand("me")
	def me(sender, command, label, args):
		info("me ran")

	@basecommands.maincommand
	def main(sender, command, label, args):
		info("main ran")
"""

#@hook.command("gm")
#def on_gm_command(sender, args):
#  """
#  /gm - custom gamemode command with extra perms for greater control
#  """
#  if not is_player(sender):
#    msg(sender, "&cDerp! Can't run that from console!")
#    return True
#  if not checkargs(sender, args, 1, 2):
#    return True
#  mode = args[0]
#  target = args[1]
#  if target and not sender.hasPermission("utils.gm.other"):
#    msg(sender, "&cYou cannot change the gamemode of another player!")
#  else:
#    target = sender
#  if mode < 0 or mode > 3:
#    msg(sender, "&cThat gamemode does not exist!")
#  elif sender.hasPermission("utils.gm." % mode):
#    runas(server.getConsoleSender(), "gamemode " % mode % " " % target)
#  else:
#    msg(sender, "&cYou cannot access that gamemode!")
#  return True


last_shear = 0.0

@hook.event("player.PlayerInteractEntityEvent")
def on_player_entity_interact(event):
    """
    Clicking redstone_sheep with shears will drop redstone + wool
    also makes a moo sound for the shearer
    """
    global last_shear
    if not event.isCancelled():
        shear_time = now()
        if last_shear + 0.4 < shear_time:
            last_shear = shear_time
            sender = event.getPlayer()
            entity = event.getRightClicked()
            if is_player(entity) and uid(entity) == "ae795aa8-6327-408e-92ab-25c8a59f3ba1" and str(sender.getItemInHand().getType()) == "SHEARS" and is_creative(sender):
                for _ in range(5):
                    entity.getWorld().dropItemNaturally(entity.getLocation(), ItemStack(bukkit.Material.getMaterial("REDSTONE")))
                    entity.getWorld().dropItemNaturally(entity.getLocation(), ItemStack(bukkit.Material.getMaterial("WOOL")))
                sender.playSound(entity.getLocation(), "mob.cow.say", 1, 1)


@hook.command("pluginversions")
def on_pluginversions_command(sender, command, label, args):
    """
    /pluginversions
    print all plugins + versions; useful when updating plugins
    """
    plugin_header(sender, "Plugin versions")
    plugins = list(server.getPluginManager().getPlugins())
    plugins.sort(key = lambda pl: pl.getDescription().getName())
    msg(sender, "&3Listing all " + str(len(plugins)) + " plugins and their version:")
    for plugin in plugins:
        msg(sender, "&6" + plugin.getDescription().getName() + "&r: &e" + plugin.getDescription().getVersion())
    return True


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


@hook.command("modules")
def on_modules_command(sender, command, label, args):
    """
    /modules
    list all modules, unloaded modules in red
    """
    plugin_header(sender, "Modules")
    msg(sender, ", ".join([(("&a" if mod in shared["modules"] else "&c") + mod) for mod in shared["load_modules"]]))


@hook.event("player.PlayerTeleportEvent")
def on_player_teleport(event):
    """
    Disable spectator teleportation
    """
    player = event.getPlayer()
    if not event.isCancelled() and str(event.getCause()) == "SPECTATE" and not player.hasPermission("utils.tp.spectate"):
        event.setCancelled(True)
        msg(event.getPlayer(), "&cSpectator teleportation is disabled")