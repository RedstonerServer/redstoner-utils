from helpers import *

"""
Use this instead of @hook.command for your command methods.

It will take care of the following things:
- Basic permission check. The default permission is utils.<cmd_name>
- Sender type check. You can pass whether the sender must be a player, a consolesender, or both. (see sender_limit below)
- Minimum and maximum args. Works with checkargs from helpers.py.
- A '/<cmd> help' message containing the description, usage and aliases of the command.

Information about some arguments:
- cmd_name:         The command you type in chat.
- usage:            For example "<player> <other_player" and is part of the help message.
- description:      A brief description of what the command does. (also part of the help message)
- aliases:          A list of aliases for the command
- permission:       The basic permission for the command. Defaults to utils.<cmd>
- sender_limit:     Defines what sendertype can use the command. Leave blank for console & player, 0 for player only, 1 for console only.
- min_args:         The least arguments for the command.
- max_args:         You guessed it right. Defaults to infinity (-1).


-----------------------------------------------------------------------------
*** DISCLAIMER ***

Your command function must take four arguments: sender, command, label, args.

Your function must also not return a boolean like before, but a String instead. The string returned will be sent to the player (&-codes supported).
Use None or "" for no message.

Feel free to edit or give suggestions (but don't break existing commands)

------------------------------------------------------------------------------

See below for an example command:

@simplecommand("test", usage = "<player>", description = "Kicks a player", aliases = ["kickp", "tek"], permission = "utils.kickuser", sender_limit = 0, min_args = 1, max_args = 2)
def on_test(sender, command, label, args):
    target = server.getPlayer(args[0]);
    if target:
        target.kickPlayer("Kicked from the server")
        return None
    return "&cThat player could not be found"
"""

def simplecommand(cmd_name, aliases = [], permission = None, usage = None, description = None, sender_limit = -1, min_args = 0, max_args = -1):
    cmd_name = cmd_name.lower()
    if not permission:
        permission = "utils." + cmd_name
    if not usage:
        usage = "[args...]"
    if not description:
        description = "Handles " + cmd_name

    # ---------------------------------------------------------------------
    # A decorator should always be called with no arguments, and it'll pass the function. The simplecommand() function simply returns this decorator.
    # the function returned by the decorator will be called when calling the function which @simplecommand was added to. The @hook.command will thus call the same.

    def decorator(function):

        @hook.command(cmd_name, aliases = aliases)
        def call(sender, command, label, args):
            message = run_cmd(sender, command, label, args)
            if message:
                msg(sender, message)

        def run_cmd(sender, command, label, args):
            isplayer = is_player(sender)
            if not is_sender_valid(isplayer):
                return "&cThis command can only be run from the console" if isplayer else "&cThis command can only be run by players"
            if not sender.hasPermission(permission):
                return "&cYou do not have permission to use this command"
            if not checkargs(sender, args, min_args, max_args):
                return None
            return help_message(sender) if args and args[0].lower() == "help" else function(sender, command, label, args)

        return call

    # ------------------------------------------------------------------------

    def is_sender_valid(isplayer):
        return True if sender_limit == -1 else sender_limit != isplayer

    def help_message(sender):
        """
        Information about command /<cmd>:       #Light green
            description...                      #Blue
            description...                      #Blue

        Syntax: /<cmd> <usage>                  #Light green
        Aliases: alias1, alias2, alias3         #Gold
        """
        help_msg  = "&aInformation about command /%s:\n    &9%s" % (cmd_name, description.replace("\n", "\n    "))
        help_msg += "\n\n&aSyntax: &o/%s %s" % (cmd_name, usage)
        if aliases:
            help_msg += ("\n&6Aliases: " + "".join([(alias + ", ") for alias in aliases]))[:-2]
        return help_msg

    return decorator