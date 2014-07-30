from helpers import *

friends           = open_json_file("friends", {}) # {Player_UUID:[List_of_friend_uuids]}
friend_join_sound = "random.orb"



@hook.event("player.PlayerJoinEvent", "high") # creates sound and sends a bold message on friend join
def fjm(event): # friend join message
  player    = event.getPlayer()
  player_id = uid(player)

  for onlineplayer in list(server.getOnlinePlayers()):
    if player_id in friends.get(uid(onlineplayer), []):
      msg(onlineplayer, "&a&l%s &ajoined!" % player.getName())
      onlineplayer.playSound(onlineplayer.getLocation(), friend_join_sound, 1, 0)


def save_friends(): # saves to friends file
  save_json_file("friends", friends)


def friendmessage(player, message): # sends a message with a prefix
  msg(player, "&7[&aFriends&7] " + message)


def ls(sender):
  sender_friends = friends.get(uid(sender), False)
  if sender_friends:
    friends_string = ""
    for uuid in sender_friends:
      friends_string += (retrieve_player(uuid).getName() + ", ")
    friendmessage(sender, "&aYour friends list: " + friends_string[:len(friends_string)-2])
  else:
    friendmessage(sender, "&cYour friends list is empty")


def clear(sender):
  sender_id = uid(sender)

  if friends.get(sender_id, False):
    for uuid in friends[sender_id]:
      friendmessage(retrieve_player(uuid), "&c&o%s &cremoved you from their friends list" % stripcolors(sender.getDisplayName()))
    friends.pop(sender_id)
    friendmessage(sender, "&aFriends list cleared")
    save_friends()
  else:
    friendmessage(sender, "&cYour friends list is already empty")


def add(sender, names):
  sender_id     = uid(sender)
  added         = []
  notfound      = []
  friendalready = []

  if not sender_id in friends:
    friends[sender_id] = []

  for name in names:
    player = server.getOfflinePlayer(name)
    # FIXME: breaks if player not known
    # FIXME: might to a blocking call, maybe we can use getOfflinePlayers()
    if known_player(player):
      player_id = uid(player)
      not_yourself = player != sender

      if not player_id in friends[sender_id]:
        if not_yourself:
          friends[sender_id].append(player_id)
          added.append(player.getName())
          friendmessage(player.getPlayer(), "&a&o%s &aadded you to their friends list" % stripcolors(sender.getDisplayName()))
      else:
        friendalready.append(player.getName())

    else:
      notfound.append(name)

  save_friends()
  if added:
    friendmessage(sender, "&a&o%s&a added." % ", ".join(added))
  if notfound:
    friendmessage(sender, "&c&o%s&c not found." % ", ".join(notfound))
  if friendalready:
    friendmessage(sender, "&c&o%s&c is/are already your friend." % ", ".join(friendalready))
  if not not_yourself:
    friendmessage(sender, "&cYou can't add yourself to your friends list.")


def rem(sender, names):
  sender_id  = uid(sender)
  removed    = []
  notfound   = []
  notafriend = []

  for name in names:
    player = server.getOfflinePlayer(name)
    if known_player(player):
      player_id = uid(player)
      if player_id in friends.get(sender_id, []):
        friends[sender_id].remove(player_id)
        removed.append(player.getName())
        friendmessage(player.getPlayer(), "&c&o%s &cremoved you from their friends list" % stripcolors(sender.getDisplayName()))
      else:
        notafriend.append(player.getName())
    else:
      notfound.append(name)

  save_friends()
  if removed:
    friendmessage(sender, "&a&o%s&a removed." % ", ".join(removed))
  if notfound:
    friendmessage(sender, "&c&o%s&c not found." % ", ".join(notfound))
  if notafriend:
    friendmessage(sender, "&c&o%s&c is/are not in your friends list." % ", ".join(notafriend))


def fhelp(sender):
  friendmessage(sender, "&a&l/friends help")
  msg(sender, "&a1. /friends &oadd <names...>    &6aliases: &o+")
  msg(sender, "&a2. /friends &orem <names...>    &6aliases: &oremove, delete, del, -")
  msg(sender, "&a3. /friends &oclear              &6aliases: &o/")
  msg(sender, "&a4. /friends &olist                 &6aliases: &olst, *")
  msg(sender, "&a5. /friends &ohelp               &6aliases: &o?")


@hook.command("friends")
def on_friend_command(sender, args):
  if not is_player(sender):
    friendmessage(sender, "&c&lYou can't have friends!")
    return True

  cmd   = args[0] if args else None
  fargs = args[1:]

  # /friends list
  if cmd in ["list", "lst", "*"]:
    ls(sender)

  # /friends clear
  elif cmd in ["clear", "/"]:
    clear(sender)

  # /friends add <names>
  elif cmd in ["add", "+"]:
    if fargs:
      add(sender, fargs)
    else:
      fhelp(sender)

  # /friends remove <names>
  elif cmd in ["remove", "rem", "delete", "del", "-"]:
    if fargs:
      rem(sender, fargs)
    else:
      fhelp(sender)

  else:
    fhelp(sender)
  return True