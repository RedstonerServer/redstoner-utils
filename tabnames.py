import mysqlhack
import org.bukkit as bukkit
import json
from java.util import UUID as UUID
from helpers import *
from org.bukkit import *
from traceback import format_exc as trace
from iptracker_secrets import *

tabnames_version = "v1.0.0"

##############################################################
#                                                            #
# This module automatically puts people in the corresponding #
# scoreboard team so that their name is colored properly and #
# tab will be nicely sorted.                                 #
#                                                            #
##############################################################

ranks = ["visitor", "member", "builder", "trusted", "modintraining", "mod", "admin", "breaker"]
prefixes = {"admin":"a", "mod":"b", "modintraining":"c", "trusted":"d", "builder":"e", "member":"f","visitor":"g"}

@hook.event("player.PlayerJoinEvent", "low")
def on_player_join(event):
    scoreboard_team = prefix(get_Rank(event.getPlayer()))
    bukkit.Bukkit.getServer().dispatchCommand(bukkit.Bukkit.getServer().getConsoleSender(), "scoreboard teams join " + scoreboard_team + " " + event.getPlayer().getName())

def get_Rank(player):
    for i in range(0, len(ranks) - 1):
        if not player.hasPermission("group." + ranks[i]):
            break
    return ranks[i-1]

def prefix(rank):
    return prefixes.get(rank) + "_" + rank
