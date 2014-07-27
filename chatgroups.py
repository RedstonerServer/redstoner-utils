#pylint: disable = F0401
from helpers import *
from java.util.UUID import fromString as juuid

groups         = open_json_file("chatgroups", {})
cg_key         = ":"
cg_toggle_list = []



@hook.command("chatgroup")
def on_chatgroup_command(sender, args):
  plugin_header(sender, "ChatGroups")
  sender_id = uid(sender)
  if len(args) == 1 and args[0] == "leave":
    if sender_id in groups.keys():
      groupchat(sender, "left the group", True)
      group = groups[sender_id]
      del(groups[sender_id])
      save_groups()
    else:
      msg(sender, "&aYou can't leave no group, derp!")
  elif len(args) == 1 and args[0] == "info":
    if sender_id in groups.keys():
      group = groups[sender_id]
      msg(sender, "&aCurrent chatgroup: %s" % group)
      users = []
      for uuid, ugroup in groups.iteritems():
        if ugroup == group:
          usr = server.getPlayer(juuid(uuid))
          if usr:
            users.append(usr.getDisplayName())
      msg(sender, "&aUsers in this group:")
      msg(sender,  "&a%s" % ", ".join(users))
    else:
      msg(sender, "&aYou're in no chatgroup.")
  elif len(args) == 2 and args[0] == "join":
    groups[sender_id] = args[1]
    groupchat(sender, "joined the group", True)
    save_groups()
    msg(sender, "&aYour chatgroup is set to '%s'" % args[1])
    msg(sender, "&aUse chat like '&e%s<message>' to send messages to this group." % cg_key)
  else:
    msg(sender, "&e/chatgroup join <name>")
    msg(sender, "&e/chatgroup leave")
    msg(sender, "&e/chatgroup info")


@hook.command("cgt")
def on_cgt_command(sender, args):
  p = uid(sender)
  if p in cg_toggle_list:
    cg_toggle_list.remove(p)
    msg(sender, "&8[&bCG&8] &e&oCG toggle: off")
  else:
    cg_toggle_list.append(p)
    msg(sender, "&8[&bCG&8] &e&oCG toggle: on")
  return True


def groupchat(sender, message, ann = False):
  group = groups.get(uid(sender))
  if group == None:
    msg(sender, "&cYou are not in a group!")
    return
  name = sender.getDisplayName()
  if ann:
    mesg = "&8[&bCG&8] &e&o%s&e&o %s" % (name, message)
  else:
    mesg = "&8[&bCG&8] &f%s&f: &6%s" % (name, message)
  info("[ChatGroups] %s (%s): %s" % (sender.getDisplayName(), group, message))
  for receiver in server.getOnlinePlayers():
    groups.get(uid(receiver)) == group and msg(receiver, mesg)



def save_groups():
  save_json_file("chatgroups", groups)


@hook.event("player.AsyncPlayerChatEvent", "normal")
def on_chat(event):
  sender = event.getPlayer()
  msge = event.getMessage()
  if not event.isCancelled():
    sender_id = uid(sender)
    if msge[:len(cg_key)] == cg_key and sender_id in groups.keys():
      groupchat(sender, msge[1:])
      event.setCancelled(True)
    elif sender_id in cg_toggle_list:
      groupchat(sender, msge)
      event.setCancelled(True)
