from helpers import *
from java.util.UUID import fromString as idToPlayer

forcefield_permissions = ["utils.forcefield", "utils.forcefield.ignore"]
forcefield_prefix = "&8[&aFF&8]"
fd = 4 # forcefield distance

forcefield_toggle = []
forcefield_whitelist = {}

@hook.command("forcefield")
def onForceFieldCommand(sender, args):
  if not isPlayer(sender) or not sender.hasPermission(forcefield_permissions[0]):
    noperm(sender)
    return True
  sender_id = str(sender.getUniqueId())
  if not args or args[0].lower() == "toggle": #Toggle
    toggle_forcefield(sender, sender_id)
  elif args[0].lower() in ["whitelist", "wl", "wlist"]: #Whitelist commands
    if not args[1:] or args[1].lower() == "list":
      whitelist_list(sender, sender_id)
    elif args[1].lower() == "clear":
      whitelist_clear(sender, sender_id)
    elif args[1].lower() in ["add", "+"]:
      whitelist_add(sender, sender_id, True, args[2:])
    elif args[1].lower() in ["remove", "delete", "rem", "del", "-"]:
      whitelist_add(sender, sender_id, False, args[2:])
    else:
      invalid_syntax(sender)
  elif args[0].lower() in ["help", "?"]: #/forcefield help
    forcefield_help(sender)
  else:
    invalid_syntax(sender)
  return True

def whitelist_add(sender, sender_id, add, players):
  if not players:
    msg(sender, "%s &cGive space-separated playernames." % forcefield_prefix)
  elif add == True and sender_id not in forcefield_whitelist:
    forcefield_whitelist[sender_id] = []
  online_players = []
  for name in list(server.getOnlinePlayers()):
    online_players.append(str(name).lower())
  for name in players:
    online = False
    player = server.getPlayer(name) if name.lower() in online_players else server.getOfflinePlayer(name)
    if name.lower() in online_players:
      online = True
    if not player == "null":
      uid = str(player.getUniqueId())
      pname = player.getDisplayName()
      if add == True and uid not in forcefield_whitelist[sender_id]:
        if player == sender:
          msg(sender, "%s &cYou can't whitelist yourself." % forcefield_prefix)
        else:
          forcefield_whitelist[sender_id].append(uid)
          msg(sender, "%s &aAdded %s to your forcefield whitelist." % (forcefield_prefix, pname))
          if online == True:
            msg(player, "%s %s &aAdded you to his forcefield whitelist." % (forcefield_prefix, sender.getDisplayName()))
      elif add == False and uid in forcefield_whitelist[sender_id]:
        forcefield_whitelist[sender_id].remove(uid)
        msg(sender, "%s &cRemoved %s from your forcefield whitelist." % (forcefield_prefix, pname))
        if online == True:
          msg(player, "%s %s &cRemoved you from his forcefield whitelist." % (forcefield_prefix, sender.getDisplayName())) 
      elif add == True:
        msg(sender, "%s &c%s &cWas already in your forcefield whitelist." % (forcefield_prefix, pname))
      else:
        msg(sender, "%s &c%s &cWas not in your forcefield whitelist." % (forcefield_prefix, pname))
    else:
      msg(sender, "%s &cplayer %s &cwas not found." % (forcefield_prefix, name))

def whitelist_list(sender, sender_id):
  msg(sender, "%s &aForceField Whitelist:" % forcefield_prefix)
  if not sender_id in forcefield_whitelist or len(forcefield_whitelist[sender_id]) == 0:
    msg(sender, "&c      Your whitelist has no entries.")
  else:
    c=0
    for uid in forcefield_whitelist[sender_id]:
      c+=1
      msg(sender, "&a      %s. &f%s" % (c, server.getPlayer(idToPlayer(uid)).getDisplayName()))

def whitelist_clear(sender, sender_id):
  if len(forcefield_whitelist[sender_id]) == 0:
    msg(sender, "%s &cYou had no players whitelisted." % forcefield_prefix)
  else:
    forcefield_whitelist[sender_id] = []
    msg(sender, "%s &aForceField Whitelist cleared." % forcefield_prefix)

def forcefield_help(sender):
  msg(sender, "%s &a&l/ForceField Help: \n&aYou can use the forcefield to keep players on distance." % forcefield_prefix)
  msg(sender, "&2Commands:")
  msg(sender, "&a1. &6/ff &ohelp &a: aliases: ?")
  msg(sender, "&a2. &6/ff &o(toggle)")
  msg(sender, "&a3. &6/ff &owhitelist (list) &a: aliases: wlist, wl")
  msg(sender, "&a4. &6/ff wl &oclear")
  msg(sender, "&a5. &6/ff wl &oadd <players> &a: aliases: &o+")
  msg(sender, "&a6. &6/ff wl &oremove <players> &a: aliases: &odelete, rem, del, -")

def toggle_forcefield(sender, sender_id):
  if sender_id in forcefield_toggle:
    forcefield_toggle.remove(sender_id)
    msg(sender, "%s &aForceField toggle: &cOFF" % forcefield_prefix)
  else:
    forcefield_toggle.append(sender_id)
    msg(sender, "%s &aForceField toggle: &2ON" % forcefield_prefix)

def invalid_syntax(sender):
  msg(sender, "%s &cInvalid syntax. Use &o/ff ? &cfor more info." % forcefield_prefix) 

#--------------------------------------------------------------------------------------------------------#

@hook.event("player.PlayerMoveEvent")
def onMove(event):
  player = event.getPlayer()
  player_id = str(player.getUniqueId())
  if player_id in forcefield_toggle: #player has forcefield, entity should be launched
    for entity in player.getNearbyEntities(fd, fd, fd):
      log("%s" % entity.getName())
      if isPlayer(entity) and not entity.hasPermission(forcefield_permissions[1]) and not str(entity.getUniqueId()) in forcefield_whitelist[player_id] and not entity == player:
        setVelocityAway(player, entity)
  if not player.hasPermission(forcefield_permissions[1]): #player should be launched, entity has forcefield
    for entity in player.getNearbyEntities(fd, fd, fd):
      entity_id = str(entity.getUniqueId())
      if isPlayer(entity) and entity_id in forcefield_toggle and not player_id in forcefield_whitelist[entity_id] and not entity == player:
        if event.getFrom().distance(entity.getLocation()) > 4: 
          event.setCancelled(True)
          msg(player, "&cYou may not get closer than %sm to %s &cdue to their forcefield." % (fd, entity.getDisplayName()))
        else:
          setVelocityAway(entity, player) #Other way around

def setVelocityAway(player, entity): #Moves entity away from player
  player_loc = player.getLocation()
  entity_loc = entity.getLocation()
  dx = entity_loc.getX() - player_loc.getX()
  dy = entity_loc.getY() - player_loc.getY()
  dz = entity_loc.getZ() - player_loc.getZ()
  negator = fd/2
  entity.setVelocity(negator/dx, negator/dy, negator/dz)

#--------------------------------------------------------------------------------------------------------#

@hook.event("player.PlayerQuitEvent")
def onQuit(event):
  try:
    forcefield_toggle.remove(str(event.getPlayer().getUniqueId()))
  except:
    pass 