from helpers import *

gamemode_permission = {"self":"gamemode.self","other":"gamemode.other"}

# Helping functions

def setGamemode(sender, gmstring):
  gmstring = gmstring.lower()
  if is_player(sender):
    if gmstring == "c" || gmstring == "creative" || gmstring == "1":
      sender.setGameMode(GameMode.CREATIVE)
    elif gmstring == "s" || gmstring == "survival" || gmstring == "0":
      sender.setGameMode(GameMode.SURVIVAL)
    elif gmstring == "a" || gmstring == "adventure" || gmstring == "2":
      sender.setGameMode(GameMode.ADVENTURE)
    else
      msg(sender, "&c%s is no known gamemode (survival/creative/adventure)")
  else
    msg(sender, "&cYou have to be a valid player to perform this command. Try /gamemode <player> <gamemode>")

# /toolbox
@hook.command("toolbox", desc="The basic command of Toolbox")
def toolbox_command(sender, args):  
  msg(sender, "&6Toolbox&f is a command library written for Redstoner.com")

# /gamemode
@hook.command("gamemode", aliases=["gm"], desc="Change a player's gamemode")
def toolbox_gamemode_command(sender, args):
  param1 = args[0].lower() if len(args)>0 else None
  param2 = args[1] if len(args)>1 else None
  
  if len(args) == 1:
    if sender.hasPermission(gamemode_permission["self"]) || sender.hasPermission(gamemode_permission["other"]):
      setGameMode(sender, param1)
    else
      noperm(sender)
  elif len(args) == 2:
    if sender.hasPermission(gamemode_permission["other"]):
      if server.getPlayer(param) != None:  
        setGameMode(server.getPlayer(param), param2)
      else
        msg(sender, "&cThere's no online player called "+param)
