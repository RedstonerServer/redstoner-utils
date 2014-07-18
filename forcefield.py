#pylint: disable = F0401
from helpers import *
from org.bukkit.util import Vector
from math import sin

ff_perm         = "utils.forcefield"
pass_perm       = "utils.forcefield.ignore"
ff_prefix       = "&8[&bFF&8] "
ff_users        = []
fd              = 6                                                         # forcefield distance
Xv              = 2.95 / fd                                                 # used in move_away(), this is more efficient.
whitelists_filename = "plugins/redstoner-utils.py.dir/files/forcefield.json"
whitelists      = {}                     # {ff_owner_id: [white, listed, ids]} (Adding file usage later, should be simple but just not yet.)


# /ff admin  is a future option I might implement


@hook.command("forcefield")
def on_forcefield_command(sender, args):
  if not is_player(sender) or not sender.hasPermission(ff_perm):
    noperm(sender)
    return True

  if not args or args[0].upper() in ["ON", "OFF"]: # Toggle
    forcefield_toggle(sender, args[:1])
    return True

  args[0] = args[0].upper() # If it gets to this point, there are argument(s).
  if args[0] in ["WHITELIST", "WL", "WLIST"]: # Whitelist commands
    if not args[1:] or args[1].upper() == "LIST":
      whitelist_list(sender)
      return True

    args[1] = args[1].upper() # If it gets too this point, there is a second argument.
    if args[1] == "CLEAR":
      whitelist_clear(sender)
    elif args[1] in ["ADD", "+"]:
      change_whitelist(sender, True, args[2:])
    elif args[1] in ["REMOVE", "DELETE", "REM", "DEL", "-"]:
      change_whitelist(sender, False, args[2:])
    else:
      forcefield_header(sender, "&cInvalid syntax. Use &e/ff ? &cfor info.")

  elif args[0] in ["HELP", "?"]: # /forcefield help
    forcefield_help(sender)
  else:
    forcefield_header(sender, "&cInvalid syntax. Use &e/ff ? &cfor info.")
  return True


def change_whitelist(sender, add, names): #Add names if add == True else Remove names.
  if names:
    sender_id = uid(sender)
    if sender_id not in whitelists:
      whitelists[sender_id] = []

    for name in names:
      player = server.getOfflinePlayer(name)
      if player.hasPlayedBefore():
        player_id = uid(player)
        pname     = player.getName()
        sname     = stripcolors(sender.getDisplayName())

        # add player to whitelist if not already added
        if add and player_id not in whitelists[sender_id]:
          if sender != player:
            whitelists[sender_id].append(player_id)
            forcefield_header(sender, "&bAdded &f%s &bto your forcefield whitelist." % pname)
            forcefield_header(player, "&f%s &badded you to his forcefield whitelist." % sname)
          else:
            forcefield_header(sender, "&cYou can't whitelist yourself.")

        # remove player from whitelist if whitelisted
        elif not add and player_id in whitelists[sender_id]:
          whitelists[sender_id].remove(player_id)
          forcefield_header(sender, "&cRemoved &f%s &cfrom your forcefield whitelist." % pname)
          forcefield_header(player, "&f%s &cremoved you from his forcefield whitelist." % sname)

        # player was already / not added to whitelist
        else:
          var = "already" if add == True else "not"
          forcefield_header(sender, "&f%s &cwas %s in your forcefield whitelist!" % (pname, var))

      else:
        forcefield_header(sender, "&cplayer &f%s &cwas not found." % name)
  else:
    forcefield_header(sender, "&cGive space-separated playernames.")


def whitelist_list(player):
  player_id = uid(player)
  count     = 0
  forcefield_header(player, "&bForcefield whitelist:")
  for user_id in whitelists.get(player_id, []):
    count += 1
    pname = retrieve_player(user_id).getName()
    msg(player, "&b %s. &f%s" % (count, pname))
  if count == 0:
    msg(player, "&c Your whitelist has no entries.")


def whitelist_clear(player):
  player_id = uid(player)
  if whitelists.get(player_id):
    whitelists.pop(player_id)
    forcefield_header(player, "&bForcefield whitelist cleared.")
  else:
    forcefield_header(player, "&cYou had no players whitelisted.")


def forcefield_help(player):
  msg(player, " ")
  forcefield_header(player, "&b&l/Forcefield help:     Your forcefield is %s" % ("&2&lON" if uid(player) in ff_users else "&c&lOFF"))
  msg(player, "&b You can use the forcefield to keep players on distance.")
  msg(player, "&b Commands:")
  msg(player, "&b 1. &6/ff &ohelp &b                         aliases: &6?")
  msg(player, "&b 2. &6/ff &o(on off)")
  msg(player, "&b 3. &6/ff &owhitelist (list) &b             aliases: &6wlist, wl")
  msg(player, "&b 4. &6/ff wl &oclear")
  msg(player, "&b 5. &6/ff wl &oadd <players> &b         aliases: &6+")
  msg(player, "&b 6. &6/ff wl &oremove <players> &b     aliases: &6delete, rem, del, -")
  msg(player, " ")


def forcefield_toggle(player, arg): # arg is a list with max 1 string
  player_id = uid(player)
  enabled   = player_id in ff_users
  argoff    = arg[0].upper() == "OFF" if arg else False
  if enabled and (not arg or argoff): # 3 possibilities for arg: [], ["OFF"], ["ON"]. This is the most efficient way. (Case insensitive)
    ff_users.remove(player_id)
    forcefield_header(player, "&bForcefield toggle: &c&lOFF")
  elif not enabled and not argoff:
    ff_users.append(player_id)
    forcefield_header(player, "&bForcefield toggle: &2&lON")
  else:
    forcefield_header(player, "&cYour forcefield is already %s!" % arg[0].lower())


def forcefield_header(player, message):
  msg(player, "%s %s" % (ff_prefix, message))


#--------------------------------------------------------------------------------------------------------#


@hook.event("player.PlayerMoveEvent")
def on_move(event):
  if ff_users:
    player = event.getPlayer()
    if is_creative(player):
      player_id = uid(player)

      # moving player has forcefield, nearby player should be moved away
      if player_id in ff_users:
        for entity in player.getNearbyEntities(fd, fd, fd):
          whitelisted = (uid(entity) in whitelists.get(player_id, []))
          if is_player(entity) and not entity.hasPermission(pass_perm) and not whitelisted:
            move_away(player, entity)

      # nearby player has forcefield, moving player should be moved away
      if not player.hasPermission(pass_perm):
        for entity in player.getNearbyEntities(fd, fd, fd):
          entity_id   = uid(entity)
          ff_enabled  = (entity_id in ff_users)
          whitelisted = (player_id in whitelists.get(entity_id, []))
          if is_player(entity) and is_creative(entity) and ff_enabled and not whitelisted:
            move_away(entity, player)


def move_away(player, entity):
  # Pushes entity away from player

  player_loc = player.getLocation()
  entity_loc = entity.getLocation()

  dx = entity_loc.getX() - player_loc.getX()
  vx = sin(Xv * dx)
  dy = entity_loc.getY() - player_loc.getY()
  vy = sin(Xv * dy)
  dz = entity_loc.getZ() - player_loc.getZ()
  vz = sin(Xv * dz)
  entity.setVelocity(Vector(vx , vy, vz))


#--------------------------------------------------------------------------------------------------------#


@hook.event("player.PlayerQuitEvent")
def on_quit(event):
  player    = event.getPlayer()
  player_id = uid(player)
  if player_id in ff_users:
    ff_users.remove(player_id)