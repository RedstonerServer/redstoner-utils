# can't import * because that's not working with nested functions & decorators
import helpers

# cmd = the actual command
# tree = e.g. [{ "name": "subcommand", "perm": "utils.cmd.command.subcommand", "func": <function>, "type": "cmd", "cont": [<tree>] }]
# helpnoargs = print help if no args given, else run the command function below decorator
# console = can be ran by console
def hypercommand(cmd, tree = [], helpnoargs = False, console = False):
    def help_msg_get(tree):
        holder = ""
        for data in tree:
            if len(data["cont"]) > 0:
                holder += ("(" + help_msg_get(data["cont"]) + ")")
            else:
                holder += (data["name"] if data["type"] == "cmd" else ("<" + data["name"] + ">"))
        return holder

    def help_msg(sender, tree):
        for data in tree:
            if len(data["cont"]) > 0:
                helpers.msg(sender, "&e-&a " + (data["name"] if data["type"] == "cmd" else ("<" + data["name"] + ">")) + " " + help_msg_get(data["cont"]))
            else:
                helpers.msg(sender, "&e-&a " + (data["name"] if data["type"] == "cmd" else ("<" + data["name"] + ">")))
        return None

    has_help = False
    for data in tree:
        if data["name"] == "help" and data["type"] == "cmd":
            has_help = True
            break
    cmd = cmd.lower()
    if not has_help:
        tree.append({"name": "help", "perm": "utils." + cmd + ".help", "func": help_msg, "type": "cmd", "cont": []}) # type = "cmd" for subcommands or "arg" for arguments

    def decorator(function):
        def get_next(sender, tree, args, all_args):
            if len(args) == 0: # ran out of arguments but command is supposed to continue, print usage
                data = []
                for comm in tree:
                    if comm["type"] == "cmd":
                        data.append(comm["name"])
                    else:
                        data.append("<" + comm["name"] + ">")
                return "&c" + " ".join(all_args) + " " + "/".join(data) + "..."
            for comm in tree:
                if comm["type"] == "cmd":
                    if comm["name"] == args[0]: # argument exists as a subcommand
                        if sender.hasPermission(comm["perm"]):
                            if len(comm["cont"]) > 0: # command continues
                                return get_next(sender, comm["cont"], args[1:], all_args) # continue in the recursive stack
                            else:
                                return comm["func"](sender, args[1:]) # run function with sender and all trailing arguments incase they are relevant
                        else:
                            return "&cNo permission"
            for comm in tree:
                if comm["type"] == "arg":
                    if len(comm["cont"]) > 0: # command continues, but this is an argument
                                              # run the function its pointing at and substitute itself with the returned subcommand to chose
                        # continue in stack as if the arg was a subcommand returned by its pointer function
                        return get_next(sender, comm["cont"], args[0:(len(args) - 1)].insert(0, comm["func"](sender, args[0])), all_args)
                    else:
                        return comm["func"](sender, args) # run the function arg is pointing at with current arguments including this one as args[0]
            return get_next(sender, tree, [], all_args[0:(len(all_args) - 1)])

        @hook.command(cmd)
        def call(sender, command, label, args):
            message = run(sender, command, label, args)
            if message:
                helpers.msg(sender, message)
            return True

        def run(sender, command, label, args):
            if not helpers.is_player(sender) and not console:
                return "&cThis command can only be executed by players"
            try:
                if len(args) == 0:
                    if helpnoargs:
                        help_msg(sender, tree)
                        return None
                    else:
                        return function(sender, command, label, args)
                    return get_next(sender, tree, args, args)
            except:
                helpers.error(helpers.trace())
                return "&cInternal Error. Please report to staff!"
        return call
    return decorator