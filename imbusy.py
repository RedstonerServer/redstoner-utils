# I'M BUSY! Plugin by Curs3d #
##############################
# Concept by CookieManors :D #
# http://bit.ly/1GnNPW8      #
##############################
# This plugin permits users to
# send a command that renders
# them "busy", not letting them
# to get tpa requests or direct
# messages, except from console.
# On restart, all busy data will
# be cleared.

from helpers import *
from basecommands import simplecommand
from traceback import format_exc as trace
busy_players = []


def unclear(sender):
    msg(sender, "Umm, what? Sorry, directions unclear, got head stuck in washing machine")


@hook.command("busy",
    aliases = ["focus"],
    usage = "/<command> <on|off|status>",
    description = "Sets busy mode on, you cannot recieve tpas and MSGs"
    )
def on_busy_command(sender, cmd, label, args):

    if not is_player(sender):
       msg(sender, "Sorry, Console cannot be busy")
       return True

    plugin_header(recipient = sender, name = "I'M BUSY!")

    if not sender.hasPermission("utils.busy.allowed"):
        noperm(sender)
        return True

    if len(args) == 0:
        msg(sender, "This plugin allows being busy, and when turned on you will not receive any direct messages or tpa requests.")
        msg(sender, "\nCommands:")
        msg(sender, "/busy on: turns on busy mode")
        msg(sender, "/busy off: turns off busy mode")
        msg(sender, "/busy status [player]: shows your or [player]'s current busy status.")

    elif len(args) == 1:
        if args[0] == "on":
            if sender.getName() in busy_players:
                msg(sender, "You cannot be even more focused than this without being a jedi!")
            else:
                busy_players.append(sender.getName())
                broadcast(None, "&c[&2Busy&c] &fNow busy: %s&r, don't even TRY bothering them!" % sender.getDisplayName())

        elif args[0] == "off":
            try:
                busy_players.remove(sender.getName())
                msg(sender, "Master has sent /busy command, %s&r is freeee of bothering!" % sender.getDisplayName())
            except ValueError:
                msg(sender, "You are not busy! You cannot be even less busy! Are you perhaps bored?")

        elif args[0] == "status":
            if sender.getName() in busy_players:
                msg(sender, "You are super-duper busy and concentrated right now. Think, think, think!")
            else:
                msg(sender, "You are completely unable to focus right now.")

        else:
            unclear(sender)
            return False

    elif len(args) == 2 and args[0] == "status":
        target = server.getPlayer(args[1])
        if target is None:
            msg(sender, "That player is not online, I doubt they are busy.")
        elif target.getName() in busy_players:
            msg(sender, "Yes, %s&r is busy. Shhh..." % target.getDisplayName())
        else:
            msg(sender, "No, you're good. Feel free to chat with %s&r!" % target.getDisplayName())

    else:
        unclear(sender)
        return False
    return True


@hook.event("player.PlayerCommandPreprocessEvent", "monitor")
def on_cmd_preprocess_event(event):
    message = event.getMessage().split(" ")
    if message[0] == "/msg" or message[0] == "/w" or message[0] == "/m" or \
        message[0] == "/tell" or message[0] == "/tpa" or message[0] == "/tpahere":
        if message[1] in busy_players:
            plugin_header(recipient = event.getPlayer(), name = "I'M BUSY!")
            msg(event.getPlayer(), "We are sorry, but %s is currently busy. Please try again later." % message[1])
            event.setCancelled(True)

@hook.event("player.PlayerQuitEvent", "lowest")
def on_player_leave(event):
    try:
        busy_players.remove(event.getPlayer().getName())
    except:
        pass
