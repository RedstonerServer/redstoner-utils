# Chat Aliasing plugin by Curs3d #
##################################
# Allows users to alias words,
# so that when they send a
# message in chat, it gets
# replaced by their specified
# word. Configuration of this
# plugin is in the "gnl"
# (general) tag of the JSON
# file named "aliases". The
# file is generated if not
# present. Set values to -1
# for unlimited values.

from helpers import *


def safe_open_json():
    data = open_json_file("aliases")
    if data is None:
        data = {"gnl":{"max_len":"35","max_entries":"10"}}
    save_json_file("aliases", data)
    return data


@hook.command("alias", usage = "/<command> [to_alias] [alias...]", desc = "Aliases words in chat")
def on_alias_command(sender, cmd, label, args):
    if not is_player(sender):
       msg(sender, "Sorry, Console cannot alias words")
       return False

    if len(args) == 0:
        plugin_header(recipient = sender, name = "Chat Alias")
        msg(sender, "This is a plugin that allows you to type in chat and have words replaced by other ones automatically!")
        msg(sender, "\nCommands:")
        msg(sender, "/alias <word>: removes <word> from aliased words. Use * to remove all aliased words.")
        msg(sender, "/alias <word> <others...>: Will change <word> to <others...> in chat")
        msg(sender, "\nYour Aliases:")
        data = safe_open_json()
        try:
            for alias, value in data[sender.getName()].items():
                msg(sender, "%s ==> %s" % (alias, value))
        except KeyError:
            pass
        return True

    elif len(args) == 1:
        data = safe_open_json()
        if args[0] == "*":
            data[sender.getName()].clear()
            save_json_file("aliases", data)
            plugin_header(recipient = sender, name = "Chat Alias")
            msg(sender, "ALL alias data successfuly removed!")
            return True
        
        if data[sender.getName()].pop(args[0], None) is None:
            plugin_header(recipient = sender, name = "Chat Alias")
            msg(sender, "Could not remove: alias not present!")
            return True
            
        save_json_file("aliases", data)
        plugin_header(recipient = sender, name = "Chat Alias")
        msg(sender, "Alias for %s successfuly removed" % args[0])
        return True
            
    elif len(args) >= 2:
        data = safe_open_json()
        alias = " ".join(args[1:])
        try:
            if len(alias) > int(data["gnl"]["max_len"]) and data["gnl"]["max_len"] > 0:
                plugin_header(recipient = sender, name = "Chat Alias")
                msg(sender, "Please do not alias long words/sentences.")
                return True
            
            if len(data[sender.getName()]) >= int(data["gnl"]["max_entries"]) and data["gnl"]["max_entries"] > 0:
                plugin_header(recipient = sender, name = "Chat Alias")
                msg(sender, "You have reached the maximum amount of alias entries! Sorry!")
                return True
        except KeyError:
            data[sender.getName()] = {}
        
        data[sender.getName()][args[0]] = alias
        save_json_file("aliases", data)
        plugin_header(recipient = sender, name = "Chat Alias")
        msg(sender, "Chat Alias %s ==> %s successfully created!" % (args[0], alias))
        return True
    
    else:
        return False



@hook.event("player.AsyncPlayerChatEvent", "High")
def on_player_chat(e):
    if e.isCancelled():
        return

    data = safe_open_json()
    for alias, value in data[e.getPlayer().getName()].items():
        e.setMessage(e.getMessage().replace(alias, value))
