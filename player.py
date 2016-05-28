from helpers import *

py_players = []

class py_player:
    def __init__(self,player):
        self.player = player
        self.logging_in = False
        self.login_time = 0

def get_py_player(player):
    #py_player = py_players[py_players.index(player)]

    for py_player in py_players:
        if py_player.player.getName() == player.getName():
            return py_player


@hook.event("player.PlayerJoinEvent","lowest")
def on_join(event):
    player = py_player(event.getPlayer())
    py_players.append(player)
    print str(len(py_players))+event.getPlayer().getName()


@hook.event("player.PlayerQuitEvent","highest")
def on_leave(event):
    player = get_py_player(event.getPlayer())
    if player in py_players:
        py_players.remove(player)
