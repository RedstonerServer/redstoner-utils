from helpers import *
from secrets import *
import mysqlhack
from com.ziclix.python.sql import zxJDBC

"""
WORK IN PROGRESS
"""

#-----------------------Config--------------------------

config_file = "website-roles"

ranks = {
    "member"      : 3,
    "builder"     : 7,
    "trusted"     : 8,
    "helper"      : 9,
    "trainingmod" : 10,
    "mod"         : 4,
    "admin"       : 5
}

ranks = open_json_file(config_file, ranks)

def save_ranks():
    save_json_file(config_file, ranks)

#-----------------------Event---------------------------

@hook.event("player.PlayerJoinEvent", "normal")
def on_player_join(event):
    user = event.getPlayer()
    uuid = uid(player).replace("-", "")

    sql_instruction

    def callback_thing(role, args):

        if role in [1, 2, 6]: #Disabled/Banned/Superadmin
            return
        if role != None:
            for rank in ranks:
                if user.hasPermission("group." + rank):
                    if role != ranks[rank]:
                        set_role(uuid, ranks[rank])
        elif user.hasPlayedBefore():
            msg(user, "&cYou haven't registed yet! Make sure to do so on redstoner.com")


def get_role(uuid):
    results = execute_query("SELECT `role_id` FROM users WHERE `uuid` = ? LIMIT 1;", uuid)
    return results[0][0]
    # Returns a table with 1 row (LIMIT 1) and 1 column (SELECT `role_id`), so we're looking for the first row of the first column.


def set_role(uuid, role_id):
    execute_update("UPDATE users SET `role_id` = ? WHERE `uuid` = ?;", (role_id, uuid,))
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
    conn.commit()
    curs.close()
    conn.close()

def get_role(uuid):
    sql_instruction()

#--------------------------------Queries / Updates----------------------------

def sql_instruction(instruction, args, fetch = True, callback_func = ignored_func, callback_args = tuple()):
    thread = threading.Thread(target = curs_instruction, args = (instruction_executor, instruction, fetch, callback_func, callback_args))
    thread.start()
    

def curs_instruction(func, instruction, fetch, callback_func, callback_args):
    conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
    curs = conn.getCursor()

    if fetch:
        returned = func(curs, instruction, fetch)
        curs.close()
        conn.close()
        callback_func(returned, callback_args)

    else:
        func(curs, instruction, fetch)
        conn.commit()
        curs.close()
        conn.close()


def instruction_executor(curs, instruction, fetch):
    curs.execute(instruction)
    return curs.fetchall() if fetch else None

def ignored_func(*args):
    pass