from wrapper import *
from passlib.hash import pbkdf2_sha256 as crypt

@event_handler("player_login","normal", utils = True)
def player_join(*args):
    player = args[1]
    if not player.registered:
        player.authenticated = True
        player.msg("Successfully logged in!")

"""
@event_handler("player.PlayerCommandPreprocessEvent", "lowest")
def on_login_command(event):
    player = event.player
    password = event.message.replace("/login", "").replace(" ", "")
    event.message = event.player.name + " Attempting to login!"
    event.cancelled = True

    @async(daemon = True)
    def check_pass(player, password):
        print password
        if not player.registered:
            player.msg("You are not registered! use /register <password> to register!")
            return
        else:
            if crypt.verify(password, player.password):
                player.authenticated = True
                player.msg("Successfully logged in!")
            else:
                print event.message
                player.msg("Wrong password!")
    check_pass(player, password)"""

@command("login")
@async(daemon = True)
def on_login_command(**kwargs):
    player = kwargs["sender"]
    args = kwargs["args"]

    if not player.registered:
        player.msg("You are not registered! use /register <password> to register!")
        return
    if len(args) > 1:
        player.msg("The syntax is /login <password>")
        return
    elif len(args) is 1:
        if crypt.verify(args[0], player.password):
            player.authenticated = True
            player.msg("Successfully logged in!")
        else:
            player.msg("Wrong password!")

@command("changepass")
@async(daemon = True)
def on_changepass_command(**kwargs):
    player = kwargs["sender"]
    args = kwargs["args"]

    if not player.registered:
        player.msg("You are not registered! use /register <password> to register!")
        return

    if len(args) < 2:
        player.msg("The syntax is /login <current_password> <new_password>")
        return
    elif len(args) is 2:
        if crypt.verify(args[0], player.password):
            player.password = crypt.encrypt(args[1], rounds=200000, salt_size=16)
            player.msg("Successfully changed your password!")
            player.save()
        else:
            player.msg("You have entered an incorrect current password!")

@command("removepass")
@async(daemon = True)
def on_removepass_command(**kwargs):
    player = kwargs["sender"]
    args = kwargs["args"]

    if not player.registered:
        player.msg("You are not registered! use /register <password> to register!")
        return

    if len(args) < 1:
        player.msg("The syntax is /removepass <current_password>")
        return

    elif len(args) is 1:
        if crypt.verify(args[0], player.password):
            player.password = "None"
            player.registered = False
            player.save()
            player.msg("Successfully removed your password!")
        else:
            player.msg("You have entered an incorrect current password!")




@command("register")
@async(daemon = True)
def on_register_command(**kwargs):
    player = kwargs["sender"]
    args = kwargs["args"]
    if len(args) > 1:
        player.msg("The syntax is /register <password>")
        return
    elif len(args) is 1:
        if player.registered:
            player.msg("You are already registered!")
            return 
        player.password = crypt.encrypt(args[0], rounds=200000, salt_size=16)
        player.registered = True
        print player.password
        player.save()
        player.msg("Successfully registered!")


blocked_events = ["block.BlockBreakEvent", "block.BlockPlaceEvent", "player.PlayerMoveEvent",
                    "player.AsyncPlayerChatEvent","player.PlayerTeleportEvent",
                     "player.PlayerInteractEvent"]

for event in blocked_events:
    @event_handler(event_name = event, priority = "highest")
    def on_blocked_event(event):
        if not event.player.authenticated:
            event.cancelled = True


