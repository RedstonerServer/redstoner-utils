from time import time
from helpers import *
from random import randrange

lols     = open_json_file("lol", [])
timeout  = 15
last_msg = 0



def save_lols():
  save_json_file("lol", lols)


def add_lol(txt):
  lols.append(txt)
  save_lols()


def del_lol(lid):
  lols.pop(lid)
  save_lols()


def print_lol(sender, lid):
  global last_msg
  if time() - last_msg > timeout:
    if len(lols) > lid:
      dispname = sender.getDisplayName() if is_player(sender) else sender.getName()
      broadcast(None, "&8[&blol&8] &7%s&8: &e%s" % (dispname, lols[lid]))
      last_msg = time()
    else:
      plugin_header(sender, "SayLol")
      msg(sender, "&cInvalid id")
  else:
    plugin_header(sender, "SayLol")
    msg(sender, "&cYou can use SayLol again in &a%s seconds!" % int(timeout + 1 - (time() - last_msg)))


def search_lols(sender, keyword):
  if not keyword:
    msg(sender, "&cPlease provide a keyword to search for!")
    return
  msg(sender, "&aLols containing '&6%s&a':" % keyword)
  for i, lol in enumerate(lols):
    if keyword in lol:
      msg(sender, "&a%s: &e%s" % (str(i).rjust(3), lol))
  msg(sender, "") # empty line showing end of list


@hook.command("lol")
def on_lol_command(sender, args):
  plugin_header(sender, "SayLol")

  cmd = args[0] if len(args) > 0 else None
  if len(args) == 0:
    if sender.hasPermission("utils.lol"):
      print_lol(sender, randrange(len(lols)))
    else:
      noperm(sender)

  elif cmd == "id":
    if sender.hasPermission("utils.lol.id"):
      try:
        i = int(args[1])
        print_lol(sender, i)
      except ValueError:
        msg(sender, "&cInvalid number '&e%s&c'" % args[1])
    else:
      noperm(sender)

  elif cmd == "list":
    for i in range(len(lols)):
      msg(sender, "&a%s: &e%s" % (str(i).rjust(3), lols[i]))

  elif cmd == "search":
    if sender.hasPermission("utils.lol.search"):
      search_lols(sender, " ".join(args[1:]))
    else:
      noperm(sender)

  elif cmd == "add":
    if sender.hasPermission("utils.lol.modify"):
      add_lol(" ".join(args[1:]))
      msg(sender, "&aNew lol message added!")
    else:
      noperm(sender)

  elif cmd == "del":
    if sender.hasPermission("utils.lol.modify"):
      try:
        i = int(args[1])
        del_lol(i)
        msg(sender, "&aLol message &e#%s&a deleted!" % i)
      except ValueError:
        msg(sender, "&cInvalid number '&e%s&c'" % args[1])

  else:
    msg(sender, "&a/lol            &eSay random message")
    msg(sender, "&a/lol list       &eList all messages")
    msg(sender, "&a/lol id <id>    &eSay specific message")
    msg(sender, "&a/lol add <text> &eAdd message")
    msg(sender, "&a/lol del <id>   &eDelete message")
  return True
