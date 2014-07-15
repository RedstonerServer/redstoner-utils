import json
from helpers import *
from re import compile as reg_compile

answers_filename = "plugins/redstoner-utils.py.dir/files/abot.json"
answers = []


def load_answers():
  global answers
  try:
    answers = json.loads(open(answers_filename).read())
  except Exception, e:
    error("Failed to load answers: %s" % e)

  # compile answers
  for answer in answers:
    answer["regex"] = [reg_compile(reg.lower()) for reg in answer["regex"]]


def list_answers(sender):
  for answer in answers:
    msg(sender, "&e{")
    msg(sender, "  &eregex:")
    for regex in answer["regex"]:
      msg(sender, "    " + regex.pattern, basecolor="a", usecolor = False)
    msg(sender, "  &epermission:")
    msg(sender, "    " + str(answer["hide-perm"]), basecolor="a", usecolor = False)
    msg(sender, "  &emessage:")
    msg(sender, "    " + "\n    ".join(answer["message"].split("\n")))
    msg(sender, "&e}")


@hook.command("abot")
def on_abot_command(sender, args):
  plugin_header(sender, "AnswerBot")
  if sender.hasPermission("utils.abot.admin"):
    if not args:
      msg(sender, "&2/abot list    &eList all answers and their regex")
      msg(sender, "&2/abot reload  &eReload the config file")
    elif args[0] == "list":
      list_answers(sender)
    elif args[0] == "reload":
      load_answers()
      msg(sender, "&2Reloaded!")
    else:
      msg(sender)
  else:
    noperm(sender)
  return True


@hook.event("player.AsyncPlayerChatEvent", "low")
def on_chat(event):
  sender  = event.getPlayer()
  message = event.getMessage().lower()
  for answer in answers:
    for regex in answer["regex"]:
      if regex.search(message):
        if answer["hide-perm"] and not sender.hasPermission(answer["hide-perm"]):
          plugin_header(sender, "AnswerBot")
          msg(sender, answer["message"] + "\n ")
          event.setCancelled(True)
          log("(hidden) %s: '%s'" % (sender.getName(), message))
          break


load_answers()