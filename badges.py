from helpers import *

badges            = open_json_file("badges", {})
badges_available  = {
  "helpful"          : "A very helpful player",
  "expert_minecraft" : "An expert in Minecraft",
  "expert_coder"     : "A good coder",
  "oldtimer"         : "A long time player",
  "good_builder"     : "A very good builder",
  "friendly"         : "Many think that this player is friendly",
  "very_active"      : "A very active player",
  "trustworthy"      : "This player is very trustworthy",
}
badges_perm_add   = "utils.badges.add"
badges_perm_del   = "utils.badges.delete"

def save_badges():
  save_json_file("badges", badges)


def get_badges(player):
  sender_id = uid(player)
  if sender_id in badges.keys():
    badges_list = badges[sender_id]
  else:
    badges_list = []
  return badges_list


def show_badges(sender, player):
  player_badges = get_badges(player)
  if player_badges:
    for key in player_badges:
      msg(sender, "&6> %s" % badges_available[key])
  else:
    msg(sender, "&eThis player has no badges yet")


def new_badge_event(player, badge):
  msg(player, "")
  msg(player, "&6Wow! You just received a badge!")
  msg(player, "&b-> &3%s" % badges_available[badge])
  msg(player, "&7Type /badge to see all your badges!")
  msg(player, "")
  player.playSound(player.getLocation(), "random.orb", 1, 1)


def del_badge_event(player, badge):
  msg(player, "&cWe took your badge \"%s\"." % badges_available[badge])


def list_badges(sender):
  if badges_available:
    for key in badges_available.keys():
      msg(sender, "&e> %s = %s" % (key, badges_available[key]))
  else:
    msg(sender, "&cThere are currently no badges available")


def add_badge(sender, target, badge):
  if badge in badges_available:
    player_badges = get_badges(target)
    if badge in player_badges:
      msg(sender, "&cThis player got this badge already!")
      return
    player_badges.append(badge)
    if player_badges:
      badges[uid(target)] = player_badges
      msg(sender, "&aYou just gave %s a new badge!" % target.getName())
      new_badge_event(target, badge)
      save_badges()
  else:
    msg(sender, "&cThere is no badge called %s. Check /badge list!" % badge)


def del_badge(sender, target, badge):
  if badge in badges_available.keys():
    player_badges = get_badges(target)
    if badge in player_badges:
      player_badges.remove(badge)
      msg(sender, "&7... just removed badge from player_badges ...")
      msg(sender, "&7... result: %s" % ", ".join(player_badges))
      badges[uid(target)] = player_badges
      msg(sender, "&7... set player_badges to uid badges target ...")
      msg(sender, "&7... result: %s" % ", ".join(badges[uid(target)]))

      msg(sender, "&aYou just took %s from %s!" % (badge, target.getName()))
      save_badges()
      del_badge_event(target)
      return
    msg(sender, "&c%s doesn't have this badge!" % target.getName())
  else:
    msg(sender, "&cThere is no badge called %s. Check /badge list!" % badge)


@hook.command("badge", aliases=["badges", "rewards"])
def on_badge_command(sender, args):
  argnum = int(len(args))

  # No arguments
  if argnum is 0:
    show_badges(sender, sender)

  # Length of arguments is 1
  if argnum == 1:

    # If only argument is "list"
    if args[0].lower() == "list":
      list_badges(sender)
      return True

    # If only argument is a player name
    target = server.getPlayer(args[0])
    if is_player(target):
      show_badges(sender, target)
      return True
    else:
      msg(sender, "&cThere is no player called %s online." % args[0])
      return True

    msg(sender, "&cUnknown syntax: /badge <playername> &o&c /badge list")
    return True

  # Length of arguments is 3
  if argnum == 3:
    cmd = args[0].lower()
    target = server.getPlayer(args[1])
    new_badge = args[2].lower()

    if cmd == "add":
      if not sender.hasPermission(badges_perm_add):
        noperm(sender)
        return True
      add_badge(sender, target, new_badge)
      return True

    if cmd == "take" or cmd == "del":
      if not sender.hasPermission(badges_perm_del):
        noperm(sender)
        return True
      del_badge(sender, target, new_badge)
      return True

    msg(sender, "&cUnknown syntax: /badge <add|take> <playername> <badge>")
    return True