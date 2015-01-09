import json
import urllib2
import datetime
import mysqlhack #pylint: disable = unused-import
from traceback import format_exc as print_traceback
from com.ziclix.python.sql import zxJDBC
from secrets import *
from helpers import *


# receive info based on the user's IP. information provided by ipinfo.io
def ip_info(player):
    if player.isOnline():
        return json.load(urllib2.urlopen("http://ipinfo.io%s/json" % str(player.getAddress().getAddress())))
    else:
      return {}


# receive first join date based on the player data (may not be accurate)
def get_first_join(player):
    first_join = int(player.getFirstPlayed())
    dt = datetime.datetime.fromtimestamp(first_join/1000.0)
    return dt.strftime("%Y-%m-%d %H:%M")


# receive last seen date based on the player data
def get_last_seen(player):
    last_seen = int(player.getLastPlayed())
    dt = datetime.datetime.fromtimestamp(last_seen/1000.0)
    return dt.strftime("%Y-%m-%d %H:%M")


# receive link and email from website
def get_website_data(player):
    conn    = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs    = conn.cursor()
    try:
        uuid = str(uid(player)).replace("-", "")
    except:
        print"failed to convert to string"
    try:
        curs.execute("SELECT DISTINCT `id`, `email` FROM users WHERE `uuid` = (?) LIMIT 1", (uuid,))
    except:
        print"Failed to curs.execute"
    results = curs.fetchall()
    curs.close()
    conn.close()
    if len(results) > 0:
    	try:
            return {
                "link": "http://redstoner.com/users/%s" % results[0],
                "email": results[1]
            }
        except:
            print "failed returning!"
    else:
        return {}


# receive country based on the user's IP
def get_country(data):
    return str(data.get("country"))


def get_all_names(player):
    uuid = str(uid(player)).replace("-", "")
    names = json.load(urllib2.urlopen("https://api.mojang.com/user/profiles/%s/names" % uuid))
    # [ {"name": "some_name"}, {"name": "other_name"} ]
    return ", ".join([name["name"] for name in names])


# combines data
def get_all_data(sender, player):
    data = ip_info(player)

    msg(sender, "")

    try:
        msg(sender, "&7   -- Data provided by Redstoner")
        msg(sender, "&6>  UUID: &e%s" % str(uid(player)))
        msg(sender, "&6>  First joined: &7(y-m-d h:m:s) &e%s" % get_first_join(player))
        msg(sender, "&6>  Last seen: &7(y-m-d h:m:s) &e%s" % get_last_seen(player))
        website = get_website_data(player)
        msg(sender, "&6>  Website account: &e%s" % website.get("link"))
        msg(sender, "&6>    email: &e%s" % website.get("email"))
        msg(sender, "&7   -- Data provided by ipinfo.io")
        msg(sender, "&6>  Country: &e%s" % get_country(data))
        msg(sender, "&7   -- Data provided by Mojang")
        msg(sender, "&6>  All ingame names used so far: &e%s" % get_all_names(player))
    except:
        # can throw exceptions such as timeouts when Mojang API is down
        warn(print_traceback())
        msg(sender, "&cSorry, something went wrong while fetching data")


@hook.command("check", description="Displays useful stuff about a user", usage="/check <player>")
def on_hook_command(sender, args):
    if sender.hasPermission("utils.check"):
        if not checkargs(sender, args, 1, 1):
            return True
        plugin_header(sender, "Check")
        msg(sender, "&7Please notice that the data may not be fully accurate!")
        player = server.getOfflinePlayer(args[0]) if len(args) > 0 else None
        get_all_data(sender, player)
    else:
        msg(sender, "&4You don't have the required permissions to execute this command!")
    return True