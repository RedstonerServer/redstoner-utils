# Chat Aliasing plugin by Curs3d #
##################################
# Allows users to alias words,
# so that when they send a
# message in chat, it gets
# replaced by their specified
# word. The JSON file for this
# plugin is generated if not
# present. Set values to -1
# for "unlimited" setting.

from helpers import *
import re
from traceback import format_exc as trace

data = None

max_entries = 10
max_alias_length = 35
# Minecraft message limit is 100 so I decided to give a little tolerance (and I added a bit more)
max_overall_length = 100 + max_alias_length

alias_perm = "utils.alias.allowed"
exceed_length = "utils.alias.exceedlimit"
exceed_entries = "utils.alias.exceedlimit"
exceed_overall_length = "utils.alias.exceedlimit"


def safe_open_json():
    global data
    if data is not None:
        return data
    data = open_json_file("aliases")
    if data is None:
        data = {}
    save_json_file("aliases", data)
    return data

def multiple_replace(aliases, text):
    regex = re.compile("|".join(map(re.escape, aliases.keys())))
    return regex.sub(lambda mo: aliases[mo.group(0)], text)


@hook.command("alias",
              usage="/<command> [to_alias] [alias...]",
              desc="Aliases words in chat")
def on_alias_command(sender, cmd, label, args):

    if not is_player(sender):
        msg(sender, "Sorry, non-players cannot alias words")
        return True
    if not sender.hasPermission(alias_perm):
        plugin_header(recipient=sender, name="Chat Alias")
        noperm(sender)
        return True
    if len(args) == 0:
        plugin_header(recipient=sender, name="Chat Alias")
        msg(sender, "&7This is a plugin that allows you to get words" +
            "replaced by other ones automatically!")
        msg(sender, "&7\nCommands:")
        msg(sender, "&e/alias <word> &7removes <word> from your aliases. " +
            "Use &e/alias * &7to remove all aliases.")
        msg(sender, "&e/alias <word> <replacement> &7will change &e<word> " +
            "&7to &e<replacement> &7in chat")
        msg(sender, "&7\nYour Aliases:")
        data = safe_open_json()
        try:
            for alias, value in data[str(sender.getUniqueId())].items():
                msg(sender, "&7%s &7==> %s" % (alias, value))
        except KeyError:
            pass
        return True
    elif len(args) == 1:
        data = safe_open_json()
        if args[0] == "*":
            try:
                del data[str(sender.getUniqueId())]
            except KeyError:
                plugin_header(recipient=sender, name="Chat Alias")
                msg(sender, "&7No alias data to remove!")
                return True
            save_json_file("aliases", data)
            plugin_header(recipient=sender, name="Chat Alias")
            msg(sender, "&cALL &7alias data successfuly removed!")
            return True
        try:
            if data[str(sender.getUniqueId())].pop(args[0], None) is None:
                plugin_header(recipient=sender, name="Chat Alias")
                msg(sender, "&7Could not remove: alias not present!")
                return True
        except KeyError:
            plugin_header(recipient=sender, name="Chat Alias")
            msg(sender, "&7Could not remove: you do not have any aliases!")
            return True
        save_json_file("aliases", data)
        plugin_header(recipient=sender, name="Chat Alias")
        msg(sender, "&7Alias for %s &7successfuly removed" % args[0])
        return True
    elif len(args) >= 2:
        data = safe_open_json()
        alias = " ".join(args[1:])
        try:
            if (len(alias) > max_alias_length) and (max_alias_length >= 0) and (not sender.hasPermission(exceed_length)):
                plugin_header(recipient=sender, name="Chat Alias")
                msg(sender, "&7Please do not alias long words/sentences.")
                return True
            if (len(data[str(sender.getUniqueId())]) >= max_entries) and (max_entries >= 0) and (not sender.hasPermission(exceed_entries)):
                plugin_header(recipient=sender, name="Chat Alias")
                msg(sender, "&7You have reached your alias limit!")
                return True
        except KeyError:
            data[str(sender.getUniqueId())] = {}
        data[str(sender.getUniqueId())][args[0]] = alias
        save_json_file("aliases", data)
        plugin_header(recipient=sender, name="Chat Alias")
        msg(sender, "&7Chat Alias %s &7==> %s &7successfully created!" % (args[0], alias))
        return True
    else:
        return False


@hook.event("player.AsyncPlayerChatEvent", "high")
def on_player_chat(event):
    playerid = str(event.getPlayer().getUniqueId())
    data = safe_open_json()
    if event.isCancelled():
        return
    if not data[playerid]:
        return
    event.setMessage(multiple_replace(data[playerid], event.getMessage()))

    if (event.getPlayer().hasPermission("essentials.chat.color")):
        event.setMessage(colorify(event.getMessage()))
    if (max_overall_length >= 0) and (len(event.getMessage()) > max_overall_length) and (not event.getPlayer().hasPermission(exceed_overall_length)):
        event.setCancelled(True)
        plugin_header(recipient=event.getPlayer(), name="Chat Alias")
        msg(event.getPlayer(), "&7The message generated was too long and was not sent. :/")

