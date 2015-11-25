from wrapper_player import *
from helpers import *

root_commands = Command_dict() # {"command": command_object}

class Command(object):
    """
      # Documentation to come.s
    """

    SENDER_ANY = 0
    SENDER_PLAYER = 1
    SENDER_CONSOLE = 2

    ACTION_IGNORE = 3
    ACTION_SYNTAXERROR = 4
    ACTION_DISPLAYSYNTAX = 5
    ACTION_DISPLAYHELP = 6

    def __init__(self,
                command, 
                aliases = (), 
                permission = None,
                description = "Description",
                type = Command.SENDER_ANY
                no_arg_action = Command.ACTION_IGNORE
                help_request_action = Command.ACTION_IGNORE
                arguments = (), 
                parent = None,
    ):

        self.command = command.lower()
        self.aliases = tuple(alias.lower() for alias in aliases)
        self.permission = self.command if permission == None else permission
        self.description = description
        self.type = type
        self.no_arg_action = no_arg_action
        self.help_request_action = help_request_action
        self.arguments = arguments
        self.parent = parent
        self.sub_commands = Command_dict()

        # ---- Check if argument layout is valid ----
        prev_arg = arguments[0] if len(arguments) > 0 else None
        for arg_info in arguments[1:]:

            if not prev_arg.required and arg_info.required:
                raise Argument_exception("Command: %s; There may not be required arguments after non-required arguments" % command)

            if prev_arg.type == Argument.MESSAGE:
                raise Argument_exception("Command: %s; An argument of type MESSAGE may not be followed by other arguments" % command)

            prev_arg = arg_info

        # ---- Add self to parent sub_commands ----
        if self.parent == None:
            root_commands[self.command] = self
        else:
            try:
                parent_route = self.parent.split(" ")
                parent_sub_commands = root_commands
                parent_obj = None
                for cmd_name in parent_route:
                    parent_obj = parent_sub_commands[cmd_name]
                    parent_sub_commands = parent_obj.sub_commands

                parent_obj.sub_commands[self.command] = self

            except KeyError as e:
                error("Error occurred while setting up command hierarchy: " + e.message + "\n" + trace())

    def __call__(self, handler):
        """
          # To clarify: This function is called when you 'call' an instance of a class.
          # This means, that Command() calls __init__() and Command()() calls __call__().
          # This makes it possible to use class instances for decoration. The decorator is this function.
        """
        self.handler = handler

        if parent == None:
            @hook.command(self.command, self.aliases)
            def run(sender, command, label, args):
                """
                  # This function will take care of prefixing and colouring of messages in the future.
                  # So it's very much WIP.
                """
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
            return self.sub_commands[args[0].lower()].execute(sender, command, label, args[1:])
        except (KeyError, IndexError):
            self.execute_checks(sender, command, label, args)

    def execute_checks(self, sender, command, label, args):

        # ---- Check sender type ----
            Validate.is_true(self.type != Command.SENDER_CONSOLE, "That command can only be used by the console")
        else:
            Validate.is_true(self.type != Command.SENDER_PLAYER, "That command can only be used by players")

        # ---- Check permission ----
        Validate.is_authorized(sender, self.permission)

        # ---- Check if a help message is expected ----
        if len(args) == 0:
            action = self.no_arg_action
        elif args[0].lower() == "help":
            action = self.help_request_action
        else:
            action = Command.ACTION_IGNORE

        if action != Command.ACTION_IGNORE:
            if action == Command.ACTION_SYNTAXERROR:
                return "&cInvalid syntax, please try again."
            if action == Command.ACTION_DISPLAYSYNTAX:
                return self.syntax()
            if action == Command.ACTION_DISPLAYHELP:
                return self.help()

        # ---- Set up passed arguments, prepare for handler call ----
        if is_player(sender):
            sender = py_players[sender]
        scape = Command_scape(args, self.arguments, command, label)
        if is_player(sender):
            sender = py_players[sender]

        return self.handler(sender, self, scape)
        # @Command("hello") def on_hello_command(sender, command, scape/args)

    def syntax(self):
        return " ".join(tuple(arg_info.syntax() for arg_info in self.arguments))

    def help(self):
        syntax = self.syntax()
        return syntax #WIP...

class Argument():

    """
      # A more advanced implementation of amin and amax, though it doesn't do exactly the same.
      # You can now pass a list of Argument objects which define what the argument represents.
      # In the process of doing so, you can set an argument type, one of the ones mentioned below.
      # For example, if Argument.PLAYER is given, the server will be searched for the given player, and
      # they will be passed as the argument, instead of a string representing their name.
      #
      # Feel free to add your own argument types. If you want to make a change to the API to make it different,
      # please don't do so on your own behalf.
    """

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

class Validate():

    """
      # Much like what you often see in Java.
      # Instead of having to check if a condition is met, and if not,
      # sending the player a message and returning true,
      # You can use one of these methods to check the condition, and
      # pass a message if it's not met.
      #
      # For example:
      # > if not sender.hasPermission("utils.smth"):
      #       noperm(sender)
      #       return True
      #
      # Can be replaced with:
      # > Validate.is_authorized(sender, "utils.smth")
      #
    """

    @staticmethod
    def is_true(expression, fail_message):
        if not expression:
            raise Command_exception(fail_message)

    @staticmethod
    def not_none(obj, fail_message):
        if obj == None:
            raise Command_exception(fail_message)

    @staticmethod
    def is_authorized(player, permission, msg = "You do not have permission to use that command"):
        if not player.hasPermission(permission):
            raise Command_exception(msg)

    @staticmethod
    def is_player(sender):
        if not is_player(sender):
            raise Command_exception("That command can only be used by players")

    @staticmethod
    def is_console(sender):
        if is_player(sender):
            raise Command_exception("That command can only be used by the console")

"""
  # ---------- API classes ----------
"""

class Command_dict(dict):
    #{"cmd1" : cmd_object}
    def __getattr__(self, alias):
        for cmd_name, cmd_obj in self.iteritems():
            if alias == cmd_name or alias in cmd_obj.aliases:
                return cmd_obj
        raise KeyError("Subcommand '%s' was not found" % alias)

class Command_exception(Exception):

    def __init__(self, message):
        self.message = message

class Command_scape(list):

    def __init__(self, args, arg_layout, command, label):
        super(list, self).__init__()
        self.raw = args
        self.arg_layout = arg_layout
        self.command = command
        self.label = label

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

class Argument_exception(Exception):

    def __init__(self, message):
        self.message = message

