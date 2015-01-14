from helpers import *
from traceback import format_exc as print_traceback
import time

an_permission      = "utils.an";
notes              = open_json_file("adminnotes", [])
continued_messages = {}


def save_notes():
    save_json_file("adminnotes", notes)


def r_ago(unit, i):
    # Return ago + plural
    i = i
    if i != 1:
        unit +="s"
    return str(i)+" "+unit+" ago"


def calc_diff(time_ago):
    current = time.time()
    s = current-time_ago
    s = int(s)
    ago = "Some time ago"

    if s < 10:
        ago = "Just now"
    elif s >= 10 and s < 60:
        ago = r_ago("second", s)
    elif s >= 60 and s < 3600:
        ago = r_ago("minute", s/60)
    elif s >= 3600 and s < 43200:
        ago = r_ago("hour", s/60/60)
    elif s >= 43200:
        ago = r_ago("day", s/60/60/12)
    return ago


def show_all_notes(sender):
    if len(notes) == 0:
        msg(sender, "&aNo open notes at the moment!")
    for i in range(0, len(notes)):
        arr = notes[i]
        name      = arr[0]
        message   = arr[1]
        note_time = arr[2]

        ago = calc_diff(note_time)

        msg(sender, "&6#%s - &e%s&6, %s:" % (str(i+1), name, ago))
        msg(sender, "&7%s" % colorify(message))


def show_an_help(sender):
    msg(sender, "&6AdminNotes Help:")
    msg(sender, "&e- /an")
    msg(sender, "&7&oLists all notes")
    msg(sender, "&e- /an del <ID>")
    msg(sender, "&7&oRemove a note")
    msg(sender, "&e- /an help")
    msg(sender, "&7&oShows this menu")
    msg(sender, "&e- /an Some text...")
    msg(sender, "&7&oWrite a new note")
    msg(sender, "&e- /an This text is very++")
    msg(sender, "&7&oContinue writing your note when using &e/an long guys!&7&o again")


@hook.command("an", aliases=["adminnotes", "adminnote"])
def adminnotes_command(sender, args):
    if not sender.hasPermission(an_permission):
        noperm(sender)
        return
    try:
        arglen = len(args)

        # arg length not valid
        if arglen < 1:
            show_all_notes(sender)
            return

        # Shows note help
        if args[0].lower() == "help":
            show_an_help(sender)
            return

        # Delete note
        if args[0].lower() == "del":
            if arglen != 2:
                show_an_help(sender)
                return
            if not args[1].isdigit():
                msg(sender, "&cThe ID has to be numeric (check /an if you're unsure)")    
                return
            note_id = int(args[1])-1
            if note_id >= len(notes):
                msg(sender, "&cThere is no note with that ID!")
                return
            # Deletes note by index
            del notes[note_id]
            save_notes()
            msg(sender, "&aSuccessfully deleted note #%s!" % str(note_id+1))
            return

        message = " ".join(args)
        name = sender.getName()
        if name in continued_messages:
            message = continued_messages[name] + message

        if message[-2:] == "++":
            message = message[:-2]
            if message[-1:] != " ":
                message += " "
            continued_messages[name] = message
            msg(sender, "&6You can continue writing by using &e/an <text ...>")
        else:
            notes.append([name, message, time.time()])
            save_notes()
            msg(sender, "&eNew note:&6 "+message)
            broadcast(an_permission, "&a%s just added a new note! &2Type /an" % name)
    except:
        print(print_traceback())


@hook.event("player.PlayerJoinEvent", "monitor")
def on_an_join(event):
    if len(notes) > 0:
        msg(event.getPlayer(), "&cThere are currently %s open notes!" % len(notes))
    elif len(notes) == 0:
        msg(event.getPlayer(), "&aThere are currently no open notes!")