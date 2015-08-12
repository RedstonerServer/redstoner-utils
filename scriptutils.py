from helpers import *

"""
Prints server restart message
arg 0 timeout
arg 1 $(whoami)
arg 2: reason
"""
@hook.command("script_restart")
def print_restart(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&2&l=============================================")
        broadcast(None, "&r")
        broadcast(None, "&r")
        broadcast(None, "&9%s is restarting the server." % args[1])
        broadcast(None, "&a&lServer is going to restart in %s seconds." % args[0])
        broadcast(None, "&6&l%s" % " ".join(args[2:]))
        broadcast(None, "&r")
        broadcast(None, "&r")
        broadcast(None, "&2&l=============================================")
    else:
        noperm(sender)

"""
Prints the server shut down message
arg 0 timeout
arg 1 $(whoami)
arg 2: reason
"""
@hook.command("script_stop")
def print_stop(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&2&l=============================================")
        broadcast(None, "&r")
        broadcast(None, "&r")
        broadcast(None, "&9%s is shutting down the server." % args[1])
        broadcast(None, "&a&lServer is going to shut down in %s seconds." % args[0])
        broadcast(None, "&6&l%s" % " ".join(args[2:]))
        broadcast(None, "&r")
        broadcast(None, "&r")
        broadcast(None, "&2&l=============================================")
    else:
        noperm(sender)

"""
Prints the shut down abort message
"""
@hook.command("script_stop_abort")
def abort_stop(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&4&oShut down has been aborted.")
    else:
        noperm(sender)

"""
Prints the restart abort message
"""
@hook.command("script_restart_abort")
def abort_restart(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&4&oRestart has been aborted.")
    else:
        noperm(sender)

"""
Prints the backup started message, saves all worlds and turns off world saving
"""
@hook.command("script_backup_begin")
def print_backup_begin(sender, command, lable, args):
    if not is_player(sender):
        broadcast(None, "&4 =&2 Starting backup now.")
        server.dispatchCommand(server.getConsoleSender(), "save-all")
        server.dispatchCommand(server.getConsoleSender(), "save-off")
    else:
        noperm(sender)

"""
Prints the backup finished message and turns on world saving
"""
@hook.command("script_backup_end")
def print_backup_end(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&4 =&2 Backup completed.")
        server.dispatchCommand(server.getConsoleSender(), "save-on")
    else:
        noperm(sender)

"""
Prints the backup error message and turns on world saving
"""
@hook.command("script_backup_error")
def print_backup_error(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&4 =&c&l Error while backing up!")
        server.dispatchCommand(server.getConsoleSender(), "save-on")
    else:
        noperm(sender)

"""
Prints the world trimming started message and starts trimming
"""
@hook.command("script_trim")
def print_backup_trim(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&4 =&3 Deleting all chunks beyond broder now.")
        server.dispatchCommand(server.getConsoleSender(), "wb Creative trim 1000000 15")
        server.dispatchCommand(server.getConsoleSender(), "wb trim confirm")
    else:
        noperm(sender)

"""
Prints the thimming finished message
arg 0 size difference of world
arg 1: world border trim data
"""
@hook.command("script_trim_result")
def print_backup_trim_res(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&4 =&3 Chunk deletion saved %s (&a%sMB&3)" % (" ".join(args[1:]), args[0]))
    else:
        noperm(sender)

"""
Prints the database backup started message and admin-chat warning
"""
@hook.command("script_backup_database_begin")
def print_backup_db_begin(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&6 =&2 Starting database backup now.")
        server.dispatchCommand(server.getConsoleSender(), "ac &aLogblock may be unavailable!")
    else:
        noperm(sender)

"""
Prints the database dumps compression started message
"""
@hook.command("script_backup_database_dumps")
def print_backup_db_dumps(sender, command, label, args):
    if not is_player(sender):
        server.dispatchCommand(server.getConsoleSender(), "ac &aDumps completed, logblock available again.")
        server.dispatchCommand(server.getConsoleSender(), "ac &aNow compressing dumps, will take a while...")
    else:
        noperm(sender)

"""
Prints the database finished message and backup size in admin-chat
arg 0 size of backup
"""
@hook.command("script_backup_database_end")
def print_backup_db_end(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&6 =&2 Databse backup completed.")
        server.dispatchCommand(server.getConsoleSender(), "ac &abackup size: &2%sMB&a." % args[0])
    else:
        noperm(sender)

"""
Prints the database backup error message
"""
@hook.command("script_backup_database_error")
def print_backup_db_error(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&6 =&c&l Error while backing up database!")
    else:
        noperm(sender)

"""
Prints the database backup abort message
"""
@hook.command("script_backup_database_abort")
def print_backup_db_abort(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&6 =&2 Database backup aborted.")
    else:
        noperm(sender)

"""
Prints the spigot update message
"""
@hook.command("script_spigot_update")
def print_update(sender, command, label, args):
    if not is_player(sender):
        broadcast(None, "&9 =&2 A new Spigot version has been downloaded!")
        broadcast(None, "&9 =&2 Update will be applied after the next reboot.")
    else:
        noperm(sender)

"""
Prints the admin-chat warning for disk is filled
arg 0 fill percentage
"""
@hook.command("script_disk_filled")
def print_disk_filled(sender, command, label, args):
    if not is_player(sender):
        server.dispatchCommand(server.getConsoleSender(), "ac &4&lWARNING:&6 Disk is filled > 96% (" + args[0] + "%)")
        server.dispatchCommand(server.getConsoleSender(), "ac &4  Server will shut down at 98%!")
        server.dispatchCommand(server.getConsoleSender(), "ac &4  Contact an admin &nimmediately&4!")
    else:
        noperm(sender)

"""
Saves all worlds, kicks players and shuts down the server
arg 0: reason
"""
@hook.command("script_shutdown")
def shutdown(sender, command, label, args):
    if not is_player(sender):
        server.dispatchCommand(server.getConsoleSender(), "save-all")
        server.dispatchCommand(server.getConsoleSender(), "kickall %s" % " ".join(args))
        server.dispatchCommand(server.getConsoleSender(), "stop")
    else:
        noperm(sender)
