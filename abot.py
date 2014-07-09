from helpers import *
from re import compile as reg_compile

rank_regex = "visitor|member|builder|trusted|helper|mod|admin|owner|rank"

faq_regex = [
  # ranks
  "(how.*? (get|be(come)?|)|who is|are you).*? (%s)" % rank_regex,
  # WE
  "(can|how|why).*? (have|haz|use|get|doesn|can'?t).*? (WorldEdit|WE|W.E.)",
  # clearing plot
  "(why|how).*? (do|can).*?( /?p clear| clear.*? plot)",
  # add someone to a plot
  "how.*? add.*? plot"
]

faq_regex = [reg_compile(reg.lower()) for reg in faq_regex]

@hook.event("player.AsyncPlayerChatEvent", "low")
def onChat(event):
  sender  = event.getPlayer()
  message = event.getMessage().lower()
  for regex in faq_regex:
    if regex.search(message):
      plugHeader(sender, "AnswerBot")
      msg(sender, "&aLooks like you're asking something that's likely in our FAQ.")
      msg(sender, "&aTake a look at &4&l/faq&a and read through the pages.\n ") # trailing space required
      event.setCancelled(True)
      log("(hidden) %s: '%s'" % (sender.getName(), message))
      break