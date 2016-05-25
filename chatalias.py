############################################
# Alias v2.0 by Pepich                     #
# Changes to previous version from curs3d: #
# Dynamic alias limit from permissions     #
# AC/CG/MSG support                        #
# Color support                            #
# Bugfixes                                 #
#                                          #
#                  TODO:                   #
# Add command support...                   #
############################################

import os
import mysqlhack
import org.bukkit as bukkit
from org.bukkit import *
from helpers import *
from traceback import format_exc as trace
from secrets import *

# Version number and requirements

alias_version = "2.0.0"
helpers_versions = ["1.1.0", "2.0.0"]
enabled = False
error = colorify("&cUnspecified error")
commands_per_page = 5
global_aliases = {"./":"/"}
data = {}
# DON'T SET THIS TO TRUE! MySQL requestst are NOT ASYNC yet! (And for some reason it doesn't want to store any data ._.)
use_mysql = False

# Permissions:

# Grants full access immediately
permission_ALL = "utils.alias.*"
# Access to the command to display the help screen
permission_BASE = "utils.alias"
# Make replacements only when the user has this permission
permission_USE = "utils.alias.use"
# Modify aliases
permission_MODIFY = "utils.alias.modify"
permission_MODIFY_OTHERS = "utils.alias.modify.others"
# List aliases
permission_LIST = "utils.alias.list"
permission_LIST_OTHERS = "utils.alias.list.others"
# Set alias amounts/length limits, e.g. utils.alias.amount.420
permission_AMOUNT = "utils.alias.amount."
permission_LENGTH = "utils.alias.length."
# See when the plugin was disabled due to version errors
permission_INFO = "utils.alias.info"
permission_FINFO = "utils.alias.finfo"

########
# CODE #
########

# OnEnable
enabled = helpers_version in helpers_versions
if not enabled:
    error = colorify("&6Incompatible versions detected (&chelpers.py&6)")


def safe_open_json(uuid):
    if not os.path.exists("plugins/redstoner-utils.py.dir/files/aliases"):
        os.makedirs("plugins/redstoner-utils.py.dir/files/aliases")
    value = open_json_file("aliases/" + uuid)
    if value is None:
        value = global_aliases
    save_json_file("aliases/" + uuid, value)
    return value


@hook.command("alias",
              usage="/<command> <add, remove, list, help> [...]",
              desc="Allows aliasing of words")
def on_alias_command(sender, cmd, label, args):
    try:
        args = array_to_list(args)
        if not enabled:
            disabled_fallback(sender)
            return True
        if not hasPerm(sender, permission_BASE):
            plugin_header(recipient=sender, name="Alias")
            noperm(sender)
            return True
        return subcommands[args[0].lower()](sender, args[1:])
    except:
        return subcommands["help"](sender, "1")


def help(sender, args):
    commands = [colorify("&e/alias help [page]")]
    if hasPerm(sender, permission_LIST):
        commands += [colorify("&e/alias list &7- Lists all your aliases")]
    if hasPerm(sender, permission_MODIFY):
        commands += [colorify("&e/alias add <word> <alias> &7- Add an alias")]
        commands += [colorify("&e/alias remove <word> &7- Remove an alias")]
    if can_remote(sender):
        while len(commands) < commands_per_page:
            commands += [""]
        commands += [colorify("&7Following commands will be executed on <player> yet all output will be redirected to you, except when you set silent to false, then <player> will see it too.")]
    if hasPerm(sender, permission_LIST_OTHERS):
        commands += [colorify("&e/alias player <name> list [silent]")]
    if hasPerm(sender, permission_MODIFY_OTHERS):
        commands += [colorify("&e/alias player <name> add <word> <alias> [silent]")]
        commands += [colorify("&e/alias player <name> remove <word> [silent]")]
    pages = (len(commands)-1)/commands_per_page + 1
    page = 1
    if len(args) != 0:
        page = int(args[0])
    if (page > pages):
        page = pages
    if page < 1:
        page = 1
    msg(sender, colorify("&e---- &6Help &e-- &6Page &c" + str(page) + "&6/&c" + str(pages) + " &e----"))
    page -= 1
    to_display = commands[5*page:5*page+5]
    for message in to_display:
        msg(sender, message)
    if page+1 < pages:
        msg(sender, colorify("&6To display the next page, type &c/alias help " + str(page+2)))
    return True


