
from helpers import *
from java.util.UUID import fromString as juuid

forcefield_permissions = ["utils.forcefield", "utils.forcefield.ignore"]
forcefield_prefix = "&8[&aFF&8]"
fd = 4 # forcefield distance

forcefield_toggle = []
forcefield_whitelist = {}

def forcefield_help(sender):
  msg(sender, "%s &a&l/ForceField Help: \n&aYou can use the forcefield to keep players on distance." % forcefield_prefix)
  msg(sender, "&2Commands:")
  msg(sender, "&a1. &6/ff &ohelp &a: aliases: ?")
  msg(sender, "&a2. &6/ff &o(toggle)")
  msg(sender, "&a3. &6/ff &owhitelist (list) &a: aliases: wlist, wl")
  msg(sender, "&a4. &6/ff wl &oclear")
  msg(sender, "&a5. &6/ff wl &oadd <players> &a: aliases: &o+")
  msg(sender, "&a6. &6/ff wl &oremove <players> &a: aliases: &odelete, rem, del, -")
  
#forcefield toggle
@hook.command("forcefield")
def onForceFieldCommand(sender, args):
  if not sender.hasPermission(forcefield_permissions[0]):
    noperm(sender)
    return True
  sender_id = str(sender.getUniqueId())
  args = args.lower()
  if not args or args[0] == "toggle": #Toggle
    if sender_id in forcefield_toggle:
      forcefield_toggle.remove(sender_id)
      msg(sender, "%s &aForceField toggle: &cOFF" % forcefield_prefix)
    else:
      forcefield_toggle.append(sender_id)
      msg(sender, "%s &aForceField toggle: &2ON" % forcefield_prefix)
  elif args[0] in ["whitelist", "wl", "wlist"]: #Whitelist commands
    if not args[1] or args[1] == "list":
      msg(sender, "%s &aForceField Whitelist:") % forcefield_prefix
      c=0
      for uid in forcefield_whitelist[sender_id]:
        c+=1
        msg(sender, "&a%s. &f%s") % (c, juuid(uid))
    elif args[1] == "clear":
      forcefield_whitelist[sender_id] = []
      msg(sender, "%s &aForceField Whitelist cleared.")
    elif args[1] in ["add", "+"]
      if not args[2:]:
        msg(sender, "%s &cGive playernames to add to your whitelist." % forcefield_prefix)
      else:
        for name in args[2:]:
          uid = str(server.getPlayer(name).getUniqueId())
          forcefield_whitelist[sender_id].append(uid)
    elif args[1] in ["remove", "delete", "rem", "del", "-"]:
      if not args[2:]:
        msg(sender, "%s &cGive playernames to remove from your whitelist." % forcefield_prefix)
      else:
        for name in args[2:]:
          uid = str(server.getPlayer(name).getUniqueId())
          forcefield_whitelist[sender_id].remove(uid)
  elif args[0] in ["help", "?"]: #/forcefield help
    forcefield_help(sender)
  else:
  	msg(sender, "%s &cInvalid syntax. Use &o/ff ? &cfor more info.")
  return True

def setVelocityAway(player, entity):
  player_loc = player.getLocation()
  entity_loc = entity.getLocation()
  dx = entity_loc.getX() - player_loc.getX()
  dy = entity_loc.getY() - player_loc.getY()
  dz = entity_loc.getZ() - player_loc.getZ()
  negator = fd/2
  entity.setVelocity(negator/dx, negator/dy, negator/dz)

@hook.event("player.PlayerMoveEvent")
def onMove(event):
  player = event.getPlayer()
  player_id = str(player.getUniqueId())
  if player_id in forcefield_toggle: #player has forcefield, entity should be launched
    for entity in player.getNearbyEntities(fd, fd, fd):
      if isPlayer(entity) and not entity.hasPermission(forcefield_permissions[1]) and not str(entity.getUniqueId()) in forcefield_whitelist[player_id]:
        setVelocityAway(player, entity)
  elif not player.hasPermission(forcefield_permissions[1]): #player should be launched, entity has forcefield
    for entity in player.getNearbyEntities(fd, fd, fd):
      entity_id = str(entity.getUniqueId())
      if isPlayer(entity) and entity_id in forcefield_toggle and not player_id in forcefield_whitelist[entity_id]:
        if event.getFrom().distance(entity.getLocation()) > 4: 
          event.setCancelled(True)
          msg(player, "&cYou may not get closer than %sm to %s due to their forcefield." % (fd, entity.getDisplayName()))
        else:
          setVelocityAway(entity, player)



