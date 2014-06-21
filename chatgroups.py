#pylint: disable=F0401
from helpers import *
import simplejson as json

chatgroups_filename = "plugins/redstoner-utils.py.dir/files/chatgroups.json"
groups              = {}
cg_key              = "."
cg_toggle_list      = []

try:
  groups = json.loads(open(chatgroups_filename).read())
except Exception, e:
  error("Failed to load chatgroups: %s" % e)


@hook.command("chatgroup")
def onChatgroupCommand(sender, args):
  try:
    plugHeader(sender, "ChatGroups")
    if len(args) == 1 and args[0] == "leave":
      if sender.getName() in groups.keys():
        groupchat(sender, "left the group", True)
        group = groups[sender.getName()]
        del(groups[sender.getName()])
        saveGroups()
      else:
        msg(sender, "&aYou can't leave no group, derp!")
    elif len(args) == 1 and args[0] == "info":
      if sender.getName() in groups.keys():
        group = groups[sender.getName()]
        msg(sender, "&aCurrent chatgroup: %s" % group)
        users = []
        for user, ugroup in groups.iteritems():
          if ugroup == group:
            users += [user]
        msg(sender, "&aUsers in this group:")
        msg(sender,  "&a%s" % ", ".join(users))
      else:
        msg(sender, "&aYou're in no chatgroup.")
    elif len(args) == 2 and args[0] == "join":
      groups[sender.getName()] = args[1]
      groupchat(sender, "joined the group", True)
      saveGroups()
      msg(sender, "&aYour chatgroup is set to '%s'" % args[1])
      msg(sender, "&aAnyone in the group sees chat that begins with &e%s" % cg_key)
    else:
      msg(sender, "&e/chatgroup join <name>")
      msg(sender, "&e/chatgroup leave")
      msg(sender, "&e/chatgroup info")
  except Exception, e:
    error(e)


@hook.command("cgt")
def onCgtCommand(sender, args):
  p = sender.getName()
  if p in cg_toggle_list:
    cg_toggle_list.remove(p)
    msg(sender, "&8[&bCG&8] &e&oCG toggle: off")
  else:
    cg_toggle_list.append(p)
    msg(sender, "&8[&bAC&8] &e&oCG toggle: on")
  return True

def groupchat(sender, message, ann=False):
  #try:
  group = groups.get(sender.getName())
  if group == None:
    msg(sender, "&cYou are not in a group!")
    return
  name = sender.getDisplayName()
  if ann:
    mesg = "&8[&bCG&8] &e&o%s&e&o %s" % (name, message)
  else:
    mesg = "&8[&bCG&8] &f%s&f: &6%s" % (name, message)
  for receiver in server.getOnlinePlayers():
    groups.get(receiver.getName()) == group and msg(receiver, mesg)
  #except Exception, e:
  #  error(e)


def saveGroups():
  try:
    chatgroups_file = open(chatgroups_filename, "w")
    chatgroups_file.write(json.dumps(groups))
    chatgroups_file.close()
  except Exception, e:
    error("Failed to write reports: " + str(e))


@hook.event("player.AsyncPlayerChatEvent", "normal")
def onChat(event):
  sender = event.getPlayer()
  msge = event.getMessage()
  if not event.isCancelled():
    if msge[:len(cg_key)] == cg_key and sender.getName() in groups.keys():
      groupchat(sender, msge[1:])
      event.setCancelled(True)
    elif sender.getName() in cg_toggle_list:
      groupchat(sender, msge)
      event.setCancelled(True)
