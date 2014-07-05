#pylint: disable=F0401
from helpers import *
import org.bukkit.inventory.ItemStack as ItemStack

#
# Welcome new players
#

@hook.event("player.PlayerJoinEvent", "monitor")
def onJoin(event):
  player = event.getPlayer()

  # send welcome broadcast
  if not server.getOfflinePlayer(player.getName()).hasPlayedBefore():
    broadcast("utils.greet_new", "")
    broadcast("utils.greet_new", "&a&lPlease welcome &f" + player.getDisplayName() + " &a&lto Redstoner!")
    broadcast("utils.greet_new", "")

    # clear out some eventual crap before
    msg(player, " \n \n \n \n \n \n \n \n \n \n \n \n ")
    msg(player, "  &4Welcome to the Redstoner Server!")
    msg(player, "  &6please make sure to read the info here:")
    msg(player, "  &6/The FAQ at /spawn")
    msg(player, "  &6/rules")
    msg(player, "  &6/ranks")
    msg(player, "  &6thank you and happy playing ;)")
    msg(player, " \n ")

  # teleport to spawn when spawning inside portal
  loginloc = player.getLocation().getBlock().getType()
  headloc = player.getEyeLocation().getBlock().getType()
  if str(loginloc) == "PORTAL" or str(headloc) == "PORTAL":
    msg(player, "&4Looks like you spawned in a portal... Let me help you out")
    msg(player, "&6You can use /back if you &nreally&6 want to go back")
    player.teleport(player.getWorld().getSpawnLocation())


#
# /sudo - execute command/chat *as* a player/console
#


@hook.command("sudo")
def onSudoCommand(sender, args):
  if sender.hasPermission("utils.sudo"):
    plugHeader(sender, "Sudo")
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


#
# Clicking redstone_sheep with shears will drop redstone + wool and makes a moo sound
#

@hook.event("player.PlayerInteractEntityEvent")
def onPlayerInteractEntity(event):
  if not event.isCancelled():
    sender = event.getPlayer()
    entity = event.getRightClicked()
    if isPlayer(entity) and str(entity.getUniqueId()) == "ae795aa8-6327-408e-92ab-25c8a59f3ba1" and str(sender.getItemInHand().getType()) == "SHEARS" and str(sender.getGameMode()) == "CREATIVE":
      for i in range(5):
        entity.getWorld().dropItemNaturally(entity.getLocation(), ItemStack(bukkit.Material.getMaterial("REDSTONE")))
        entity.getWorld().dropItemNaturally(entity.getLocation(), ItemStack(bukkit.Material.getMaterial("WOOL")))
      sender.playSound(entity.getLocation(), "mob.cow.say", 1, 1)


#
# Various text commands
#

@hook.command("rules")
def onRulesCommand(sender, args):
  if not checkargs(sender, args, 0, 0):
    return True
  arrow = u"\u2192"
  plugHeader(sender, "Redstoner rules")
  msg(sender, "&aPlease look at our rules on redstoner.com/info")
  return True


@hook.command("nick")
def onNickCommand(sender, args):
  plugHeader(sender, "Nicknames")
  msg(sender, "&aPlease look at our nickname guidelines on redstoner.com/info")
  return True


@hook.command("ranks")
def onRanksCommand(sender, args):
  if not checkargs(sender, args, 0, 0):
    return True
  plugHeader(sender, "Rank colours")
  msg(sender, "&aPlease look at our rank info on redstoner.com/info")
  return True


@hook.command("donate")
def onDonateCommand(sender, args):
  if not checkargs(sender, args, 0, 0):
    return True
  msg(sender, "")
  plugHeader(sender, "Donations")
  msg(sender, " &aWant to donate? Awesome!")
  msg(sender, " &6all info is at &nredstoner.com/donate&r")
  msg(sender, "")
  return True

#
# /pluginversions - print all plugins + versions; useful when updating plugins
#

@hook.command("pluginversions")
def onPluginversionsCommand(sender, args):
  plugHeader(sender, "Plugin versions")
  plugins = list(server.getPluginManager().getPlugins())
  plugins.sort(key=lambda pl: pl.getName())
  msg(sender, "&3Listing all " + str(len(plugins)) + " plugins and their version:")
  for plugin in plugins:
    msg(sender, "&6" + plugin.getName() + "&r: &e" + plugin.getDescription().getVersion())
  return True


#
# Various command aliases
#

@hook.command("spawn")
def onSpawnCommand(sender, args):
  warp(sender, args, "spawn")
  return True

@hook.command("cr")
def onCrCommand(sender, args):
  warp(sender, args, "cr")
  return True

@hook.command("tr")
def onTrCommand(sender, args):
  warp(sender, args, "tr")
  return True

@hook.command("faq")
def onFaqCommand(sender, args):
  warp(sender, args, "faq")
  return True