@hook.event("player.PlayerJoinEvent", "high")
def on_join(event):
    if enabled:
        t = threading.Thread(target=load_data, args=(uid(event.getPlayer()), ))
        t.daemon = True
        t.start()
    else:
        if event.getPlayer().hasPermission(permission_FINFO):
            disabled_fallback(event.getPlayer())


@hook.event("player.AsyncPlayerChatEvent", "high")
def on_player_chat(event):
    try:
        if enabled:
            if event.isCancelled():
                return
            if not hasPerm(event.getPlayer(), permission_USE):
                return
            for alias, value in data[str(uid(event.getPlayer()))].items():
                if not event.getPlayer().hasPermission(permission_ALL) and len(event.getMessage()) > int(get_permission_content(event.getPlayer(), permission_LENGTH)):
                    event.setCanceled(True)
                    plugin_header(event.getPlayer, "Alias")
                    msg(event.getPlayer(), "The message you wanted to generate would exceed your limit. Please make it shorter!")
                    return
                if event.getPlayer().hasPermission("essentials.chat.color"):
                    event.setMessage(event.getMessage().replace(colorify(alias), colorify(value)))
                else:
                    event.setMessage(event.getMessage().replace(alias, value))
    except:
        print(trace())


def hasPerm(player, permission):
    return (player.hasPermission(permission)) or (player.hasPermission(permission_ALL))


def disabled_fallback(receiver):
    if not hasPerm(receiver, permission_INFO):
        msg(receiver, colorify("&cUnknown command. Use &e/help&c, &e/plugins &cor ask a mod."))
    else:
        msg(receiver, colorify("&cPlugin alias v" + alias_version + " has experienced an &eEMERGENCY SHUTDOWN:"))
        msg(receiver, error)
        msg(receiver, colorify("&cPlease contact a dev/admin (especially pep :P) about this to take a look at it."))


def can_remote(player):
    return hasPerm(player, permission_LIST_OTHERS) or hasPerm(player, permission_MODIFY_OTHERS)


def add(sender, args):
    plugin_header(sender, "Alias")
    if not sender.hasPermission(permission_ALL) and len(data[uid(sender)]) >= int(get_permission_content(sender, permission_AMOUNT)):
        msg(sender, "&cCould not create alias: Max_limit reached!")
        return True
    args = [args[0]] + [" ".join(args[1:])]
    data[str(uid(sender))][str(args[0])] = args[1]
    save_data(uid(sender))
    msg(sender, colorify("&7Alias: ") + args[0] + colorify("&7 -> " + args[1] + colorify("&7 was succesfully created!")), usecolor=sender.hasPermission("essentials.chat.color"))
    return True


def radd(sender, args):
    plugin_header(sender, "Alias")
    args = args[0:2] + [" ".join(args[2:len(args)-1])] + [args[len(args)-1]]
    if is_player(sender):
        sender_name = colorify(sender.getDisplayName())
    else:
        sender_name = colorify("&6Console")
    target = get_player(args[0])
    if args[3].lower() == "false":
        plugin_header(target, "Alias")
        msg(target, "&cPlayer " + sender_name + " &cis creating an alias for you!")
    if not sender.hasPermission(permission_ALL) and len(data[uid(sender)]) >= int(get_permission_content(target, permission_AMOUNT)):
        msg(sender, "&cCould not create alias: Max_limit reached!")
        if args[3].lower() == "false":
            msg(target, "&cCould not create alias: Max_limit reached!")
        return True
    if len(args) == 3:
        args += ["true"]
    data[str(uid(target))][str(args[1])] = str(args[2])
    save_data(uid(target))
    msg(sender, colorify("&7Alias: ") + args[1] + colorify("&7 -> " + args[2] + colorify("&7 was succesfully created!")), usecolor=target.hasPermission("essentials.chat.color"))
    if args[3].lower() == "false":
        msg(target, colorify("&7Alias: ") + args[1] + colorify("&7 -> " + args[2] + colorify("&7 was succesfully created!")), usecolor=target.hasPermission("essentials.chat.color"))
    return True


def remove(sender, args):
    plugin_header(sender, "Alias")
    try:
        msg(sender, colorify("&7Successfully removed alias ") + args[0] + colorify(" &7-> ") + data[uid(sender)].pop(args[0]) + colorify("&7!"), usecolor=sender.hasPermission("essentials.chat.color"))
        save_data(uid(sender))
    except:
        msg(sender, colorify("&cCould not remove alias ") + args[0] + colorify(", it does not exist."), usecolor=sender.hasPermission("essentials.chat.color"))
    return True


