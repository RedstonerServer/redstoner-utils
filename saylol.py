import simplejson as json
from time import time
from helpers import *
from random import randrange

lol_filename = "plugins/redstoner-utils.py.dir/files/lol.json"
lols         = []
timeout      = 15
last_msg     = 0

try:
  lols = json.loads(open(lol_filename).read())
except Exception, e:
  error("Failed to load lols: %s" % e)



def save_lols():
  try:
    lolfile = open(lol_filename, "w")
    lolfile.write(json.dumps(lols))
    lolfile.close()
  except Exception, e:
    error("Failed to write lols: " + str(e))

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
      dispname = sender.getDisplayName() if isPlayer(sender) else sender.getName()
      broadcast("", "&8[&blol&8] &7%s&8: &e%s" % (dispname, lols[lid]))
      last_msg = time()
    else:
      plugHeader(sender, "SayLol")
      msg(sender, "&cInvalid id")
  else:
    plugHeader(sender, "SayLol")
    msg(sender, "&cYou can use SayLol again in &a%s seconds!" % int(timeout + 1 - (time() - last_msg)))


@hook.command("lol")
def onLolCommand(sender, args):
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
        plugHeader(sender, "SayLol")
        msg(sender, "&cInvalid number '&e%s&c'" % args[1])
    else:
      noperm(sender)

  elif cmd == "list":
    plugHeader(sender, "SayLol")
    for i in range(len(lols)):
      msg(sender, "&a%s: &e%s" % (str(i).rjust(3), lols[i]))

  elif cmd == "add":
    if sender.hasPermission("utils.lol.modify"):
      plugHeader(sender, "SayLol")
      add_lol(" ".join(args[1:]))
      msg(sender, "&aNew lol message added!")
    else:
      noperm(sender)

  elif cmd == "del":
    if sender.hasPermission("utils.lol.modify"):
      plugHeader(sender, "SayLol")
      try:
        i = int(args[1])
        del_lol(i)
        msg(sender, "&aLol message &e#%s&a deleted!" % i)
      except ValueError:
        msg(sender, "&cInvalid number '&e%s&c'" % args[1])

  else:
    plugHeader(sender, "SayLol")
    msg(sender, "&a/lol            &eSay random message")
    msg(sender, "&a/lol list       &eList all messages")
    msg(sender, "&a/lol id <id>    &eSay specific message")
    msg(sender, "&a/lol add <text> &eAdd message")
    msg(sender, "&a/lol del <id>   &eDelete message")
  return True
