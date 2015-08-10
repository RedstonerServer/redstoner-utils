from helpers import *
import org.bukkit.entity.Player as Base_player
import blockplacemods as blockmods
import snowbrawl
import loginsecurity as login
import calc
import chatgroups as cg
import adminchat as ac

players = []

###############################################################
# Outside-accessible functions

def get_player(name):
    for player in players:
        if player.get_name() == name:
            return player
    return None

##############################################################
# Events

@hook.event("player.PlayerQuitEvent", "highest")
def on_quit(event):
    for i in range(len(players)):
        if players[i].get_uuid() == uid(event.getPlayer()):
            players.remove(i)
            return

@hook.event("player.PlayerJoinEvent", "highest")
def on_join(event):
    players.append(Player(event.getPlayer()))

#############################################################
# Player class

class Player():

    def __init__(self, player):
        self.player = player

    def get_java_player(self):
        return self.player

    def get_uuid(self):
        return uid(self.player)

    def get_name(self):
        return self.get_java_player().getName()

    def get_display_name(self):
        return self.get_java_player().getDisplayName()

    def in_sb_arena(self):
        for arena in snowbrawl.arenas:
            if arena.in_players(self.get_java_player()):
                return True
        return False

    def get_sb_arena(self):
        for arena in snowbrawl.arenas:
            if arena.in_players(self.get_java_player()):
                return arena
        return None

    def logged_in(self):
        return self.get_name() not in login.logging_in

    def has_autoflip_slab_on(self):
        return blockmods.isEnabled("slab", self.get_uuid())

    def has_autofill_cauldron(self):
        return blockmods.isEnabled("cauldron", self.get_uuid())

    def has_autoface_piston(self):
        return blockmods.isEnabled("piston", self.get_uuid())

    def has_calc(self):
        return self.get_uuid() in calc.calc_users

    def in_cg(self):
        return self.get_uuid() in cg.groups.keys()

    def get_cg(self):
        if self.in_cg:
            return cg.groups[self.get_uuid()]
        else:
            return None

    def get_cg_key(self):
        return cg.get_key(self.get_uuid())

    def has_cg_toggle(self):
        return self.get_uuid() in cg.cg_toggle_list

    def in_ac(self):
        return self.get_java_player().hasPermission(ac.ac_permission)

    def get_ac_key(self):
        return ac.get_key(self.get_uuid())

    def has_ac_toggle(self):
        return self.get_name() in ac.ac_toggle_list


