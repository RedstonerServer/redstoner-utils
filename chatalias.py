# TODO: Add cg/ac/msg support

import os
import mysqlhack
import org.bukkit as bukkit
from org.bukkit import *
from helpers import *


# Version number and requirements

alias_version = "2.1.0"
helpers_versions = ["1.1.0", "2.0.0"]
enabled = False
error_msg = colorify("&cUnspecified error")
commands_per_page = 5
global_aliases = {"./":"/"}
data = {}
use_mysql = True

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
default_alias_limit = 15
permission_LENGTH = "utils.alias.length."
default_length_limit = 120
# See when the plugin was disabled due to version errors
permission_INFO = "utils.alias.info"
permission_FINFO = "utils.alias.finfo"


def safe_open_json(uuid):
    if not os.path.exists("plugins/redstoner-utils.py.dir/files/aliases"):
        os.makedirs("plugins/redstoner-utils.py.dir/files/aliases")
    value = open_json_file("aliases/" + uuid)
    if value is None:
        value = dict(global_aliases)
        save_json_file("aliases/" + uuid, value)
    return value


def get_player_alias_limit(player):
    value = get_permission_content(player, permission_AMOUNT)
    if value is not None and value.isdigit():
        return int(value)
    return default_alias_limit


def get_player_length_limit(player):
    value = get_permission_content(player, permission_LENGTH)
    if value is not None and value.isdigit():
        return int(value)
    return default_length_limit


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
    if enabled:
        if event.isCancelled():
            return
        player = event.getPlayer() 
        if not hasPerm(player, permission_USE):
            return
        msg_limit = get_player_length_limit(player)
        for alias, value in data[uid(player)].iteritems():
            if player.hasPermission("essentials.chat.color"):
                event.setMessage(event.getMessage().replace(colorify(alias), colorify(value)))
            else:
                event.setMessage(event.getMessage().replace(alias, value))
            if not player.hasPermission(permission_ALL) and len(event.getMessage()) > msg_limit:
                event.setCancelled(True)
                plugin_header(player, "Chatalias")
                msg(player, "The message you wanted to generate would exceed the length limit limit of %d. Please make it shorter!" % msg_limit)
                return


def hasPerm(player, permission):
    return (player.hasPermission(permission)) or (player.hasPermission(permission_ALL))


def disabled_fallback(receiver):
    if not hasPerm(receiver, permission_INFO):
        msg(receiver, colorify("&cUnknown command. Use &e/help&c, &e/plugins &cor ask a mod."))
    else:
        msg(receiver, colorify("&cPlugin alias v" + alias_version + " has experienced an &eEMERGENCY SHUTDOWN:"))
        msg(receiver, error_msg)
        msg(receiver, colorify("&cPlease contact a dev/admin (especially pep :P) about this to take a look at it."))


def can_remote(player):
    return hasPerm(player, permission_LIST_OTHERS) or hasPerm(player, permission_MODIFY_OTHERS)


# Command

@hook.command("alias",
              usage="/<command> <add, remove, list, help> [...]",
              desc="Allows aliasing of words")
def on_alias_command(sender, cmd, label, args):
    plugin_header(sender, "Chatalias")
    try:
        args = array_to_list(args)
        if not enabled:
            disabled_fallback(sender)
            return
        if not hasPerm(sender, permission_BASE):
            noperm(sender)
            return
        if args[0].lower() != "player" and not is_player(sender):
            msg(sender, "&cThe console cannot have aliases")
            return True
        subcommands[args[0].lower()](sender, args[1:])
    except:
        subcommands["help"](sender, "1")
    return True


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


def add(sender, args):
    uuid = uid(sender)
    args = [args[0]] + [" ".join(args[1:])]
    if (args[0] not in data[uuid]) and is_alias_limit_reached(sender, sender):
        return
    if not add_alias_data(uuid, args[0], args[1]):
        msg(sender, colorify("&c") + "Could not add this alias because it would cause some sequences to be replaced multiple times", usecolor = False)
        return
    msg(sender, colorify("&7Alias: ") + args[0] + colorify("&7 -> ") + args[1] + colorify("&7 was succesfully created!"), usecolor=sender.hasPermission("essentials.chat.color"))


