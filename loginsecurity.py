from helpers import *
from basecommands import simplecommand
import bcrypt
from time import time as now
import thread


wait_time       = 60 #seconds
admin_perm      = "utils.loginsecurity.admin"
min_pass_length = 6

run_kick_thread = True
blocked_events  = ["block.BlockBreakEvent", "block.BlockPlaceEvent", "player.PlayerMoveEvent"]
passwords       = open_json_file("loginpasswords", {})

#if passwords == None: (set default value to None  ^^)
#    Keep everyone from playing? (Insecure)

withholdings    = {} #pname : jointime


def save_passwords():
    save_json_file("loginpasswords", passwords)


def matches(password, user):
    hashed = passwords.get(uid(user))
    return bcrypt.hashpw(password, hashed) == hashed


@simplecommand("login",
        usage       = "<password>", 
        description = "Logs you in if <password> matches your password.",
        senderLimit = 0, 
        helpNoargs  = True)
def login_command(sender, command, label, args):
    password = " ".join(args)
    if matches(password, sender):
        del withholdings[sender.getName()]
        return "&aLogged in successfully!"
    return "&cInvalid password"


@simplecommand("register",
        usage       = "<password>",
        description = "Registers you with <password>. Next time you join, log in with /login",
        senderLimit = 0,
        helpNoArgs  = True)
def register_command(sender, command, label, args):
    uuid = uid(sender)
    if uuid in passwords:
        return "&cYou are already registered!"
    password = " ".join(args)
    if len(password) < min_pass_length:
        return "&cThe password has to be made up of at least 8 characters!"
    hashed = bcrypt.hashpw(password, bcrypt.gensalt(16))
    passwords[uuid] = hashed
    return "&cPassword set. Use /login <password> upon join."


@simplecommand("rmpass",
        usage       = "<password>",
        description = "Removes your password if the password matches",
        senderLimit = 0,
        helpNoArgs  = True)
def rmpass_command(sender, command, label, args):
    password = " ".join(args)
    if matches(password, sender):
        del passwords[uuid(sender)]
        return "&aPassword removed successfully. You will not be prompted anymore."
    return "&cInvalid password"


@simplecommand("rmotherpass",
        aliases     = ["lacrmpass"],
        usage       = "<user>",
        description = "Removes password of <user> and sends them a notification",
        helpNoArgs  = True)
def rmotherpass_command(sender, command, label, args):
    user = server.getOfflinePlayer(args[0])
    if user:
        del passwords[uid(user)]
        runas(server.getConsoleSender(), colorify("mail send %s &cYour password was reset by a staff member. Use &o/register&c to set a new one."))
        return "&sPassword of %s reset successfully" % user.getName()
    return "&cThat player could not be found"


@hook.event("player.PlayerJoinEvent", "highest")
def on_join(event):
    user = event.getPlayer()
    if get_id(user) in passwords:
        withholdings[user.getName()] = now()


@hook.event("player.PlayerQuitEvent", "normal")
def on_quit(event):
    del withholdings[event.getPlayer().getName()]


def kick_thread():
    wait_time_millis = wait_time * 1000
    while True:
        if not run_kick_thread:
            info("Exiting LoginSecurity kicking thread!")
            thread.exit()
        time.sleep(1)
        moment = now()
        for name, jointime in withholdings.iteritems():
            if moment - jointime > wait_time_millis:
                server.getPlayer(name).kickPlayer(colorify("&cLogin timed out"))


thread.start_new_thread(kick_thread, ())

for blocked_event in blocked_events:
    @hook.event(blocked_event, "low")
    def on_blocked_event(event):
        user = event.getPlayer()
        if user.getName() in withholdings:
            event.setCancelled(True)
            msg(user, "&cYou have to log in first! Use /login <password>")
