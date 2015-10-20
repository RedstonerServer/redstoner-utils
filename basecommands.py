from helpers import *

"""
@simplecommand is a decorator which is meant to replace @hook.command in redstoner-utils, where useful.
It takes care of checks such as whether the sender is a player, whether they have permission,
whether there are enough argumens, and also takes care of a help message.
On top of that, it makes the code shorter and easier to write with features like Validate, and returning a message instead of a boolean value.
@simplecommand has an inbuilt tracing feature, so you won't have to put all your code in a try/except statement anymore.
Make sure to `from basecommands import simplecommand` before using this decorator.

The arguments are as follows:
* cmd: the command, self explanatory (required);

* aliases: A list containing any aliases for the command, like shortcuts;

* usage: a String defining the expected arguments for the command. Example:
    Let's say I have a command /tp <player_to_teleport> <destination_player>. The usage is: "<player_to_teleport> <destination_player>".
    I suggest we use the same format throughout redstoner-utils:
    - Separate arguments by spaces;
    - Use <> if the argument is required, and [] if the argument is optional;
    - Add .. to the argument's identifier (name) if it is for example a message (containing spaces).
      for example in /msg, the usage would be "<player> <msg..>"

* description: a description of what the command does. Defaults to "Handles cmd".
    This is used for the help message, where the description is (meant to be) indented. To keep this indentation 
    with longer descriptions, call the help message (with the command, ingame) and add '\n' 
    when it jumps to a new line in the chat. The decorator will take care of the indentation after that.

* senderLimit: an integer resembling the accepted sender type. Defaults to -1. Use:
    -1 for console as well as players;
    0 for players only;
    1 for console only.

* amin: an integer resembling the minimum amount of arguments. Defaults to 0

* amax: an integer resembling the maximum amount of arguments. Defaults to -1, which means that there is no maximum.

* helpNoargs: a boolean value resembling whether the help message should be displayed when no arguments are given.
    Defaults to False.

* helpSubcmd: a boolean value resembling whether the help message should be displayed when the first argument.lower() equals "help".
    Defaults to False.

Comments on the function added to the decorator:
It should return a message to send to the player. Color codes are translated automatically. It can return None or an empty string to send nothing.

Inside the function, calls to static methods in the class Validate can be used to make the code shorter and easier to write (maybe not easier to read).
For example, to make sure that a condition is met, use Validate.isTrue(condition, message to send to the player if the condition is not met)
Don't forget to `from basecommands import Validate` if you wish to make use of this.
For all other Validate checks, see the code below. Feel free to add your own.

Instead of returning a message mid-code to describe an error, you can also use raise CommandException(msg), but it is almost always possible
to replace this return statement with a call to one of the functions in the Validate class. Once again, if you use raise CommandException(msg),
don't forget to `from basecommands import CommandException`.
"""

to_see_permission = "utils.showpermission" # See cmd permission in help

def isSenderValid(senderLimit, isPlayer):
    return True if senderLimit == -1 else senderLimit != isPlayer

def invalidSenderMsg(isPlayer):
        return "&cThat command can only be used by " + ("the console" if isPlayer else "players")

def helpMsg(sender, cmd, description, usage, aliases, permission):
    help_msg  = "&aInformation about command /%s:\n    &9%s" % (cmd, description.replace("\n", "\n    "))
    help_msg += "\n \n&aSyntax: /%s %s" % (cmd, usage)
    if aliases:
        help_msg += ("\n&6Aliases: " + "".join([(alias + ", ") for alias in aliases]))[:-2]
    if sender.hasPermission(to_see_permission):
        help_msg += "\n&6Required permission: " + permission
    return help_msg


def simplecommand(cmd,
                aliases     = [],
                usage       = "[args...]",
                description = None,
                senderLimit = -1,
                amin        = 0,
                amax        = -1,
                helpNoargs  = False,
                helpSubcmd  = False):
    cmd = cmd.lower()
    permission = "utils." + cmd
    if not description:
        description = "Handles " + cmd
    if not usage:
        usage = "/%s <subcmd>" % cmd

    def getHelp(sender):
        return helpMsg(sender, cmd, description, usage, aliases, permission)

    def decorator(function):

        @hook.command(cmd, aliases = aliases)
        def call(sender, command, label, args):
            message = run(sender, command, label, args)
            if message:
                if message == "HELP":
                    message = getHelp(sender)
                msg(sender, message)
            return True

        def run(sender, command, label, args):
            isPlayer = is_player(sender)
            if not isSenderValid(senderLimit, isPlayer):
                return invalidSenderMsg(isPlayer)
            if not sender.hasPermission(permission):
                return "&cYou do not have permission to use that command"
            if ((not args) and helpNoargs) or (helpSubcmd and args and args[0].lower() == "help"):
                return getHelp(sender)
            if not checkargs(sender, args, amin, amax):
                return None

            try:
                return function(sender, command, label, args)
            except CommandException, e:
                return e.message
            except Exception, e:
                error(trace())
                return "&cAn internal error occurred while attempting to perform this command"

        return call
    return decorator


class CommandException(Exception):
    pass


class Validate():
    @staticmethod
    def notNone(obj, msg):
        if obj == None:
            raise CommandException(msg)

    @staticmethod
    def isPlayer(sender):
        if not is_player(sender):
            raise CommandException("&cThat command can only be run by players")

    @staticmethod
    def isConsole(sender):
        if is_player(sender):
            raise CommandException("&cThat command can only be run from the console")

    @staticmethod
    def isAuthorized(sender, permission, msg = "that command"):
        if not sender.hasPermission(permission):
            raise CommandException("&cYou do not have permission to use " + msg)

    @staticmethod
    def isTrue(obj, msg):
        if obj != True:
            raise CommandException(msg)

    @staticmethod
    def checkArgs(sender, args, amin, amax):
        if not checkargs(sender, args, amin, amax):
            raise CommandException("")