def radd(sender, sender_name, target, args, silent):
    if len(args) < 2:
        msg(sender, "&cYou must pass a sequence and an alias for it")
        return
    replaced = args[0]
    alias = " ".join(args[1:])
    uuid = uid(target)
    if not silent:
        if sender is not target:
            plugin_header(target, "Chatalias")
        msg(target, "&cPlayer %s &cis creating an alias for you!" % sender_name)
    if (replaced not in data[uuid]) and is_alias_limit_reached(target, sender, silent):
        return
    if not add_alias_data(uuid, replaced, alias):
        message = colorify("&c") + "Could not add this alias because it would cause some sequences to be replaced multiple times"
        msg(sender, message, usecolor = False)
        if not silent:
            msg(target, message, usecolor = False)
        return
    message = colorify("&7Alias: &7%s&7 -> &7%s&7 was successfully created!") % ((colorify(replaced), colorify(alias)) if target.hasPermission("essentials.chat.color") else (replaced, alias))
    msg(sender, message, usecolor = False)
    if not silent:
        msg(target, message, usecolor = False)


def is_alias_limit_reached(player, recipient, silent = True):
    if player.hasPermission(permission_ALL):
        return False
    alias_limit = get_player_alias_limit(player)
    if len(data[uid(player)]) >= alias_limit:
        message = ("&cYour limit of %d has been reached" if player is recipient else "&cThe limit of %d has been reached for that player") % alias_limit
        msg(recipient, message)
        if not silent:
            msg(player, message)
        return True
    return False


def add_alias_data(puuid, aliased, new_alias):
    prior = dict(data[puuid])
    if aliased in prior:
        info("Checking prior, removing previous alias for " + aliased)
        del prior[aliased]

    # prevent 2 -> 3 if there is 1 -> 2
    for alias in prior.values():
        if aliased in alias:
            info("aliased %s in alias %s" % (aliased, alias))
            return False

    # prevent 1 -> 2 if there is 2 -> 3
    for sequence in prior:
        if sequence in new_alias:
            info("sequence %s in new_alias %s" % (sequence, new_alias))
            return False

    data[puuid][aliased] = new_alias
    save_data(puuid)
    return True


def remove(sender, args):
    try:
        msg(sender, colorify("&7Successfully removed alias ") + args[0] + colorify(" &7-> ") + data[uid(sender)].pop(args[0]) + colorify("&7!"), usecolor=sender.hasPermission("essentials.chat.color"))
        save_data(uid(sender))
    except:
        msg(sender, colorify("&cCould not remove alias ") + args[0] + colorify(", it does not exist."), usecolor=sender.hasPermission("essentials.chat.color"))


def rremove(sender, sender_name, target, args, silent):
    if len(args) < 1:
        msg(sender, "&cYou must specify a sequence whose alias is to be removed")
        return
    removed = args[0]
    uuid = uid(target)
    aliases = data[uuid]
    if not silent:
        msg(target, "&cPlayer %s &cis removing an alias for you!" % sender_name)
    if removed in aliases:
        alias = aliases.pop(removed)
        message = colorify("&7Alias: &7%s&7 -> &7%s&7 successfully removed!") % ((colorify(removed), colorify(alias)) if target.hasPermission("essentials.chat.color") else (removed, alias))
        msg(sender, message, usecolor = False)
        if not silent:
            msg(target, message, usecolor = False)
        save_data(uuid)
    else:
        message = colorify("&cCould not remove alias &7%s&c, it does not exist") % colorify(removed) if target.hasPermission("essentials.chat.color") else removed
        msg(sender, message, usecolor = False)
        if not silent:
            msg(target, message, usecolor = False)


