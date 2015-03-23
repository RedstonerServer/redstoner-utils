from helpers import *
from secrets import *
import mysqlhack
from com.ziclix.python.sql import zxJDBC

ranks = {
    "member"      : 3,
    "builder"     : 7,
    "trusted"     : 8,
    "helper"      : 9,
    "trainingmod" : 10,
    "mod"         : 4,
    "admin"       : 5
}


@hook.event("player.PlayerJoinEvent", "normal")
def on_player_join(event):
    user = event.getPlayer()
    uuid = uid(player)
    role = get_role(uuid)
    if role in [1, 2, 6]: #Disabled/Banned/Superadmin
        return
    if role != None:
        for rank in ranks:
            if user.hasPermission("group." + rank):
                set_role(uuid, ranks[rank])
        return
    if not user.hasPlayedBefore():
        return
    if role == None:
        msg(user, "&cYou haven't registed yet! Make sure to do so on redstoner.com")
    elif not is_email_confirmed(uuid):
        msg(user, "&cWe noticed that you haven't confirmed your website email! Don't forget to do so!")



def get_role(uuid):
    return execute_query("SELECT `role_id` FROM users WHERE `uuid` = ? LIMIT 1")[0][17]


def set_role(uuid, role_id):
    execute_query("UPDATE users SET `role_id` = %d WHERE `uuid` = ?" % role_id)


def is_email_confirmed(uuid):
    return execute_query("SELECT `confirmed` FROM users WHERE `uuid` = ? LIMIT 1")[0][15]


def execute_query(query, uuid):
    conn    = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs    = conn.cursor()
    uuid    = uid(player).replace("-", "")
    curs.execute(query, (uuid,))
    results = curs.fetchall()
    curs.close()
    conn.close()
    return results



