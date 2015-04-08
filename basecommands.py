from helpers import *
import inspect, new

current_subs = []
current_main = None

to_see_permission = "utils.showpermission" # See cmd permission in help

def maincommand(function):
    current_main = function
    return function

class subcommand():

    def __init__(self, cmd, 
            aliases      = [], 
            amin         = 0, 
            amax         = -1, 
            description  = None, 
            usage        = "[args...]", 
            senderLimit  = -1,
            helpNoargs   = False,
            helpSubcmd   = False):
        cmd = cmd.lower()
        self.description = description
        self.cmd         = cmd
        self.usage       = usage
        self.aliases     = aliases
        self.amin        = amin
        self.amax        = amax
        self.senderLimit = senderLimit
        self.helpNoargs  = helpNoargs
        self.helpSubcmd  = helpSubcmd
        self.permission  = None
        self.parent      = None
        self.call        = None

    def __call__(self, f):
        def call_sub(sender, command, label, args):
            isPlayer = is_player(sender)
            if not isSenderValid(senderLimit, isPlayer):
                return invalidSenderMsg(isPlayer)
            if not sender.hasPermission(permission):
                return "&cYou do not have permission to use that command"
            if ((not args) and helpNoargs) or (helpSubcmd and args and args[0].lower() == "help"):
                return getHelp(sender)
            if not checkargs(sender, args, amin, amax):
                return None
            return f(sender, command, label, args)

        self.call = call_sub
        current_subs.append(self)
        return call_sub

    def getHelp(sender):
        return helpMsg(sender, "%s %s" % (parent, cmd), description, usage, aliases, permission)

    def setParent(self, parent):
        self.parent      = parent
        self.permission  = "utils.%s.%s" % (parent, self.cmd)
        self.description = self.description if self.description else "Handles /" + parent

    def isCalled(self, subcmd):
        alias = self.cmd
        i = 0
        while i <= len(self.aliases):
            if alias == subcmd:
                return True
            alias = self.aliases[i]
            i += 1
        return False


def command(cmd,
                aliases     = [], 
                usage       = "[args...]", 
                description = None,
                senderLimit = -1, 
                amin        = 0, 
                amax        = -1, 
                helpNoargs  = False, 
                helpSubcmd  = False):

    cmd = cmd.lower()

    subcommands = []
    for subcmd in current_subs:
        subcmd.setParent(cmd)
        subcommands.append(subcmd)
    info(subcommands)
    current_subs = []

    main_function = current_main
    current_main = None
    if main_function == None and len(subcommands) != 0:
        error("No main function found for " + cmd)

    permission = "utils." + cmd
    if not description:
        description = "Handles " + cmd
    if not usage:
        usage = "/%s <subcmd>" % cmd

    def getHelp(sender):
        return helpMsg(sender, cmd, description, usage, aliases, permission)

    def getCalledCmd(cmdName):
        for subcmd in subcommands:
            if subcmd.isCalled(cmdName):
                return subcmd
        return None

    def decorator(function):

        if len(subcommands) == 0:
            main_function = function

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

            if args:
                arg1 = args[0].lower()
                if (not args) and helpNoargs:
                    return getHelp(sender)
                if helpSubcmd and arg1 == "help":
                    if len(args) > 1:
                        sub = getCalledCmd(args[1].lower())
                        return sub.getHelp(sender) if sub and sub.helpSubcmd else "&c%s is not a command!" % args[1]
                    return getHelp(sender)
                sub = getCalledCmd(args[0].lower())
                if sub:
                    return sub.call(sender, command, label, args[1:])
            if not sender.hasPermission(permission):
                return "&cYou do not have permission to use that command"
            if not checkargs(sender, args, amin, amax):
                return None
            return main_function(sender, command, label, args)
        return call
    return decorator




def isSenderValid(senderLimit, isPlayer):
    return True if senderLimit == -1 else senderLimit != isPlayer

