from helpers import *
from re import compile as reg_compile

rank_regex = "visitor|member|builder|trusted|helper|mod\\b|moderator|admin|owner|rank"

faq_regex = [
  # ranks
  "\\b(how.*? (get|be(come)?)|who is|are you).*? (%s)|who owns.* server" % rank_regex,
  # WE
  "\\b(can|how|why).*? (have|haz|use|get|doesn|can'?t).*? (WorldEdit|WE\\b|W\\.E\\.\\b)",
  # clearing plot
  "\\b((why|how|who).*? (do|can)|how to).*?( /?p clear| clear.*? plot)",
  # add someone to a plot, claim plot
  "\\bhow.*? (get|claim|own|add).*? plot"
]

faq_regex = [reg_compile(reg.lower()) for reg in faq_regex]

@hook.event("player.AsyncPlayerChatEvent", "low")
def onChat(event):
  sender  = event.getPlayer()
  if not sender.hasPermission("utils.ignore_abot"):
    message = event.getMessage().lower()
    for regex in faq_regex:
      if regex.search(message):
        plugHeader(sender, "AnswerBot")
        msg(sender, "&aLooks like you're asking something that's likely in our FAQ.")
        msg(sender, "&aTake a look at &4&l/faq&a and read through the pages.\n ") # trailing space required
        event.setCancelled(True)
        log("(hidden) %s: '%s'" % (sender.getName(), message))
        break
