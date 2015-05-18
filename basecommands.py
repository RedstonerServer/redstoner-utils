from helpers import *

to_see_permission = "utils.showpermission" # See cmd permission in help


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

            try:
                return function(sender, command, label, args)
            except CommandException, e:
                return e.message
            except Exception, e:
                error(e.message, trace())
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

    