def invalidSenderMsg(isPlayer):
        return "&cThat command can only be run from the console" if isPlayer else "&cThat command can only be run by players"

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
            return function(sender, command, label, args)
        return call
    return decorator


"""
def advancedcommand(cmd,
                    aliases = [],
                    description = None,
                    usage = None,
                    senderLimit = -1, 
                    subCommands = []):
    cmd = cmd.lower()

    def isSenderValid(isPlayer):
        return True if senderLimit == -1 else senderLimit != isPlayer

    def getHelp(sender):
        return helpMsg(sender, cmd, description, usage, aliases)

    def getSubCmd(alias):
        called = None
        for sub in subCommands:
            if sub.isCalled(alias):
                called = sub

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
        if not args:
            return getHelp()
        subcmd = args[0].lower()
        if subcmd == "help":
            if len(args) == 2:
                called = getSubCmd(args[1].lower())
                if called:
                    return called.getHelp(sender)
            else:
                return getHelp()
        called = getSubCmd(subcmd)
        if not called:
            return getHelp()
        if not isSenderValid(called.senderLimit, isPlayer):
            return invalidSenderMsg(isPlayer)
        if not sender.hasPermission(called.permission):
            return "&cYou do not have permission to use that command"
        if not checkargs(sender, args[1:], called.amin, called.amax):
            return None
        return called.call(sender, command, label, args)

    def decorator(function):
        #functions = [new.function(c, globals()) for c in function.func_code.co_consts if inspect.iscode(c)]
        functions = function()
        for sub in subCommands:
            sub.setParent(cmd)
            for func in functions:
                if sub.cmd == func.__name__.lower():
                    sub.setCalledFunction(func)
            if not sub.call:
                error("No function found for /%s %s" % (cmd, sub.cmd))
        return call
    return decorator
"""


"""
Use this instead of @hook.command for your command methods. (@simplecommand(things...))

It will take care of the following things:
- Basic permission check. The default permission is utils.<cmd_name>
- Sender type check. You can pass whether the sender must be a player, a consolesender, or both. (see sender_limit below)
- Minimum and maximum args. Works with checkargs from helpers.py.
- A '/<cmd> help' message containing the description, usage and aliases of the command.

Information about some arguments:
- cmd:              The command you type in chat.
- usage:            For example "<player> <other_player" and is part of the help message.
- description:      A brief description of what the command does. (also part of the help message)
- aliases:          A list of aliases for the command
- permission:       The basic permission for the command. Defaults to utils.<cmd>
- sender_limit:     Defines what sendertype can use the command. Leave blank for console & player, 0 for player only, 1 for console only.
- min_args:         The least arguments for the command.
- max_args:         You guessed it right. Defaults to infinity (-1).
- help_noargs:      Whether to send help if no arguments are given
- help_subcmd:      Whether to send help upon '/<cmd> help'

*** DISCLAIMER ***

Your command function must take four arguments: sender, command, label, args and help_msg.
help_msg is a function which can be called like 'return help_msg(sender)' to send them information about the command.

Your function must also not return a boolean like before, but a String instead. The string returned will be sent to the player (&-codes supported).
Use None or "" for no message.

Feel free to edit or give suggestions (but don't break existing commands)

See below for an example command:

@simplecommand("test", usage = "<player>", description = "Kicks a player", aliases = ["kickp", "tek"], permission = "utils.kickuser", sender_limit = 0, min_args = 1, max_args = 2)
def on_test(sender, command, label, args):
    target = server.getPlayer(args[0]);
    if target:
        target.kickPlayer("Kicked from the server")
        return None
    return "&cThat player could not be found"
"""

"""
Example @command:

@command("forcefield")
def forcefield_command():

    @subcommand("add")
    def func(sender, command, label, args):
        ...add to whitelist

    @maincommand
    def other(sender, command, label, args):
        ...Execute command if no sub commands were called

@command("simplestuff")
def simplestuff_command(sender, command, label, args):
    msg(sender, "hi, I do not use subcommands!")
"""
