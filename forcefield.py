from helpers import *
from java.util.UUID import fromString as id_to_player
from org.bukkit.util import Vector
from math import sin

ff_perms       = ["utils.forcefield", "utils.forcefield.ignore"]
ff_prefix      = "&8[&aFF&8]"
ff_users       = []
whitelists     = {}  # {ff_owner_id: [white, listed, ids]}
fd             = 6   # forcefield distance
Xv            = 3.05 / fd # used in set_velocity_away(), this is more efficient.

# /ff admin  is a future option I might implement

@hook.command("forcefield")
def on_forcefield_command(sender, args):
  if not is_player(sender) or not sender.hasPermission(ff_perms[0]):
    noperm(sender)
    return True
  sender_id = str(sender.getUniqueId())

  if not args or args[0].lower() == "toggle": #Toggle
    forcefield_toggle(sender)

  elif args[0].lower() in ["whitelist", "wl", "wlist"]: #Whitelist commands
    if not args[1:] or args[1].lower() == "list":
      whitelist_list(sender)
    elif args[1].lower() == "clear":
      whitelist_clear(sender)
    elif args[1].lower() in ["add", "+"]:
      whitelist_add(sender, True, args[2:])
    elif args[1].lower() in ["remove", "delete", "rem", "del", "-"]:
      whitelist_add(sender, False, args[2:])
    else:
      invalid_syntax(sender)

  elif args[0].lower() in ["help", "?"]: #/forcefield help
    forcefield_help(sender)
  else:
    invalid_syntax(sender)
  return True


def whitelist_add(sender, add, players):
  if not players: msg(sender, "%s &cGive space-separated playernames." % ff_prefix)
  else:
    sender_id = str(sender.getUniqueId())
    whitelists[sender_id] = [] if sender_id not in whitelists else whitelists[sender_id]
    for name in players:
      player = server.getOfflinePlayer(name)
      if player:
        player_id = str(player.getUniqueId())
        pname = player.getName()
        sname = stripcolors(sender.getDisplayName())
        online = True if player in list(server.getOnlinePlayers()) else False
        if add == True and player_id not in whitelists[sender_id]:
          if not sender == player:
            whitelists[sender_id].append(player_id)
            msg(sender, "%s &aAdded %s to your forcefield whitelist." % (ff_prefix, pname))
            if online == True: msg(player, "%s &a%s &aadded you to his forcefield whitelist." % (ff_prefix, sname))
          else: msg(sender, "%s &cYou can't whitelist yourself." % ff_prefix)
        elif add == False and player_id in whitelists[sender_id]:
          whitelists[sender_id].remove(player_id)
          msg(sender, "%s &cRemoved %s from your forcefield whitelist." % (ff_prefix, pname))
          if online == True: msg(player, "%s &c%s &cremoved you from his forcefield whitelist." % (ff_prefix, sname))
        elif add == True: msg(sender, "%s &c%s &cwas already in your forcefield whitelist." % (ff_prefix, pname))
        else: msg(sender, "%s &c%s &cwas not in your forcefield whitelist." % (ff_prefix, pname))
      else: msg(sender, "%s &cplayer %s &cwas not found." % (ff_prefix, name))


def whitelist_list(sender):
  sender_id = str(sender.getUniqueId())
  msg(sender, "%s &aForceField Whitelist:" % ff_prefix)
  count = 0
  for player_id in whitelists.get(sender_id, []):
    count += 1
    msg(sender, "&a      %s. &f%s" % (count, server.getOfflinePlayer(id_to_player(player_id)).getName()))
  if count == 0:
    msg(sender, "&c      Your whitelist has no entries.")


def whitelist_clear(sender):
  sender_id = str(sender.getUniqueId())
  if len(whitelists[sender_id]) == 0:
    msg(sender, "%s &cYou had no players whitelisted." % ff_prefix)
  else:
    whitelists.pop(sender_id)
    msg(sender, "%s &aForceField Whitelist cleared." % ff_prefix)


def forcefield_help(sender):
  msg(sender, "%s &a&l/ForceField Help: \n&aYou can use the forcefield to keep players on distance." % ff_prefix)
  msg(sender, "&2Commands:")
  msg(sender, "&a1. &6/ff &ohelp &a: aliases: ?")
  msg(sender, "&a2. &6/ff &o(toggle)")
  msg(sender, "&a3. &6/ff &owhitelist (list) &a: aliases: wlist, wl")
  msg(sender, "&a4. &6/ff wl &oclear")
  msg(sender, "&a5. &6/ff wl &oadd <players> &a: aliases: &o+")
  msg(sender, "&a6. &6/ff wl &oremove <players> &a: aliases: &odelete, rem, del, -")


def forcefield_toggle(sender):
  sender_id = str(sender.getUniqueId())
  if sender_id in ff_users:
    ff_users.remove(sender_id)
    msg(sender, "%s &aForceField toggle: &cOFF" % ff_prefix)
  else:
    ff_users.append(sender_id)
    msg(sender, "%s &aForceField toggle: &2ON" % ff_prefix)


def invalid_syntax(sender):
  msg(sender, "%s &cInvalid syntax. Use &o/ff ? &cfor info." % ff_prefix)


#--------------------------------------------------------------------------------------------------------#


@hook.event("player.PlayerMoveEvent")
def on_move(event):
  player = event.getPlayer()
  if is_creative(player):
    player_id = str(player.getUniqueId())
    if player_id in ff_users: # player has forcefield, entity should be blocked
      log("1")
      for entity in player.getNearbyEntities(fd, fd, fd):
        if is_player(entity) and is_creative(entity) and not entity.hasPermission(ff_perms[1]) and not (str(entity.getUniqueId()) in whitelists.get(player_id, [])):
          #if not whitelists[entity_id], check in blank list e.g. False
          move_away(player, entity)

    if player.hasPermission(ff_perms[1]): # player should be blocked, entity has forcefield
      for entity in player.getNearbyEntities(fd, fd, fd):
        entity_id = str(entity.getUniqueId())
        if is_player(entity) and is_creative(entity) and (entity_id in ff_users) and not (player_id in whitelists.get(entity_id, [])):
          #if not whitelists[entity_id], check in blank list e.g. False
          move_away(entity, player)


def move_away(player, entity): #Moves entity away from player
  player_loc = player.getLocation()
  entity_loc = entity.getLocation()
  dx = entity_loc.getX() - player_loc.getX()
  vx = sin(Xv * dx)
  dy = entity_loc.getY() - player_loc.getY()
  vy = sin(Xv * dy)
  dz = entity_loc.getZ() - player_loc.getZ()
  vz = sin(Xv * dz)
  entity.setVelocity(Vector(vx , vy, vz))
  #We don't want to go above max_speed, and we dont want to divide by 0.


#--------------------------------------------------------------------------------------------------------#


@hook.event("player.PlayerQuitEvent")
def on_quit(event):
  player = event.getPlayer()
  uid    = str(player.getUniqueId())
  if uid in ff_users:
    ff_users.remove(uid)