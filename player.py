from helpers import *

players = []

class py_player:

    def __init__(player):
        self.player = player

    #Properties TODO
    #Example:
    self.logging_in = False

def get_py_player(player):
    py_player = players[players.index(player)]
    return py_player


@hook.event("player.PlayerJoinEvent","highest")
def on_join(event):
    player = py_player(event.getPlayer())
    players.append(player)


@hook.event("player.PlayerQuitEvent","highest")
def on_leave(event):
    players.remove(get_py_player(event.getPlayer()))
