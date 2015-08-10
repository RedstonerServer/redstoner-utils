from helpers import *
import threading

calc_users = open_json_file("calc", [])
calc_perm = "utils.calc"

def calculate(text):
    pass

def calc(text, sender):
    try:
        result = calculate(text)
        msg(sender, "&2=== Calc:&6 %s" % result)
    except:
        msg(sender, "&2=== Calc:&c Something went wrong while calculating - calulation aborted")

@hook.event("player.AsyncPlayerChatEvent", "monitor")
def on_calc_chat(event):
    sender = event.getPlayer()
    message = event.getMessage()
    if not event.isCancelled() and uid(sender) in calc_users and sender.hasPermission(calc_perm):
        thread = threading.Thread(target=calc, args=(message, sender))
        thread.daemon = True
        thread.start()

@hook.command("calc", description="Toggles chat calculations")
def on_calc_command(sender, command, label, args):
    plugin_header(sender, "Chat Calculator")
    if not sender.hasPermission(calc_perm):
        noperm(sender)
        return True
    if not checkargs(sender, args, 0, 1):
        return True
    if not is_player(sender):
        msg(sender, "&cYou are not a player!")
        return True

    toggle(sender, calc_users, name = "Calc")
    save_json_file("calc", calc_users)

    return True