def rremove(sender, args):
    plugin_header(sender, "Alias")
    target = get_player(args[0])
    if is_player(sender):
        sender_name = colorify(sender.getDisplayName())
    else:
        sender_name = colorify("&6Console")
    if args[2].lower() == "false":
        plugin_header(target, "Alias")
        msg(target, "&cPlayer " + sender_name + " &cis removing an alias for you!")
    try:
        alias = data[uid(target)].pop(args[1])
        msg(sender, colorify("&7Successfully removed alias ") + args[1] + colorify(" &7-> ") + alias + colorify("&7!"), usecolor=sender.hasPermission("essentials.chat.color"))
        if args[2].lower() == "false":
            msg(target, colorify("&7Successfully removed alias ") + args[1] + colorify(" &7-> ") + alias + colorify("&7!"), usecolor=sender.hasPermission("essentials.chat.color"))
        save_data(uid(target))
    except:
        msg(sender, colorify("&cCould not remove alias ") + args[1] + colorify(", it does not exist."), usecolor=sender.hasPermission("essentials.chat.color"))
        if args[2].lower() == "false":
            msg(target, colorify("&cCould not remove alias ") + args[1] + colorify(", it does not exist."), usecolor=sender.hasPermission("essentials.chat.color"))
    return True


def list_alias(sender, args):
    plugin_header(sender, "Alias")
    msg(sender, "&7You have a total of " + str(len(data[uid(sender)])) + " aliases:")
    for word, alias in data[str(uid(sender))].items():
        msg(sender, colorify("&7") + word + colorify("&7 -> ") + alias, usecolor=sender.hasPermission("essentials.chat.color"))
    return True


def rlist_alias(sender, args):
    plugin_header(sender, "Alias")
    target = get_player(args[0])
    if is_player(sender):
        sender_name = colorify(sender.getDisplayName)
    else:
        sender_name = colorify("&6Console")
    if len(args) == 1:
        args += ["true"]
    msg(sender, "Player " + args[0] + " has following aliases (" + str(len(data[uid(target)])) + " in total):")
    if args[1].lower() == "false":
        plugin_header(target, "Alias")
        msg(target, "&cPlayer " + sender_name + " &cis listing your aliases (" + str(len(data[uid(target)])) + " in total):")
    for word, alias in data[str(uid(target))].items():
        msg(sender, colorify("&7") + word + colorify("&7 -> ") + alias, usecolor=target.hasPermission("essentials.chat.color"))
        if args[1].lower() == "false":
            msg(target, colorify("&7") + word + colorify("&7 -> ") + alias, usecolor=target.hasPermission("essentials.chat.color"))
    return True


def remote(sender, args):
    try:
        return remotes[args[1].lower()](sender, [args[0]] + args[2:])
    except:
        return subcommands["help"](sender, ["2"])


def load_data(uuid):
    try:
        load_data_thread(uuid)
#        t = threading.Thread(target=load_data_thread, args=(uuid))
#        t.daemon = True
#        t.start()
    except:
        print(trace())

def load_data_thread(uuid):
    if use_mysql:
        conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
        curs = conn.cursor()
        curs.execute("SELECT alias FROM alias WHERE uuid = ?", (uuid, ))
        results = curs.fetchall()
        if len(results) == 0:
            results = global_aliases
            curs.execute("INSERT INTO alias VALUES (?,?)", (uuid, results, ))
        data[uuid] = results
    else:
        data[uuid] = safe_open_json(uuid)


def save_data(uuid):
    try:
        save_data_thread(uuid)
#        t = threading.Thread(target=save_data_thread, args=(uuid))
#        t.daemon = True
#        t.start()
    except:
        print(trace())

def save_data_thread(uuid):
    if use_mysql:
        conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
        curs = conn.cursor()
        curs.execute("UPDATE alias SET alias = ? WHERE uuid = ?", (data[uuid], uuid, ))
    else:
        save_json_file("aliases/" + uuid, data[uuid])


# Subcommands:
subcommands = {
    "help": help,
    "add": add,
    "remove": remove,
    "player": remote,
    "list": list_alias
}

remotes = {
    "add": radd,
    "remove": rremove,
    "list": rlist_alias,
}
Status API Training Shop Blog About
© 2016 GitHub, Inc. Terms Privacy Security Contact Help