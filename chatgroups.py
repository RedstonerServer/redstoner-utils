#pylint: disable = F0401
from helpers import *
from basecommands import simplecommand
from java.util.UUID import fromString as juuid
from traceback import format_exc as trace

groups         = open_json_file("chatgroups", {})
cg_defaultkey  = ":"
cg_keys        = open_json_file("chatgroup_keys", {})
cg_toggle_list = []

def get_key(uuid):
    key = cg_keys.get(uuid)
    return key if key != None else cg_defaultkey


@hook.command("chatgroup")
def on_chatgroup_command(sender, command, label, args):
    plugin_header(sender, "ChatGroups")
    sender_id = uid(sender)
    if len(args) == 1 and args[0] == "leave":
        if sender_id in groups.keys():
            groupchat(sender, "left the group", True)
            group = groups[sender_id]
            del(groups[sender_id])
            save_groups()
        else:
            msg(sender, "&aYou can't leave no group, derp!")
    elif len(args) == 1 and args[0] == "info":
        if sender_id in groups.keys():
            group = groups[sender_id]
            msg(sender, "&aCurrent chatgroup: %s" % group)
            users = [user.getDisplayName() for user in [server.getPlayer(juuid(uuid)) for uuid, ugroup in groups.iteritems() if ugroup == group] if user]
            msg(sender, "&aUsers in this group:")
            msg(sender,  "&a%s" % ", ".join(users))
        else:
            msg(sender, "&aYou're in no chatgroup.")
    elif len(args) == 2 and args[0] == "join":
        groups[sender_id] = args[1]
        groupchat(sender, "joined the group", True)
        save_groups()
        msg(sender, "&aYour chatgroup is set to '%s'" % args[1])
        msg(sender, "&aUse chat like '&e%s<message>' to send messages to this group." % get_key(sender_id))
    elif len(args) == 1 and args[0] == "key":
        msg(sender, "&aYour chatgroup key is currently: '&c%s&a'" % get_key(sender_id))
    else:
        msg(sender, "&e/chatgroup join <name>")
        msg(sender, "&e/chatgroup leave")
        msg(sender, "&e/chatgroup info")
        msg(sender, "&e/chatgroup key")


@hook.command("cgt")
def on_cgt_command(sender, command, label, args):
    p = uid(sender)
    if p in cg_toggle_list:
        cg_toggle_list.remove(p)
        msg(sender, "&8[&bCG&8] &e&oCG toggle: off")
    else:
        cg_toggle_list.append(p)
        msg(sender, "&8[&bCG&8] &e&oCG toggle: on")
    return True


def groupchat(sender, message, ann = False):
    group = groups.get(uid(sender))
    if group == None:
        msg(sender, "&cYou are not in a group!")
        return
    name = sender.getDisplayName()
    if ann:
        mesg = "&8[&bCG&8] &e&o%s&e&o %s" % (name, message)
    else:
        mesg = "&8[&bCG&8] &f%s&f: &6%s" % (name, message)
    info("[ChatGroups] %s (%s): %s" % (sender.getDisplayName(), group, message))
    for receiver in server.getOnlinePlayers():
        groups.get(uid(receiver)) == group and msg(receiver, mesg)



def save_groups():
    save_json_file("chatgroups", groups)


@hook.event("player.AsyncPlayerChatEvent", "normal")
def on_chat(event):
    sender = event.getPlayer()
    msge = event.getMessage()
    if not event.isCancelled():
        sender_id = uid(sender)
        key = get_key(sender_id)
        keylen = len(key)
        if msge[:keylen] == key and sender_id in groups.keys():
            groupchat(sender, msge[keylen:])
            event.setCancelled(True)
        elif sender_id in cg_toggle_list:
            groupchat(sender, msge)
            event.setCancelled(True)

@simplecommand("chatgroupkey", 
        aliases = ["cgkey"], 
        senderLimit = 0, 
        helpNoargs = True, 
        helpSubcmd = True, 
        description = "Sets a key character for chatting to your chatgroup", 
        usage = "<key>")
def chatgroupkey_command(sender, command, label, args):
    key = " ".join(args)
    uuid = uid(sender)
    if key.lower() == "default" or key == cg_defaultkey:
        del cg_keys[uuid]
        save_keys()
        return "&aYour chatgroup key was set to the default character: '&c%s&a'" % cg_defaultkey
    cg_keys[uid(sender)] = key
    save_keys()
    return "&aYour chatgroup key was set to: '&c%s&a'" % key

def save_keys():
    save_json_file("chatgroup_keys", cg_keys)
