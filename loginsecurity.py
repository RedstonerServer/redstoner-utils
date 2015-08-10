from helpers import *
from passlib.hash import pbkdf2_sha256 as crypt
from basecommands import simplecommand
import time
import threading
from login_secrets import * #Don't forget to make login_secrets aswell
import mysqlhack
from com.ziclix.python.sql import zxJDBC
from java.lang import Runnable

wait_time = 5 #seconds
admin_perm = "utils.loginsecurity.admin"
min_pass_length = 8
blocked_events = ["block.BlockBreakEvent", "block.BlockPlaceEvent", "player.PlayerMoveEvent","player.AsyncPlayerChatEvent"]


logging_in = {}


matches_bool = False

def matches(password,user):
    thread = threading.Thread(target=matches_thread, args = (password,user))
    thread.start()


def matches_thread(password, user):
    hashed = get_pass(uid(user))
    if crypt.verify(password, hashed):
        del logging_in[user.getName()]
        msg(user, "&aLogged in successfully!")
    else:
        msg(user, "&cInvalid password")


@simplecommand("cgpass",
	usage       = "<password> <new password>",
	description = "Changes your password",
	senderLimit = 0,
	helpNoargs  = True)
def change_pass_command(sender, command, label, args):
    if sender.getName() in logging_in:
        return "&cYou are not logged in"
    if not len(args) == 2:
        return "&cInvalid arguments"
    password = args[0]
    new_password = args[1]
    uuid = uid(sender)
    if is_registered(uuid):
        change_pass(uuid, crypt.encrypt(new_password, rounds=200000, salt_size=16))
        return "&aPassword changed"
    return "&cYou are not registered"

@simplecommand("login",
        usage       = "<password>", 
        description = "Logs you in if <password> matches your password.",
        senderLimit = 0, 
        helpNoargs  = True)
def login_command(sender, command, label, args):
    password = args[0]
    matches(password, sender)
        #del logging_in[sender.getName()]
        #return "&aLogged in successfully!"
    #return "&cInvalid password"

@simplecommand("register",
        usage       = "<password>",
        description = "Registers you with <password>. Next time you join, log in with /login",
        senderLimit = 0,
        helpNoargs  = True)
def register_command(sender, command, label, args):
    if len(args) > 1:
        return "&cPassword can only be one word!"
    uuid = str(uid(sender))
    if is_registered(uuid):
        return "&cYou are already registered!"
    password = args[0]
    if len(password) < min_pass_length:
        return "&cThe password has to be made up of at least %s characters!" % min_pass_length
    create_pass(uuid, password)
    return "&cPassword set. Use /login <password> upon join."

@simplecommand("rmpass",
        description = "Removes your password if the password matches",
        senderLimit = 0,
        amax = 0,
        helpNoargs  = False)
def rmpass_command(sender, command, label, args):
    if sender.getName() in logging_in:
        return "&cYou are not logged in"
    if not is_registered(uid(sender)):
        return "&cYou are not registered!"
    if not sender.getName() in logging_in:
        delete_pass(uid(sender))
        return "&aPassword removed successfully. You will not be prompted anymore."
    return "&cFailed to remove password, please contact a staff member"

@simplecommand("rmotherpass",
        aliases     = ["lacrmpass"],
        usage       = "<user>",
        description = "Removes password of <user> and sends them a notification",
        helpNoargs  = True)
def rmotherpass_command(sender, command, label, args):
    if sender.getName() in logging_in:
        return "&cYou are not logged in"
    if not sender.hasPermission(admin_perm):
        noperm(sender)
        return
    user = server.getOfflinePlayer(args[0])
    if is_registered(uid(user)):
        delete_pass(uid(user))
        runas(server.getConsoleSender(), colorify("mail send %s &cYour password was reset by a staff member. Use &6/register&c to set a new one." % user.getName()))
        return "&aPassword of %s reset successfully" % user.getName()
    return "&cThat player could not be found (or is not registered)"

def change_pass(uuid, pw):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("UPDATE secret SET pass = ? WHERE uuid = ?", (pw,uuid,))
    conn.commit()
    curs.close()
    conn.close()

def get_pass(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("SELECT pass FROM secret WHERE uuid = ?", (uuid,))
    results = curs.fetchall()
    curs.close()
    conn.close()
    return results[0][0]

def create_pass(uuid,pw):
    thread = threading.Thread(target=create_pass_thread, args=(uuid,pw))
    thread.start()

def create_pass_thread(uuid, pw):
    pw = crypt.encrypt(pw, rounds=200000, salt_size=16)
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("INSERT INTO secret VALUES (?,?)", (uuid,pw,))
    conn.commit()
    curs.close()
    conn.close()

def is_registered(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("SELECT EXISTS(SELECT * FROM secret WHERE uuid = ?)", (uuid,))
    results = curs.fetchall()
    curs.close()
    conn.close()
    if results[0][0] == 1:
        return True
    return False

def delete_pass(uuid):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("DELETE FROM secret WHERE uuid = ?", (uuid,))
    conn.commit()
    curs.close()
    conn.close()

@hook.event("player.PlayerJoinEvent", "high")
def on_join(event):
    user = event.getPlayer()
    if is_registered(uid(user)):
        msg(event.getPlayer(), "&6You will be disconnected after 60 seconds if you don't &alogin")
        msg(user, "&cUse /login <password>")
        logging_in[user.getName()] = time.time()


@hook.event("player.PlayerQuitEvent", "high")
def on_quit(event):
    if event.getPlayer().getName() in logging_in:
        del logging_in[event.getPlayer().getName()]

##Threading start
class kick_class(Runnable):

    def __init__(self, player):
        self.player = player

    def run(self):
        if self.player.isOnline():
            self.player.kickPlayer(colorify("&aLogin timed out"))

def kick_thread():
    while True:
        time.sleep(1)
        now = time.time()
        for name, jointime in logging_in.iteritems():
            if now - jointime > wait_time:
                player = server.getPlayer(name)
                kick = kick_class(player)
                server.getScheduler().runTask(server.getPluginManager().getPlugin("RedstonerUtils"), kick)
                if name in logging_in:
                    del logging_in[name]
                    break
                


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
