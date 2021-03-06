from helpers import *

##############################################################
#                                                            #
# This module automatically puts people in the corresponding #
# scoreboard team so that their name is colored properly and #
# tab will be nicely sorted.                                 #
#                                                            #
##############################################################

ranks = ["visitor", "member", "builder", "trusted", "trainingmod", "mod", "admin"]
# prefixes are used for sorting in the tab list
prefixes = {"admin":"a", "mod":"b", "trainingmod":"c", "trusted":"d", "builder":"e", "member":"f","visitor":"g"}

@hook.event("player.PlayerJoinEvent", "low")
def on_player_join(event):
    player = event.getPlayer()
    team = get_team(player)
    if team:
        cmd = "scoreboard teams join %s %s" % (team, player.getName())
        server.dispatchCommand(server.getConsoleSender(), cmd)

def get_rank(player):
    player_rank = None
    for rank in ranks:
        if not player.hasPermission("group.%s" % rank):
            break
        player_rank = rank
    if not player_rank:
        warn("Couldn't find rank for player %s" % player.getName())
    return player_rank

def get_team(player):
    rank = get_rank(player)
    if rank:
        prefix = prefixes.get(rank)
        return "_".join([prefix, rank])