#pylint: disable = F0401
from helpers import *
from time import time as now
from sys import exc_info
import thread
import org.bukkit.inventory.ItemStack as ItemStack


# Welcome new players
@hook.event("player.PlayerJoinEvent", "monitor")
def on_join(event):
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
        msg(player, "  &6look at the &a&l/FAQ &6command.")
        msg(player, "  \n&6thank you and happy playing ;)")
        msg(player, " \n \n")

    # teleport to spawn when spawning inside portal
    loginloc = player.getLocation().getBlock().getType()
    headloc = player.getEyeLocation().getBlock().getType()
    if str(loginloc) == "PORTAL" or str(headloc) == "PORTAL":
        msg(player, "&4Looks like you spawned in a portal... Let me help you out")
        msg(player, "&6You can use /back if you &nreally&6 want to go back")
        player.teleport(player.getWorld().getSpawnLocation())


# /sudo - execute command/chat *as* a player/console
@hook.command("sudo")
def on_sudo_command(sender, args):
    if sender.hasPermission("utils.sudo"):
        plugin_header(sender, "Sudo")
        if not checkargs(sender, args, 2, -1):
            return True
        target = args[0]

        cmd =  " ".join(args[1:])
        msg(sender, "Running '&e%s&r' as &3%s" % (cmd, target))
        if cmd[0] == "/":
            cmd = cmd[1:]
            if target.lower() == "server" or target.lower() == "console":
                runas(server.getConsoleSender(), cmd)
            elif server.getPlayer(target):
                runas(server.getPlayer(target), cmd)
            else:
                msg(sender, "&cPlayer %s not found!" % target)
        else:
            if target.lower() == "server" or target.lower() == "console":
                runas(server.getConsoleSender(), "say %s" % cmd)
            elif server.getPlayer(target):
                server.getPlayer(target).chat(cmd)
            else:
                msg(sender, "&cPlayer %s not found!" % target)
    else:
        noperm(sender)
    return True


# /gm - custom gamemode command with extra perms for greater control
#@hook.command("gm")
#def on_gm_command(sender, args):
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


# Clicking redstone_sheep with shears will drop redstone + wool
# also makes a moo sound for the shearer
last_shear = 0.0

@hook.event("player.PlayerInteractEntityEvent")
def on_player_entity_interact(event):
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


# /pluginversions - print all plugins + versions; useful when updating plugins
@hook.command("pluginversions")
def on_pluginversions_command(sender, args):
    plugin_header(sender, "Plugin versions")
    plugins = list(server.getPluginManager().getPlugins())
    plugins.sort(key = lambda pl: pl.getDescription().getName())
    msg(sender, "&3Listing all " + str(len(plugins)) + " plugins and their version:")
    for plugin in plugins:
        msg(sender, "&6" + plugin.getDescription().getName() + "&r: &e" + plugin.getDescription().getVersion())
    return True


# /echo - essentials echo sucks and prints mail alerts sometimes
@hook.command("echo")
def on_echo_command(sender, args):
    msg(sender, " ".join(args).replace("\\n", "\n"))


# /pyeval - run python ingame
# has to be in main.py so we can access the modules
def eval_thread(sender, code):
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


# /pyeval - run python code ingame
@hook.command("pyeval")
def on_pyeval_command(sender, args):
    if sender.hasPermission("utils.pyeval"):
        if not checkargs(sender, args, 1, -1):
            return True
        msg(sender, "%s" % " ".join(args), False, "e")
        thread.start_new_thread(eval_thread, (sender, " ".join(args)))
    else:
        noperm(sender)
    return True


# /modules - list all modules, unloaded modules in red
@hook.command("modules")
def on_modules_command(sender, args):
    plugin_header(sender, "Modules")
    for mod in shared["load_modules"]:
        color = "a" if mod in shared["modules"] else "c"
        msg(sender, "&" + color + mod)


# Disable spectator teleportation
@hook.event("player.PlayerTeleportEvent")
def on_player_teleport(event):
    player = event.getPlayer()
    if not event.isCancelled() and str(event.getCause()) == "SPECTATE" and not player.hasPermission("utils.tp.spectate"):
        event.setCancelled(True)
        msg(event.getPlayer(), "&cSpectator teleportation is disabled")