#pylint: disable = F0401
from helpers import *
from java.util.UUID import fromString as id_to_player
from org.bukkit.util import Vector
from math import sin

ff_perm        = "utils.forcefield"
pass_perm      = "utils.forcefield.pass"
ff_prefix      = "&8[&aFF&8]"
ff_users       = []
whitelists     = {}        # {ff_owner_id: [white, listed, ids]}
fd             = 6         # forcefield distance
Xv             = 3.05 / fd # used in set_velocity_away(), this is more efficient.

# /ff admin  is a future option I might implement


@hook.command("forcefield")
def on_forcefield_command(sender, args):
  if not is_player(sender) or not sender.hasPermission(ff_perm):
    noperm(sender)
    return True

  cmd = args[0].lower()

  if not args or cmd == "toggle": # Toggle
    forcefield_toggle(sender)

  elif cmd in ["whitelist", "wl", "wlist"]: # Whitelist commands

    if len(args) >= 2:
      arg = args[1].lower()

      if arg == "list":
        whitelist_list(sender)
      elif arg == "clear":
        whitelist_clear(sender)
      elif arg in ["add", "+"]:
        change_whitelist(sender, True, args[2:])
      elif arg in ["remove", "delete", "rem", "del", "-"]:
        change_whitelist(sender, False, args[2:])
      else:
        invalid_syntax(sender)
    else:
      invalid_syntax(sender)

  elif cmd in ["help", "?"]: # /forcefield help
    forcefield_help(sender)
  else:
    invalid_syntax(sender)
  return True


def change_whitelist(sender, add, names):
  if names:
    sender_id = uid(sender)
    if sender_id not in whitelists:
      whitelists[sender_id] = []

    for name in names:
      player = server.getOfflinePlayer(name)
      if player:
        player_id = uid(player)
        pname     = player.getName()
        sname     = sender.getDisplayName()

        # add player to whitelist if not already added
        if add and player_id not in whitelists[sender_id]:
          if sender != player:
            whitelists[sender_id].append(player_id)
            msg(sender, "%s &aAdded %s to your forcefield whitelist." % (ff_prefix, pname))
            msg(player, "%s &a%s &aadded you to his forcefield whitelist." % (ff_prefix, sname))
          else:
            msg(sender, "%s &cYou can't whitelist yourself." % ff_prefix)

        # remove player from whitelist if whitelisted
        elif not add and player_id in whitelists[sender_id]:
          whitelists[sender_id].remove(player_id)
          msg(sender, "%s &cRemoved %s from your forcefield whitelist." % (ff_prefix, pname))
          msg(player, "%s &c%s &cremoved you from his forcefield whitelist." % (ff_prefix, sname))

      else:
        msg(sender, "%s &cplayer %s &cwas not found." % (ff_prefix, name))
  else:
    msg(sender, "%s &cGive space-separated playernames." % ff_prefix)


def whitelist_list(sender):
  sender_id = uid(sender)
  count     = 0
  msg(sender, "%s &aForceField Whitelist:" % ff_prefix)
  for player_id in whitelists.get(sender_id, []):
    count += 1
    msg(sender, "&a%s. &f%s" % (count, server.getOfflinePlayer(id_to_player(player_id)).getName()))
  if count == 0:
    msg(sender, "&cYour whitelist has no entries.")


def whitelist_clear(sender):
  sender_id = uid(sender)
  if whitelists.get(sender_id):
    whitelists.pop(sender_id)
    msg(sender, "%s &aForceField Whitelist cleared." % ff_prefix)
  else:
    msg(sender, "%s &cYou had no players whitelisted." % ff_prefix)


def forcefield_help(sender):
  msg(sender, "%s &a&l/ForceField Help:" % ff_prefix)
  msg(sender, "&aYou can use the forcefield to keep players on distance.")
  msg(sender, "&2Commands:")
  msg(sender, "&a1. &6/ff &ohelp &a: aliases: ?")
  msg(sender, "&a2. &6/ff &o(toggle)")
  msg(sender, "&a3. &6/ff &owhitelist (list) &a: aliases: wlist, wl")
  msg(sender, "&a4. &6/ff wl &oclear")
  msg(sender, "&a5. &6/ff wl &oadd <players> &a: aliases: &o+")
  msg(sender, "&a6. &6/ff wl &oremove <players> &a: aliases: &odelete, rem, del, -")


def forcefield_toggle(sender):
  sender_id = uid(sender)
  if sender_id in ff_users:
    ff_users.remove(sender_id)
    msg(sender, "%s &aForceField toggle: &cOFF" % ff_prefix)
  else:
    ff_users.append(sender_id)
    msg(sender, "%s &aForceField toggle: &2ON" % ff_prefix)


def invalid_syntax(sender):
  msg(sender, "%s &cInvalid syntax. Use &e/ff ? &cfor info." % ff_prefix)


def move_away(player, entity):
  """
  Pushes entity away from player
  """

  player_loc = player.getLocation()
  entity_loc = entity.getLocation()

  dx = entity_loc.getX() - player_loc.getX()
  vx = sin(Xv * dx)
  dy = entity_loc.getY() - player_loc.getY()
  vy = sin(Xv * dy)
  dz = entity_loc.getZ() - player_loc.getZ()
  vz = sin(Xv * dz)
  entity.setVelocity(Vector(vx , vy, vz))
  # We don't want to go above max_speed, and we dont want to divide by 0.


#--------------------------------------------------------------------------------------------------------#


@hook.event("player.PlayerMoveEvent")
def on_move(event):
  player = event.getPlayer()
  if is_creative(player):
    player_id = uid(player)

    # moving player has forcefield, nerby player should be moved away
    if player_id in ff_users:
      for entity in player.getNearbyEntities(fd, fd, fd):
        whitelisted = (uid(entity) in whitelists.get(player_id, []))
        if is_player(entity) and not entity.hasPermission(pass_perm) and not whitelisted:
          move_away(player, entity)

    # nerby player has forcefield, moving player should be moved away
    if player.hasPermission(pass_perm):
      for entity in player.getNearbyEntities(fd, fd, fd):
        entity_id   = uid(entity)
        ff_enabled  = (entity_id in ff_users)
        whitelisted = (player_id in whitelists.get(entity_id, []))
        if is_player(entity) and is_creative(entity) and ff_enabled and not whitelisted:
          move_away(entity, player)


#--------------------------------------------------------------------------------------------------------#


@hook.event("player.PlayerQuitEvent")
def on_quit(event):
  player = event.getPlayer()
  uid    = uid(player)
  if uid in ff_users:
    ff_users.remove(uid)