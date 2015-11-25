from wrapper_player import *
from helpers import *

root_commands = Command_dict() # {"command": command_object}

def check_arguments(command, arguments):
    prev_required = True
    type_message_seen = False
    prev_arg = arguments[0] if len(arguments) > 0 else None
    for arg_info in arguments[1:]:

        if not prev_arg.required and arg_info.required:
            raise Argument_exception("Command: %s; There may not be required arguments after non-required arguments" % command)

        if prev_arg.type == Argument.MESSAGE:
            raise Argument_exception("Command: %s; An argument of type MESSAGE may not be followed by other arguments" % command)

        prev_arg = arg_info

#--------------------------------------------------------------------------------------

class Command_dict(dict):
    #{"cmd1" : cmd_object}
    def get_command_object(self, alias):
        for cmd_name, cmd_obj in self.iteritems():
            if alias == cmd_name or alias in cmd_obj.aliases:
                return cmd_obj
        raise KeyError("Subcommand '%s' was not found" % alias)

#--------------------------------------------------------------------------------------

class Command(object):

    def __init__(self, 
                command, 
                aliases = (), 
                arguments = (
                    Argument("target", Argument.string, "the player to teleport to"), 
                    Argument("second target", Argument.string, "the player to teleport", False),
                ), 
                parent = None):

        self.command = command.lower()
        self.arguments = arguments

        check_arguments(self.command, self.arguments)

        prev_required = True
        for arg_info in self.arguments:
            if not prev_required and arg_info.required:
                raise Argument_exception("Command: %s; There may not be required arguments after non-required arguments" % self.command)

        self.aliases = tuple(alias.lower() for alias in aliases)
        self.parent = parent
        self.sub_commands = Command_dict()

        if self.parent == None:
            root_commands[self.command] = self
        else:
            try:
                parent_route = self.parent.split(" ")
                parent_sub_commands = root_commands
                parent_obj = None
                for cmd_name in parent_route:
                    parent_obj = parent_sub_commands.get_command_object(cmd_name)
                    parent_sub_commands = parent_obj.sub_commands
                parent_obj.sub_commands[self.command] = self

            except command_exception, e:
                error("Error occurred while setting up command hierarchy. " + e.message + "\n" + trace())

    def __call__(self, handler):
        self.handler = handler

        if parent == None:
            @hook.command(self.command, self.aliases)
            def run(sender, command, label, args):
                try:
                    message = self.execute(sender, command, label, args)
                except Command_exception as e:
                    message = e.message
                except Exception:
                    error(trace())
                    return True
                if message:
                    sender.sendMessage(message)
                return True

        return handler

    def execute(self, sender, command, label, args):
        try:
            return self.sub_commands.get_command_object(args[0].lower()).execute(sender, command, label, args[1:])
        except (KeyError, IndexError):
            self.execute_checks(sender, command, label, args)

    def execute_checks(self, sender, command, label, args):
        #TODO

        scape = Command_scape(args, self.arguments)
        if is_player(sender):
            sender = py_players[sender]

        return self.handler(sender, self, scape)

    def syntax(self):
        return " ".join(tuple(arg_info.syntax() for arg_info in self.arguments))

#--------------------------------------------------------------------------------------

class Command_scape(list):

    def __init__(self, args, arg_layout):
        super(list, self).__init__()
        self.raw = args
        self.arg_layout = arg_layout

        has_message = False
        for i in range(len(arg_layout)):
            arg_info = arg_layout[i]

            given = (len(args) >= i + 1)
            if arg_info.required and not given:
                raise Argument_exception("You must specify the " + arg_info.name)

            if not given:
                self.append(None)
                continue

            given_arg = args[i]
            arg_type = arg_info.type

            if arg_type == Argument.STRING:
                self.append(given_arg)

            elif arg_type == Argument.INTEGER:
                try:
                    value = int(given_arg)
                except ValueError:
                    raise Argument_exception("The %s has to be a round number" % arg_info.name)
                self.append(value)

            elif arg_type == Argument.FLOAT:
                try:
                    value = float(given_arg)
                except ValueError:
                    raise Argument_exception("The %s has to be a number" % arg_info.name)
                self.append(value)

            elif arg_type == Argument.PLAYER:
                target = server.getPlayer(given_arg)
                if target == None:
                    raise Argument_exception("The %s has to be an online player" % arg_info.name)
                self.append(py_players[target])

            elif arg_type == Argument.OFFLINE_PLAYER:
                try:
                    # Code to get the PY PLAYER by name. Possibly, uid(server.getOfflinePlayer(given_arg)) can be used?
                    pass
                except KeyError:
                    raise Argument_exception("The %s has to be an existing player" % arg_info.name)
                self.append(None)

            elif arg_type == Argument.MESSAGE:
                self.append(" ".join(args[i:]))
                has_message = True
            else:
                error("Argument type not found: %d" % arg_type)
                raise Argument_exception("A weird thing has happened, please contact an administrator")

        if not has_message:
            self.remainder = args[len(arg_layout):]
        else:
            self.remainder = None

    def has_flag(self, flag, check_all = False):
        return (("-" + flag) in self.raw) if check_all else (("-" + flag) in self.remainder)

    def get_raw(self):
        return self.raw

    def get_arg_layout(self):
        return self.arg_layout

#--------------------------------------------------------------------------------------

class Command_exception(Exception):

    def __init__(self, message):
        self.message = message

class Argument_exception(Exception):

    def __init__(self, message):
        self.message = message

#--------------------------------------------------------------------------------------

class Argument():

    STRING = 0
    INTEGER = 1
    FLOAT = 2
    PLAYER = 3
    OFFLINE_PLAYER = 4
    MESSAGE = 5

    def __init__(self, name, type, definition, required = True):
        self.name = name
        self.type = type
        self.definition = definition
        self.required = required

    def syntax(self):
        syntax = self.name
        if self.type == Argument.MESSAGE:
            syntax += "..."
        return (("<%s>" if self.required else "[%s]") % syntax)

#--------------------------------------------------------------------------------------

class Validate():

    @staticmethod
    def is_true(expression, fail_message):
        if not expression:
            raise Command_exception(fail_message)

    @staticmethod
    def not_none(obj, fail_message):
        if obj == None:
            raise Command_exception(fail_message)
