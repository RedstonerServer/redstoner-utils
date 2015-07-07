from helpers import *
from passlib.hash import pbkdf2_sha256 as crypt
from basecommands import simplecommand
import time
import threading
from utils_security import *
import mysqlhack
from com.ziclix.python.sql import zxJDBC




wait_time = 60 #seconds
admin_perm = "utils.loginsecurity.admin"
min_pass_length = 8
blocked_events = ["block.BlockBreakEvent", "block.BlockPlaceEvent", "player.PlayerMoveEvent"]


logging_in = {}


def matches(password, user):
    hashed = get_pass(uid(user))
    return crypt.verify(password, hashed)

@simplecommand("cgpass",
	usage       = "<password> <new password>",
	description = "Changes your password",
	senderLimit = 0,
	helpNoargs  = True)
def change_pass_command(sender, command, label, args):
    if not len(args) == 2:
        return "&cInvalid arguments"
    password = args[0]
    new_password = args[1]
    uuid = uid(sender)
    if is_registered(uuid):
        if matches(password, sender):
            change_pass(uuid, crypt.encrypt(new_password, rounds=200000, salt_size=16))
            return "&aPassword changed"
        return "&cInvalid password!"
    return "&cYou are not registered"

@simplecommand("login",
        usage       = "<password>", 
        description = "Logs you in if <password> matches your password.",
        senderLimit = 0, 
        helpNoargs  = True)
def login_command(sender, command, label, args):
    password = args[0]
    if matches(password, sender):
        del logging_in[sender.getName()]
        return "&aLogged in successfully!"
    return "&cInvalid password"

@simplecommand("register",
        usage       = "<password>",
        description = "Registers you with <password>. Next time you join, log in with /login",
        senderLimit = 0,
        helpNoargs  = True)
def register_command(sender, command, label, args):
    if len(args) > 1:
        return "&cPassword can only be one word!"
    uuid = str(uid(sender))
    ######################### - delete after testing
    """
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("SELECT EXISTS(SELECT * FROM secret WHERE 'uuid' = ?)",(uuid,)) 
    results = curs.fetchall()
    print results[0][0]
    """
    #########################
    if is_registered(uuid):
        return "&cYou are already registered!"
    password = args[0]
    if len(password) < min_pass_length:
        return "&cThe password has to be made up of at least %s characters!" % min_pass_length
    hashed = crypt.encrypt(password, rounds=200000, salt_size=16)
    create_pass(uuid, hashed)
    return "&cPassword set. Use /login <password> upon join."

@simplecommand("rmpass",
        usage       = "<password>",
        description = "Removes your password if the password matches",
        senderLimit = 0,
        helpNoargs  = True)
def rmpass_command(sender, command, label, args):
    if not is_registered(uid(sender)):
        return "&cYou are not registered!"
    password = " ".join(args)
    if matches(password, sender):
        delete_pass(uid(sender))
        return "&aPassword removed successfully. You will not be prompted anymore."
    return "&cInvalid password"

@simplecommand("rmotherpass",
        aliases     = ["lacrmpass"],
        usage       = "<user>",
        description = "Removes password of <user> and sends them a notification",
        helpNoargs  = True)
def rmotherpass_command(sender, command, label, args):
    if not sender.hasPermission(admin_perm):
        noperm(sender)
        return
    user = server.getOfflinePlayer(args[0])
    if is_registered(uid(user)):
        delete_pass(uid(user))
        runas(server.getConsoleSender(), colorify("mail send %s &cYour password was reset by a staff member. Use &6/register&c to set a new one." % sender.getDisplayName()))
        return "&sPassword of %s reset successfully" % user.getName()
    return "&cThat player could not be found (or is not registered)"

def change_pass(uuid, pw):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("UPDATE secret SET 'pass' = ? WHERE 'uuid' = ?", (pw,), (uuid,))

def get_pass(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("SELECT pass FROM secret WHERE 'uuid' = ?", (uuid,))
    results = curs.fetchall()
    curs.close()
    conn.close()
    return results[0][0]

def create_pass(uuid, pw):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("INSERT INTO secret VALUES (?)", (uuid,pw,))
    curs.close()
    conn.close()

def is_registered(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("SELECT EXISTS(SELECT * FROM secret WHERE 'uuid' = ?)", (uuid,))
    results = curs.fetchall()
    curs.close()
    conn.close()
    return results[0][0] == 1

def delete_pass(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("DELETE FROM secret WHERE 'uuid' = ?", (uuid,))
    curs.close()
    conn.close()

@hook.event("player.PlayerJoinEvent", "high")
def on_join(event):
    try:
        thingy(event)
    except:
        print trace()


def thingy(event):
    user = event.getPlayer()
    if is_registered(uid(user)):
        logging_in[user.getName()] = time.time()


@hook.event("player.PlayerQuitEvent", "high")
def on_quit(event):
    del logging_in[event.getPlayer().getName()]

##Threading start
def kick_thread():
    wait_time_millis = wait_time * 1000
    while True:
        time.sleep(1)
        moment = time.time()
        for name, jointime in logging_in.iteritems():
            if moment - jointime > wait_time_millis:
                server.getPlayer(name).kickPlayer(colorify("&cLogin timed out"))


thread = threading.Thread(target = kick_thread)
thread.daemon = True
thread.start()
##Threading end


for blocked_event in blocked_events:
    @hook.event(blocked_event, "high")
    def on_blocked_event(event):
        user = event.getPlayer()
        if user.getName() in logging_in:
            event.setCancelled(True)
            msg(user, "&cYou have to log in first! Use /login <password>")
