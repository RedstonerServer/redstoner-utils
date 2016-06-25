"""
This plugin permits users to   
send a command that renders    
them "busy", not letting them  
to get tpa requests or direct 
messages, except from console. 
On restart, all busy data will 
be cleared.                    
"""

from helpers import *
from friends import is_friend_of
import org.bukkit.command.Command as Command
from time import time as now

imbusy_version = "v1.1.0"

base_permission = "utils.imbusy" # for /busy status
use_permission = "utils.imbusy.use" # for being busy
override_permission = "utils.imbusy.override" # for being able to bother busy people

busy_status_change_timeout = 15 # seconds

busy_players = {} # name : (status, timeout_expire)
# possible statuses: True if SUPER busy, False if normal busy, None if not busy


@hook.command("imbusy",
    aliases = ["busy"],
    usage = "/<command> [on, off, status/check]",
    description = "Offers control over your busy status"
    )
@debug
def on_busy_command(sender, cmd, label, args):
    if not is_player(sender):
        msg(sender, "&7Sorry, Console cannot be busy")
        return True

    plugin_header(recipient = sender, name = "I'M BUSY!")

    if not sender.hasPermission(base_permission):
        noperm(sender)
        return True

    if len(args) == 0:
        return toggle(sender)

    arg0 = args[0].lower()
    if arg0 == "on":
        return on(sender)
    if arg0 == "off":
        return off(sender)
    if arg0 in ("status", "check"):
        return status(sender, args[1:])
    if arg0 == "super":
        return super_cmd(sender)
    return help(sender)


def change_status(target, status):
    target_name = target.getName()
    old_status = None
    if target_name in busy_players:
        value = busy_players[target_name]
        time_left = value[1] - now()
        if time_left > 0:
            msg(target, "&cYou must wait %.2fs untill you can change your status" % time_left)
            return
        old_status = value[0]

    if old_status is status:
        if status is True:
            msg(target, "&cYou are already SUPER busy")
        elif status is False:
            msg(target, "&cYou are already busy")
        else:
            msg(target, "&cYou weren't busy yet")
        return

    busy_players[target_name] = (status, now() + busy_status_change_timeout)
    if status is True:
        broadcast(None, target.getDisplayName() + " &7is now SUPER busy")
    elif status is False:
        broadcast(None, target.getDisplayName() + " &7is now busy")
    else:
        broadcast(None, target.getDisplayName() + " &7is not busy anymore")


def get_status(target):
    return busy_players.get(target.getName(), (None,))[0]


def toggle(sender):
    if not sender.hasPermission(use_permission):
        noperm(sender)
        return True
    if get_status(sender) is None:
        change_status(sender, False)
    else:
        change_status(sender, None)
    return True


def help(sender):
    msg(sender, "Let's you put yourself in busy status, preventing pms and tpa requests from other players")
    msg(sender, "\n&eCommands:")
    msg(sender, "&e/busy &7- Toggles busy status")
    msg(sender, "&e/busy on &7- Turns on busy status")
    msg(sender, "&e/busy off &7- Turns off busy status")
    msg(sender, "&e/busy status [player] &7- shows your or [player]'s current busy status")
    msg(sender, "&e/busy super &7- sets your status to SUPER busy such that even friends can not bother you")
    return True


def on(sender):
    if not sender.hasPermission(use_permission):
        noperm(sender)
        return True
    change_status(sender, False)
    return True


def off(sender):
    if not sender.hasPermission(use_permission):
        noperm(sender)
        return True
    change_status(sender, None)
    return True


def status(sender, args):
    if not sender.hasPermission(base_permission):
        noperm(sender)
        return True
    if len(args) == 0:
        target = sender
    else:
        target = server.getPlayer(args[0])
        if target is None:
            msg(sender, "&cThat player is not online")
            return True
    status = get_status(target)
    if status is True:
        status_str = "SUPER busy"
    elif status is False:
        status_str = "busy"
    else:
        status_str = "not busy"
    msg(sender, "&7%s currently %s" % ("You are" if target is sender else "Player %s&7 is" % target.getDisplayName()), status_str)
    return True


def super_cmd(sender):
    if not sender.hasPermission(use_permission):
        noperm(sender)
        return True
    change_status(sender, True)
    return True


@hook.event("player.PlayerQuitEvent", "lowest")
def on_player_leave(event):
    player_name = event.getPlayer().getName()
    if player_name in busy_players:
        del busy_players[player_name]


# Block any bothering if should be. If a busy player msgs someone else, they can be replied to and /msg'd as well.
# It's not entirely perfect in that regard as the ability to reply is lost when you are /msg'd by someone else. 

reply_targets = {} # name : (reply_target_name, true if initiated by target)


def can_send(sender, target):
    if target is sender or sender.hasPermission(override_permission):
        return True
    status = get_status(target)
    if status is None:
        return True
    return status is False and is_friend_of(target, sender)


def whisper(sender, target_name):
    target = server.getPlayer(target_name)

    if target is not None:
        sender_name = sender.getName()
        if not can_send(sender, target):
            value = reply_targets[sender_name]
            if value[0] != target_name or value[1] is False:
                msg(sender, "&c[&fBUSY&c] %s&r is busy!" % target.getDisplayName())
                return False

        reply_targets[sender_name] = (target_name, False)
        reply_targets[target_name] = (sender_name, True)
    return True


def reply(sender):
    sender_name = sender.getName()
    if sender_name in reply_targets:
        value = reply_targets[sender_name]
        target = server.getPlayer(value[0])
        if target is not None: 
            if not value[1] and not can_send(sender, target):
                msg(sender, "&c[&fBUSY&c] %s&r is busy!" % target.getDisplayName())
                return False

            reply_targets[target.getName()] = (sender_name, True)
    return True

try:

    def msg_interception(sender, args):
        return not is_player(sender) or len(args) <= 1 or whisper(sender, args[0])

    def reply_interception(sender, args):
        return not is_player(sender) or len(args) == 0 or reply(sender)

    def tpa_interception(sender, args):
        if len(args) == 0 or not is_player(sender):
            return True
        target = server.getPlayer(args[0])
        if target is not None and not can_send(sender, target):
            msg(sender, "&c[&fBUSY&c] %s&r is busy!" % target.getDisplayName())
            return False
        return True

    def tpahere_interception(sender, args):
        return tpa_command_checker(sender, args)

    def mail_interception(sender, args):
        if len(args) < 3 or args[0].lower() != "send" or not is_player(sender):
            return True
        target = server.getPlayer(args[1])
        if target is not None and not can_send(sender, target):
            msg(sender, "&c[&fBUSY&c] %s&r is busy!" % target.getDisplayName())
            return False
        return True

    register = shared["modules"]["misc"].CommandInterceptions.register
    register("essentials", "msg", msg_interception)
    register("minecraft", "tell", msg_interception)
    register("essentials", "reply", reply_interception)
    register("essentials", "tpa", tpa_interception)
    register("essentials", "tpahere", tpahere_interception)
    register("essentials", "mail", mail_interception)

except:
    error("[Imbusy] Failed to intercept commands:")
    error(trace())
