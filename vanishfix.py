from helpers import *
from java.lang import Runnable

class run(Runnable):

    def run(self):
        players = server.getOnlinePlayers()
        for player in players:
            if player.hasPermission("essentials.vanish"):
                player.performCommand("vanish")
                player.performCommand("vanish")

def enabled():
    server.getScheduler().runTaskTimer(server.getPluginManager().getPlugin("RedstonerUtils"), run(), 20, 1200)
