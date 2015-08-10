from helpers import *
import org.bukkit.entity.Player as Base_player
import blockplacemods as blockmods
import snowbrawl
import loginsecurity as login
import calc
import chatgroups as cg
import adminchat as ac
import cycle
import forcefield as ff
import imout
import mentio
import pmtoggle


get_info_perm = "utils.playermanager.info"

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
            players.remove(players[i])
            return

@hook.event("player.PlayerJoinEvent", "highest")
def on_join(event):
    players.append(Player(event.getPlayer()))

#############################################################
# Commands

def send(sender, name, data):
    if isinstance(data, bool):
        if data == True:
            msg(sender, "&e-&a %s&e:&a True" % name)
        else:
            msg(sender, "&e-&a %s&e:&c False" % name)
    else:
        msg(sender, "&e-&a %s&e:&6 %s" % (name, str(data)))

def send_header(sender, name):
    msg(sender, "&e- &2 %s&e:" % name.upper())

def print_info(sender, player):
    send_header(sender, "general")
    send(sender, "Nickname", player.get_display_name())
    send(sender, "Name", player.get_name())
    send(sender, "UUID", player.get_uuid())
    send(sender, "Logged in", player.logged_in())
    send_header(sender, "snowbrawl")
    send(sender, "In arena", player.in_sb_arena())
    send(sender, "Arena", player.get_sb_arena())
    send_header(sender, "place-mods")
    send(sender, "Slab flip", player.has_autoflip_slab())
    send(sender, "Cauldron fill", player.has_autofill_cauldron())
    send(sender, "Piston face", player.has_autoface_piston())
    send_header(sender, "chat groups")
    send(sender, "In chatgroup", player.in_cg())
    send(sender, "Chatgroup", player.get_cg())
    send(sender, "Key", player.get_cg_key())
    send(sender, "Toggle", player.has_cg_toggle())
    send_header(sender, "Admin chat")
    send(sender, "In adminchat", player.in_ac())
    send(sender, "Key", player.get_ac_key())
    send(sender, "Toggle", player.has_ac_toggle())
    send_header(sender, "forcefield")
    send(sender, "Whitelist", "&e, &6".join(player.get_ff_whitelist()))
    send(sender, "Toggle", player.has_ff_toggle())
    send_header(sender, "miscellaneous")
    send(sender, "Calc", player.has_calc())
    send(sender, "PM toggle", player.has_pm_toggle())
    send(sender, "Cycle toggle", player.has_cycle())
    send(sender, "Imout toggle", player.has_imout_toggle())
    send(sender, "Mentio", "&e, &6".join(player.get_mentio_list()))

@hook.command("getinfo")
def on_command(sender, cmd, label, args):
    if sender.hasPermission(get_info_perm):
        if len(args) != 1:
            msg(sender, "&e-&a /getinfo <name>")
        else:
            player = get_player(args[0])
            if player != None:
                print_info(sender, player)
            else:
                msg(sender, "&e-&c Player not online or does not exist")
    else:
        noperm(sender)
    return True

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

    def has_autoflip_slab(self):
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
        if self.in_cg():
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

    def has_cycle(self):
        return self.get_uuid() not in cycle.no_cyclers

    def has_ff_toggle(self):
        return self.get_uuid() in ff.ff_users

    def get_ff_whitelist(self):
        return ff.whitelists.get(self.get_uuid(), [])

    def has_imout_toggle(self):
        return self.get_name() in imout.imout_toggle_list

    def get_mentio_list(self):
        return mentio.get_keywords(self.get_java_player())

    def has_pm_toggle(self):
        return self.get_uuid() in pmtoggle.toggle_dict
