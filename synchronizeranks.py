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
    uuid = uid(player).replace("-", "")
    role = get_role(uuid)
    if role in [1, 2, 6]: #Disabled/Banned/Superadmin
        return
    if role:
        for rank in ranks:
            if user.hasPermission("group." + rank):
                if role != ranks[rank]:
                    set_role(uuid, ranks[rank])
        return
    if user.hasPlayedBefore() and role == None:
        msg(user, "&cYou haven't registed yet! Make sure to do so on redstoner.com")


def get_role(uuid):
    results = execute_query("SELECT `role_id` FROM users WHERE `uuid` = ? LIMIT 1", uuid)
    return results[0][0]
    # Returns a table with 1 row (LIMIT 1) and 1 column (SELECT `role_id`), so we're looking for the first row of the first column.


def set_role(uuid, role_id):
    execute_update(("UPDATE users SET `role_id` = %d WHERE `uuid` = ?" % role_id), uuid)
    # %d is like %s for integers (unlogically, you'd expect something like %i), though %s also works here.


def execute_query(query, uuid):
    conn    = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs    = conn.cursor()
    curs.execute(query, (uuid,))
    results = curs.fetchall()
    curs.close()
    conn.close()
    return results


def execute_update(update, uuid):
    conn    = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs    = conn.cursor()
    curs.execute(update, (uuid,))
    curs.close()
    conn.close()