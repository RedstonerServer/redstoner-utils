import json
import urllib2
import datetime

from helpers import *

# receive info based on the user's IP. information provided by ipinfo.io
def ip_info(player):
  data = json.load(urllib2.urlopen("http://ipinfo.io%s/json" % str(player.getAddress().getAddress())))
  return data

# receive first join date based on the player data (may not be accurate)
def get_first_join(player):
  first_join = int(player.getFirstPlayed())
  dt = datetime.datetime.fromtimestamp(first_join/1000.0)
  return "%s-%s-%s %s:%s:%s" % (str(dt.year), str(dt.month), str(dt.day), str(dt.hour), str(dt.minute), str(dt.second))

# receive country based on the user's IP
def get_country(data):
  return str(data.get("country"))

def get_all_names(player):
  uuid = str(player.getUniqueId()).replace("-", "")
  names = json.load(urllib2.urlopen("https://api.mojang.com/user/profiles/%s/names" % uuid))
  return ", ".join(names)

# combines data
def get_all_data(sender, player):
  data = ip_info(player)

  msg(sender, "")

  try:
    msg(sender, "&7   -- Data provided by Redstoner")
    msg(sender, "&6>  Unique User ID: &e%s" % str(player.getUniqueId()))
    msg(sender, "&6>  First joined: &7(y-m-d h:m:s) &e%s" % get_first_join(player))
    msg(sender, "")
    msg(sender, "&7   -- Data provided by Mojang")
    msg(sender, "&6>  Country: &e%s" % get_country(data))
    msg(sender, "&6>  All ingame names used so far: &e%s" % get_all_names(player))
  except Exception as e:
    # can throw exceptions such as timeouts sometimes
    warn(e)



@hook.command("check", description="Displays useful stuff about a user", aliases="ck", usage="/check <player>")
def on_hook_command(sender, args):
  if sender.hasPermission("utils.check"):
    plugin_header(sender, "Check")
    msg(sender, "&7Please notice that the data may not be fully accurate!")

    player = server.getPlayer(args[0]) if len(args) > 0 else None
    if player is not None and is_player(player):
      get_all_data(sender, player)
    else:
      msg(sender, "&cLooks like this player is not online.")
  else:
    msg(sender, "&4You don't have the required permissions to execute this command!")
  return True