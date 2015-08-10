#pylint: disable = F0401
from helpers import *
from basecommands import simplecommand

ac_permission  = "utils.ac"

ac_defaultkey  = ","
ac_keys        = open_json_file("adminchat_keys", {})

ac_toggle_list = []
ac_prefix      = "&8[&cAC&8]"

def adminchat(sender, msg):
    name = "&7{unknown}"
    try:
        name = sender.getDisplayName()
    except AttributeError:
        name = sender.getName()
    broadcast(ac_permission, "%s &9%s&8: &b%s" % (ac_prefix, name, msg))
    # Needs something here like fine(message) to show up in the logs when you use ackey, but fine doesnt work for some reason. It did on the server with /pyeval (not show up on console, but show up in logs nevertheless)


# ac toggle
@hook.command("act")
def on_act_command(sender, args):
    if sender.hasPermission(ac_permission):
        p = sender.getName()
        if p in ac_toggle_list:
            ac_toggle_list.remove(p)
            msg(sender, "%s &aAC toggle: off" % ac_prefix)
        else:
            ac_toggle_list.append(p)
            msg(sender, "%s &aAC toggle: on" % ac_prefix)
    else:
        noperm(sender)
    return True


@hook.command("ac")
def on_ac_command(sender, args):
    if sender.hasPermission(ac_permission):
        if not checkargs(sender, args, 1, -1):
            return True
        adminchat(sender, " ".join(args))
    else:
        noperm(sender)
    return True

def get_key(uuid):
    key = ac_keys.get(uuid)
    return key if key != None else ac_defaultkey

@simplecommand("adminchatkey", 
        aliases = ["ackey"], 
        senderLimit = 0, 
        helpNoargs = True, 
        helpSubcmd = True, 
        description = "Sets a key character for adminchat", 
        usage = "<key>")
def adminchatkey_command(sender, command, label, args):
    key = " ".join(args)
    uuid = uid(sender)
    if key.lower() == "default" or key == ac_defaultkey:
        del ac_keys[uuid]
        save_keys()
        return "&aYour adminchat key was set to the default character: '&c%s&a'" % ac_defaultkey
    ac_keys[uid(sender)] = key
    save_keys()
    return "&aYour adminchat key was set to: '&c%s&a'" % key

def save_keys():
    save_json_file("adminchat_keys", ac_keys)


@hook.event("player.AsyncPlayerChatEvent", "low")
def on_chat(event):
    sender = event.getPlayer()
    msg = event.getMessage()
    if sender.hasPermission(ac_permission) and not event.isCancelled():
        key = get_key(uid(sender))
        if sender.getName() in ac_toggle_list:
            adminchat(sender, msg)
            event.setCancelled(True)
        elif msg[:len(key)] == key:
            adminchat(sender, msg[len(key):])
            event.setCancelled(True)
