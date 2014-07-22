from helpers import *

friends_filename  = "plugins/redstoner-utils.py.dir/files/friends.json"
friends           = open_json_file(friends_filename) # {Player_UUID:[List_of_friend_uuids]}
friend_join_sound = "random.orb"



@hook.event("player.PlayerJoinEvent", "high") # creates sound and sends a bold message on friend join
def fjm(event): # friend join message
  player    = event.getPlayer()
  player_id = uid(player)
  playerlist = ""
  for onlineplayer in list(server.getOnlinePlayers()):
    if player_id in friends.get(uid(onlineplayer), []):
      msg(onlineplayer, "&a&l%s &ajoined!" % player.getName())
      onlineplayer.playSound(onlineplayer.getLocation(), friend_join_sound, 1, 0)


def save_friends(): # saves to friends file
  save_json_file(friends_filename, friends)


def friendmessage(player, message): # sends a message with a prefix
  msg(player, "&7[&aFriends&7] " + message)


@hook.command("friends")
def on_friend_command(sender, args):
  if not is_player(sender):
    friendmessage(sender, "&c&lYou can't have friends!")
    return True
  sender_id = uid(sender)
  if not args or args[0] in ["list", "lst", "*"]: #/friends list
    sender_friends = friends.get(sender_id, False)
    if sender_friends:
      friends_string = ""
      for uuid in sender_friends:
        friends_string += (retrieve_player(uuid).getName() + ", ")
      friendmessage(sender, "&aYour friends list: " + friends_string[:len(friends_string)-2])
    else:
      friendmessage(sender, "&cYour friends list is empty")

  elif args[0] in ["clear", "/"]: #/friends clear
    if friends.get(sender_id, False):
      for uuid in friends[sender_id]:
        friendmessage(retrieve_player(uuid), "&c&o%s &cremoved you from their friends list" % stripcolors(sender.getDisplayName()))
      friends.pop(sender_id)
      friendmessage(sender, "&aFriends list cleared")
      save_friends()
    else:
      friendmessage(sender, "&cYour friends list is already empty")
  
  elif args[0] in ["add", "+"]: #/friends add <names>
    if args[1:]:
      if not sender_id in friends:
        friends[sender_id] = []
      added         = ""
      notfound      = ""
      friendalready = ""
      for name in args[1:]:
        player = server.getOfflinePlayer(name)
        if played_before(player):
          player_id = uid(player)
          not_yourself = player != sender
          if not player_id in friends[sender_id]:
            if not_yourself:
              friends[sender_id].append(player_id)
              added += (player.getName() + ", ")
              friendmessage(player.getPlayer(), "&a&o%s &aadded you to their friends list" % stripcolors(sender.getDisplayName()))
          else:
            friendalready += (player.getName() + ", ")
        else: 
          notfound += (name + ", ")
      save_friends()
      if added     != "":
        friendmessage(sender, "&a&o%s&a added."                      % added[:len(added)-2])
      if notfound  != "":
        friendmessage(sender, "&c&o%s&c not found."                  % notfound[:len(notfound)-2])
      if friendalready != "":
        friendmessage(sender, "&c&o%s&c is/are already your friend." % friendalready[:len(friendalready)-2])
      if not not_yourself:
        friendmessage(sender, "&cYou can't add yourself to your friends list.")
    else:
      friendmessage(sender, "&cUsage: &o/friends + <names...>")

  elif args[0] in ["remove", "rem", "delete", "del", "-"]: #/friends remove <names>
    if args[1:]:
      removed    = ""
      notfound   = ""
      notafriend = ""
      for name in args[1:]:
        player = server.getOfflinePlayer(name)
        if played_before(player):
          player_id = uid(player)
          if player_id in friends.get(sender_id, []):
            friends[sender_id].remove(player_id)
            removed += (player.getName() + ", ")
            friendmessage(player.getPlayer(), "&c&o%s &cremoved you from their friends list" % stripcolors(sender.getDisplayName()))
          else:
            notafriend += (player.getName() + ", ")
        else: 
          notfound += (name + ", ")
      save_friends()
      if removed    != "":
        friendmessage(sender, "&a&o%s&a removed."                         % removed[:len(removed)-2])
      if notfound   != "":
        friendmessage(sender, "&c&o%s&c not found."                       % notfound[:len(notfound)-2])
      if notafriend != "":
        friendmessage(sender, "&c&o%s&c is/are not in your friends list." % notafriend[:len(notafriend)-2])
    else:
      friendmessage(sender, "&cUsage: &o/friends - <names...>")

  elif args[0] in ["help", "?"]: #/friends help
    friendmessage(sender, "&a&l/friends help")
    msg(sender, "&a1. /friends &oadd <names...>    &6aliases: &o+")
    msg(sender, "&a2. /friends &orem <names...>    &6aliases: &oremove, delete, del, -")
    msg(sender, "&a3. /friends &oclear              &6aliases: &o/")
    msg(sender, "&a4. /friends &olist                 &6aliases: &olst, *")
    msg(sender, "&a5. /friends &ohelp               &6aliases: &o?")

  else:
    friendmessage(sender, "&cInvalid syntax. use &o/friends ? &cfor info.")
  return True