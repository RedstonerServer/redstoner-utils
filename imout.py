import thread
from helpers import *

imout_toggle_list = []

@hook.command("imout")
def on_imout_command(sender, args):
  if sender.hasPermission("utils.imout"):
    name = sender.getName()
    symbol = "&a+"
    if name in imout_toggle_list:
      msg(sender, "&eWelcome back! You are no longer hidden")
      imout_toggle_list.remove(name)
    else:
      symbol = "&c-"
      msg(sender, "&eYou just left... Or didn't you?")
      imout_toggle_list.append(name)

    broadcast(None, "&l%s &7%s" % (symbol, name))
