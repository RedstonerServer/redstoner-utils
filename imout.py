import thread
from helpers import *
from adminchat import *

imout_toggle_list = []

@hook.command("imout")
def on_imout_command(sender, args):
    if sender.hasPermission("utils.imout"):
        name = sender.getName()
        symbol = "&a&l+"
        if name in imout_toggle_list:
            msg(sender, "&eWelcome back! You are no longer hidden")
            msg(sender, "&6We disabled /act for you!")
            if name in imout_toggle_list:
                imout_toggle_list.remove(name)
            if name in ac_toggle_list:
                ac_toggle_list.remove(name)
        else:
            symbol = "&c&l-"
            msg(sender, "&eYou just left... Or didn't you?")
            imout_toggle_list.append(name)
            if name not in ac_toggle_list:
                msg(sender, "&6We enabled /act for you!")
                ac_toggle_list.append(name)

        broadcast(None, "%s &7%s" % (symbol, name))
