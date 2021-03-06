from helpers import *
from basecommands import simplecommand
from basecommands import Validate

vanished = []


def is_authorized(player):
    return player.hasPermission("utils.vanish")


def is_vanished(player):
    return uid(player) in vanished


#this can be used to silently set the vanished state of a player
def set_state(player, state):
    if state == is_vanished(player):
        return

    if state:
        enable_vanish(player)
    else:
        disable_vanish(player)


def enable_vanish(target):
    vanished.append(uid(target))
    for player in list(server.getOnlinePlayers()):
        if not is_authorized(player):
            player.hidePlayer(target)


def disable_vanish(target):
    vanished.remove(uid(target))
    for player in list(server.getOnlinePlayers()):
        player.showPlayer(target)


@simplecommand("vanish", 
        aliases = ["v"],
        usage = "[on/off]",
        description = "Toggles vanish mode, hiding you and your online status \nfrom other players.",
        senderLimit = 0,
        amin = 0,
        amax = 1,
        helpNoargs = False,
        helpSubcmd = True
)
def vanish_command(sender, command, label, args):
    try:
        current_state = is_vanished(sender)
        new_state = not current_state

        if len(args) == 1:
            arg = args[0].lower()
            if arg == "on":
                new_state = True
            elif arg == "off":
                new_state = False

        if current_state == new_state:
            return "&cYou were %s vanished!" % ("already" if current_state else "not yet")

        set_state(sender, new_state)
        return "&a%s vanish mode!" % ("Enabled" if new_state else "Disabled")
    except:
        error(trace())


@hook.event("player.PlayerJoinEvent")
def on_player_join(event):
    player = event.getPlayer()

    if not is_authorized(player):
        for uuid in vanished:
            player.hidePlayer(retrieve_player(uuid))

    elif is_vanished(player):
        msg(player, "&cKeep in mind that you are still vanished! Use /vanish to disable.")


@hook.event("player.PlayerQuitEvent")
def on_player_quit(event):
    player = event.getPlayer()

    if not is_authorized(player):
        for uuid in vanished:
            player.showPlayer(retrieve_player(uuid))


@simplecommand("vanishother",
        usage = "{player} [on/off]",
        description = "Toggles vanish mode for someone, hiding them and their online status from other players.",
        amin = 1,
        amax = 2,
        helpNoargs = True,
        helpSubcmd = True)
def vanishother_command(sender, command, label, args):
    target = server.getPlayer(args[0])
    Validate.notNone(target, "&cThe specified player is not online")

    current_state = is_vanished(target)
    new_state     = not current_state

    if len(args) == 2:
        arg = args[1].lower()
        if arg == "on":
            new_state = True
        elif arg == "off":
            new_state = False

    if current_state == new_state:
        return "&cThat player was already vanished!" if current_state else "&cThat player was not yet vanished!"

    set_state(target, new_state)

    enabled_str = "enabled" if new_state else "disabled"
    if target != sender:
        msg(target, "&aVanish mode %s by %s" % (enabled_str, sender.getDisplayName() if is_player(sender) else "&9CONSOLE"))
    return "&aVanish mode %s%s" % (enabled_str, " for " + target.getDisplayName() if target != sender else "")
