#pylint: disable = F0401
from helpers import *
from time import time as now
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

#
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

"""
@hook.command("pluginversions")
def on_pluginversions_command(sender, command, label, args):
    ""
    /pluginversions
    print all plugins + versions; useful when updating plugins
    ""
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
"""


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

"""
def eval_argument_thread(event):
    words = event.getMessage()[5:].split(" ")
    for i in range(len(words)):
        word = words[i]
        if is_pyeval_call(word):
            code = word[5:]
            try:
                result = unicode(eval(code))
            except:
                e = exc_info()[1]
                try:
                    eclass = e.__class__
                except AttributeError:
                    eclass = type(e)
                msg(event.getPlayer(), ">>> %s: %s" % (eclass.__name__, e) + "\n ", False, "c")
                result = code
            words[i] = result
    event.setMessage(" ".join(words))
    thread.exit()
"""


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


"""
@hook.event("player.AsyncPlayerChatEvent", "lowest")
def on_chat(event):
    user = event.getPlayer()
    if user.hasPermission("utils.pyeval"):
        thread.start_new_thread(eval_argument_thread, (event,))

@hook.event("player.PlayerCommandPreprocessEvent", "lowest")
def on_cmd(event):
    user = event.getPlayer()
    if user.hasPermission("utils.pyeval"):
        thread.start_new_thread(eval_argument_thread, (event,))

def is_pyeval_call(string):
    return len(string) > 5 and string[:5] == "EVAL:"
"""
