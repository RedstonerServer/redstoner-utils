from helpers import *
from re import compile as reg_compile

answers = []


def load_answers():
    global answers
    answers = open_json_file("abot", [])

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
def on_abot_command(sender, command, label, args):
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


def check_msg(event, message):
    sender = event.getPlayer()
    for answer in answers:
        for regex in answer["regex"]:
            if regex.search(message):
                if not answer["hide-perm"] or not sender.hasPermission(answer["hide-perm"]):
                    plugin_header(sender, "AnswerBot")
                    msg(sender, answer["message"] + "\n ")
                    event.setCancelled(True)
                    info("(hidden) %s: '%s'" % (sender.getName(), message))
                    break


@hook.event("player.AsyncPlayerChatEvent", "low")
def on_chat(event):
    check_msg(event, event.getMessage().lower())

@hook.event("player.PlayerCommandPreprocessEvent", "low")
def on_any_cmd(event):
    words = event.getMessage().lower().split(" ")
    cmd = words[0][1:]
    if cmd in ["msg", "m", "t", "pm", "mail", "r", "reply"]:
        check_msg(event, " ".join(words[1:]))

load_answers()