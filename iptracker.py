import mysqlhack
import org.bukkit as bukkit
import json
from java.util import UUID as UUID
from helpers import *
from org.bukkit import *
from traceback import format_exc as trace
from iptracker_secrets import *


iptrack_permission = "utils.iptrack"


@hook.event("player.PlayerJoinEvent", "low")
def on_player_join(event):
    t = threading.Thread(target=on_player_join_thread, args=(event))
    t.daemon = True
    t.start()

def on_player_join_thread(event):
    player = event.getPlayer()
    ip = player.getAddress().getHostString()
    uuid = uid(player)
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.cursor()
    curs.execute("SELECT ips FROM uuid2ips WHERE uuid = ?", (uuid, ))
    results = curs.fetchall()
    if len(results) == 0:
        ips = []
    else:
        ips = json.loads(results[0][0])
    curs.execute("SELECT uuids FROM ip2uuids WHERE ip = ?", (ip, ))
    results = curs.fetchall()
    if len(results) == 0:
        uuids = []
    else:
        uuids = json.loads(results[0][0])
    new_ip_entry = (len(ips) == 0)
    new_uuid_entry = (len(uuids) == 0)
    if ip not in ips:
        ips.append(ip)
        if new_ip_entry:
            curs.execute("INSERT INTO uuid2ips VALUES (?,?)", (uuid, json.dumps(ips), ))
        else:
            curs.execute("UPDATE uuid2ips SET ips = ? WHERE uuid = ?", (uuid, json.dumps(ips), ))
    if uuid not in uuids:
        uuids.append(uuid)
        if new_uuid_entry:
            curs.execute("INSERT INTO ip2uuids VALUES (?,?)", (ip, json.dumps(uuids), ))
        else:
            curs.execute("UPDATE ip2uuids SET uuids = ? WHERE uuid = ?", (ip, json.dumps(uuids), ))
        conn.commit()
    curs.close()
    conn.close()


@hook.command("getinfo")
def on_getinfo_command(sender, args):
    t = threading.Thread(target=on_player_join_thread, args=(sender, args))
    t.daemon = True
    t.start()

def on_getinfo_command_thread(sender, args):
    if(sender.hasPermission(iptrack_permission)):
        if not checkargs(sender, args, 1, 1):
            return False
        else:
            if isIP(args[0]):
                conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
                curs = conn.cursor()
                curs.execute("SELECT uuids FROM ip2uuids WHERE ip = ?", (args[0], ))
                results = curs.fetchall()
                curs.close()
                conn.close()
                if len(results) == 0:
                    msg(sender, "IP " + args[0] + " is not registered in the database, maybe you got a number wrong?")
                else:
                    uuids = json.loads(results[0][0])
                    msg(sender, "IP " + args[0] + " was seen with " + str(len(uuids)) + " different Accounts:")
                    for i in range(0, len(uuids)):
                        p=Bukkit.getOfflinePlayer(UUID.fromString(uuids[i]))
                        if is_player(sender):
                            send_JSON_message(sender.getName(), '["",{"text":"' + p.getName() + ' - (uuid: ' + uuids[i] + '","color":"gold","clickEvent":{"action":"run_command","value":"/getinfo ' + p.getName() + '"},"hoverEvent":{"action":"show_text","value":{"text":"","extra":[{"text":"To search for ' + p.getName() + ' in the database, simply click the name!","color":"gold"}]}}}]')
                        else:
                            msg(sender,p.getName() + " - (uuid: " + uuids[i] + ")")
            else:
                target = Bukkit.getOfflinePlayer(args[0])
                uuid = target.getUniqueId()
                conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
                curs = conn.cursor()
                curs.execute("SELECT ips FROM uuid2ips WHERE uuid = ?", (uuid.toString(), ))
                results = curs.fetchall()
                curs.close()
                conn.close()
                if len(results) == 0:
                    msg(sender, "Player " + args[0] + " is not registered in the database, maybe you misspelled the name?")
                else:
                    ips = json.loads(results[0][0])
                    msg(sender, "Player " + args[0] + " was seen with " + str(len(ips)) + " different IPs:")
                    for i in range(0, len(ips)):
                        if is_player(sender):
                            send_JSON_message(sender.getName(), '["",{"text":"' + ips[i] + '","color":"gold","clickEvent":{"action":"run_command","value":"/getinfo ' + ips[i] + '"},"hoverEvent":{"action":"show_text","value":{"text":"","extra":[{"text":"To search for the IP ' + ips[i] + ' in the database, simply click the IP!","color":"gold"}]}}}]')
                        else:
                            msg(sender,ips[i])
    else:
        noperm(sender)
    return True
