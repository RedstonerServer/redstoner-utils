from helpers import *

class commandmanager(object):

    """
    Use this instead of @hook.command for your command methods. (@commandmanager(things...))

    It will take care of the following things:
    - Basic permission check. The default permission is utils.<cmd_name>
    - Sender type check. You can pass whether the sender must be a player, a consolesender, or both. (see sender_limit below)
    - Minimum and maximum args. Works with checkargs from helpers.py.
    - A '/<cmd> help' message containing the description, usage and aliases of the command.

    Information about some arguments:
    - f:                The method. Don't bother with that.
    - cmd_name:         The command you type in chat.
    - usage:            For example "<player> <other_player" and is part of the help message.
    - description:      A brief description of what the command does. (also part of the help message)
    - aliases:          A list of aliases for the command
    - permission:       The basic permission for the command. Defaults to utils.<cmd>
    - sender_limit:     Defines what sendertype can use the command. Leave blank for console & player, 0 for player only, 1 for console only.
    - min_args:         The least arguments for the command.
    - max_args:         You guessed it right. Defaults to infinity (-1).

    *** DISCLAIMER ***

    Your command function must take three arguments: sender, handler, args.
    Where handler is the instance of this class. You can for example return help_message(sender), get the given arguments etc.

    Your function must also not return a boolean like before, but a String instead. The string returned will be sent to the player (&-codes supported).
    Use None or "" for no message.

    Feel free to edit or give suggestions (but don't break existing commands)
    """

    def __init__(self, f, cmd_name, usage = "[args...]", description = "Handles" + cmd_name, aliases = [], permission = "utils." + cmd_name.lower(), sender_limit = -1, min_args = 0, max_args = -1):
        self.f = f
        self.cmd_name = cmd_name.lower()
        self.usage = usage
        self.description = description
        self.aliases = aliases
        self.permission = permission
        self.sender_limit = sender_limit
        self.min_args = min_args
        self.max_args = max_args

    @hook.command(cmd_name, aliases = aliases)
    def __call__(sender, command, label, args):
        msg = __run__(sender, command, label, args)
        if msg:
            msg(sender, msg)

    def __run__(sender, args):
        isplayer = is_player(sender)
        if not is_sender_valid(isplayer):
            return "&cThis command can only be run from the console" if isplayer else "&cThis command can only be run by players"
        if not sender.hasPermission(permission):
            return "&cYou do not have permission to use this command"
        if not checkargs(sender, args, min_args, max_args):
            return None
        return help_message(sender) if args and args[0].lower() == "help" else f(sender, self, args)

    def is_sender_valid(isplayer):
        return True if sender_limit == -1 else sender_limit == 0 == isplayer

    def help_message(sender):
        """
        Information about command /<cmd>:       #Light green
            description...                      #Blue
            description...                      #Blue

        Syntax: /<cmd> <usage>                  #Light green
        Aliases: alias1, alias2, alias3         #Gold
        """
        msg = "&aInformation about command /%s:\n    &9%s" % (cmd_name, description.replace("\n", "\n    "))
        msg += "\n\n&aSyntax: &o/%s %s" % (cmd_name, usage)
        if aliases:
            msg += ("\n&6Aliases: " + [msg + ", " for msg in aliases])[:-2]
        return msg