from helpers import *

add_perm = "utils.tag.add"
del_perm = "utils.tag.del"
check_perm = "utils.tag.check"

data = open_json_file("tag", {})

@hook.command("tag")
def command(sender, command, label, args):
    if len(args) > 0:
        if str(args[0]) == "add":
            if sender.hasPermission(add_perm):
                if len(args) > 2:
                    add(sender, args[1:])
                else:
                    msg(sender, "&a-&c Usage: /tag add <name> <reason>")
            else:
                noperm(sender)
        elif str(args[0]) == "check":
            if sender.hasPermission(check_perm):
                if len(args) == 2:
                    check(sender, args[1:])
                else:
                    msg(sender, "&a-&c Usage: /tag check <name>")
            else:
                noperm(sender)
        elif str(args[0]) == "del":
            if sender.hasPermission(del_perm):
                if len(args) == 3:
                    delete(sender, args[1:])
                else:
                    msg(sender, "&a-&c Usage: /tag del <id>")
        else:
            msg(sender, "&a-&c Unknown subcommand! (add, check, del)")
    else:
        msg(sender, "&a&c Usage: /tag add/check")
    return True

def delete(sender, args):
    player = server.getPlayer(args[0])
    uuid = uid(player)
    try:
        if data[uuid] == None:
            pass
    except:
        msg(sender, "&a-&e There are no notes about this player")
        return
    if int(args[1]) - 1 >= len(data[uuid]):
        msg(sender, "&a-&c Id of note is out of range")
        return
    del (data[uuid])[int(args[1]) - 1]
    save_json_file("tag", data)
    msg(sender, "&a-&e Deleted note at %s" % args[1])

def add(sender, args):
    player = server.getPlayer(args[0])
    uuid = uid(player)
    try:
        if data[uuid] == None:
            pass
    except:
        data[uuid] = []
    data[uuid].append(" ".join(args[1:]))
    msg(sender, "&a-&e Note added")
    save_json_file("tag", data)

def check(sender, args):
    player = server.getPlayer(args[0])
    uuid = uid(player)
    try:
        num = 0
        for tag in data[uuid]:
            num += 1
            msg(sender, "&a-&e %s: %s" % (str(num), str(tag)))
    except:
        msg(sender, "&a-&e There are no notes about this player")