def list_alias(sender, args):
    msg(sender, "&7You have a total of " + str(len(data[uid(sender)])) + " aliases:")
    for word, alias in data[str(uid(sender))].items():
        msg(sender, colorify("&7") + word + colorify("&7 -> ") + alias, usecolor=sender.hasPermission("essentials.chat.color"))


def rlist_alias(sender, sender_name, target, args, silent):
    aliases = data[uid(target)]
    msg(sender, "&7Player %s has a total of %d aliases:" % (target.getName(), len(aliases)))
    if not silent:
        if sender is not target:
            plugin_header(target, "Chatalias")
        msg(target, "&cPlayer %s &cis listing your aliases" % sender_name)
    if target.hasPermission("essentials.chat.color"):
        for pair in aliases.iteritems():
            msg(sender, colorify("&7%s&7 -> %s" % pair), usecolor = False)
    else:
        for pair in aliases.iteritems():
            msg(sender, colorify("&7%s&7 -> %s") % pair, usecolor = False)


def remote(sender, args):
    if len(args) < 2:
        msg(sender, "&cAlias remotes take at least 3 arguments")
        return
    target_remote = remotes.get(args[1].lower())
    if target_remote is None:
        msg(sender, "&cThat remote command does not exist")
        return
    target = server.getOfflinePlayer(args[0])
    if target is None or not (target.hasPlayedBefore() or target.isOnline()):
        msg(sender, "&cThat player could not be found")
        return
    silent = True
    if len(args) > (2 if target_remote is rlist_alias else 3 if target_remote is rremove else 4):
        if args[-1].lower() == "false":
            silent = sender is target or not target.isOnline()
            args = args[:-1]
        elif args[-1].lower() == "true":
            args = args[:-1]
    target_remote(sender, sender.getDisplayName() if is_player(sender) else colorify("&6Console"), target, args[2:], silent)


subcommands = {
    "help": help,
    "?": help,
    "add": add,
    "remove": remove,
    "del": remove,
    "delete": remove,
    "player": remote,
    "remote": remote,
    "list": list_alias
}

remotes = {
    "add": radd,
    "remove": rremove,
    "del": rremove,
    "delete": rremove,
    "list": rlist_alias,
}


# Storage
# MySQL Table:
# CREATE TABLE `chatalias` (`uuid` VARCHAR(36) PRIMARY KEY, `alias` TEXT);

def load_data(uuid):
    if use_mysql:
        try:
            t = threading.Thread(target=load_data_thread, args=(uuid,))
            t.daemon = True
            t.start()
        except:
            error(trace())
    else:
        data[uuid] = safe_open_json(uuid)

def load_data_thread(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("SELECT `alias` FROM `chatalias` WHERE `uuid` = ?;", (uuid, ))
    results = curs.fetchall()
    curs.close()
    conn.close()
    if len(results) == 0:
        value = dict(global_aliases)
    else:
        value = json_loads(results[0][0])
    data[uuid] = value


def save_data(uuid):
    if use_mysql:
        try:
            t = threading.Thread(target=save_data_thread, args=(uuid,))
            t.daemon = True
            t.start()
        except:
            error(trace())
    else:
        save_json_file("aliases/" + uuid, data[uuid])

def save_data_thread(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("INSERT INTO `chatalias` (`uuid`, `alias`) VALUES (?, ?) ON DUPLICATE KEY UPDATE `alias` = VALUES(`alias`);", 
        (uuid, json_dumps(data[uuid])))
    conn.commit()
    curs.close()
    conn.close()


# OnModuleLoad

enabled = helpers_version in helpers_versions
if not enabled:
    error_msg = colorify("&6Incompatible versions detected (&chelpers.py&6)")
for player in server.getOnlinePlayers():
    if enabled:
        load_data(uid(player))
    else:
        if player.hasPermission(permission_FINFO):
            disabled_fallback(player)
