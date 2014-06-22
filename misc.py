#pylint: disable=F0401
from helpers import *
import org.bukkit.inventory.ItemStack as ItemStack

#
# Welcome new players
#

@hook.event("player.PlayerJoinEvent", "monitor")
def onJoin(event):
  player = event.getPlayer()
  for item in player.getInventory():
    if (item != None and item.getTypeId() == 175 and item.getDurability() > 5):
      item.setDurability(0)
      log("&cPlayer '%s' had 175:6 or higher in his inventory! Replaced with 175:0" % player.getName())
      msg(player, " &a----------------------------------------------------")
      msg(player, " &4&lWARNING: &cYou had 175:7 (invalid flower) in your inventory.")
      msg(player, " &cThis crashes your client. We have replaced it with 175:0.")
      msg(player, " &a----------------------------------------------------")

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
    if isPlayer(entity) and str(entity.getUniqueId()) == "ae795aa8-6327-408e-92ab-25c8a59f3ba1" and str(sender.getItemInHand().getType()) == "SHEARS" and str(sender.getGameMode() == "CREATIVE"):
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
  msg(sender, "&31 &7"  + arrow + " &bMake use of common sense and respect.")
  msg(sender, "&32 &7"  + arrow + " &bDo NOT ask for promotion.")
  msg(sender, "&33 &7"  + arrow + " &bDo NOT use cheats in Survival worlds.")
  msg(sender, "&34 &7"  + arrow + " &bDo NOT spam entities or leave clocks running.")
  msg(sender, "&35 &7"  + arrow + " &bSwearing is okay, offending is NOT.")
  msg(sender, "&36 &7"  + arrow + " &bDo NOT build huge walls around your plot.")
  msg(sender, "&37 &7"  + arrow + " &bListen to the admins and mods, even if it is not in the rules.")
  msg(sender, "&38 &7"  + arrow + " &bOnly english in public chat.")
  msg(sender, "&39 &7"  + arrow + " &bEveryone can get punished, even admins.")
  msg(sender, "&310 &7" + arrow + " &bSame rules for everyone.")
  msg(sender, "&311 &7" + arrow + " &bNO OP items.")
  msg(sender, "&312 &7" + arrow + " &bDo NOT trap other players.")
  return True


@hook.command("history")
def onHistoryCommand(sender, args):
  if not checkargs(sender, args, 0, 0):
    return True
  plugHeader(sender, "Redstoner history")
  msg(sender, "")
  msg(sender, " &2First, oliverissocool1 owned redstoner.com plus the server which usually had 10-15 players on.\n")
  msg(sender, " &2Oliver became lazy and thus moved ownership to oleerik, who was another admin there.\n")
  msg(sender, " &2Dico joined the server and later he became a moderator.\n")
  msg(sender, " &2But then oleerik also became lazy, lost interest and shut down the server.\n")
  msg(sender, " &2Some time later he offered dico to use the server and he was - of course - interested in it.\n")
  msg(sender, " &2The server did not have the old worlds and configuration anymore and it was down for a good while, so it was like a complete new server.\n")
  msg(sender, " &2He invited some friends to help him set up the server before opening it to the public (as his 'fan server').\n")
  msg(sender, " &2Redstone Sheep was one of these friends and made the website, he happened to become the guy who maintains the whole server.\n")
  msg(sender, " &2The server somtimes crashed or lost it's connection and we were not too happy plus oleerik was always paying for it, without using it himself.\n")
  msg(sender, " &2PanFritz first helped out by donating and then offered to host a physical server.\n")
  msg(sender, " &2We discussed a lot and moved everything, it worked very well.\n")
  msg(sender, " &2A month or two later, a new server was bought from donations and it took some time until the new machine was ready, but the move went quick and without much downtime.\n")
  msg(sender, " &2Another couple months later, the server underwent many major changes, this update was known as Redstoner 2.0 and vastly improved almost every aspect of the server.\n")

  msg(sender, " &2That's our story for now.")
  return True


@hook.command("nick")
def onNickCommand(sender, args):
  plugHeader(sender, "Nicknames")
  msg(sender, "&31. &aYou need to be Donor or Trusted. &8&o(See /ranks)")
  msg(sender, "&32. &aHas to begin with &nat least&3&o " + sender.getName()[:3] + "&a.")
  msg(sender, "&33. &aMore characters are required when other players")
  msg(sender, "&a   begin with the same 3 letters.")
  msg(sender, "&34. &aIt must not be longer than your name.")
  msg(sender, "&a   (e.g. No addons like '&3" + sender.getName() + "TheCoolOne&a'.)")
  msg(sender, "&6Ask any staff to get your nickname. Requests are ignored when requirements are not covered. Be patient.")
  return True


@hook.command("ranks")
def onRanksCommand(sender, args):
  if not checkargs(sender, args, 0, 0):
    return True
  plugHeader(sender, "Rank colours")
  msg(sender, " &7Guest")
  msg(sender, " &fMember")
  msg(sender, " &aBuilder")
  msg(sender, " &3Trusted")
  msg(sender, " &cModerator")
  msg(sender, " &4Admin")
  plugHeader(sender, "Rank info")
  msg(sender, " &oitalic &rnames are nicks. use &a/realname <nick>&r to check")
  msg(sender, " &eDonator&r rank has <name> &e$&r")
  msg(sender, " &eDonator+&r rank has <name> &e&l$&r")
  msg(sender, " To get the &e$&r, see &a/donate&r for more info")
  msg(sender, "")
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
  plugins = server.getPluginManager().getPlugins().tolist()
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