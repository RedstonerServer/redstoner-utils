from helpers import *
from re import compile as reg_compile

rank_regex = "visitor|member|builder|trusted|helper|mod|admin|owner|rank"

faq_regex = [
  # ranks
  "(how.+ (get|be(come)?|)|who is).+ (%s)" % rank_regex,
  # WE
  "(can|how|why).+ (have|haz|use|get|doesn|can'?t).+ (WorldEdit|WE|W.E.)",
  # clearing plot
  "(why|how).+ (do|can).+( /?p clear| clear.+ plot)",
  # add someone to a plot
  "how.+ add.+ plot"
]

faq_regex = [reg_compile(reg.lower()) for reg in faq_regex]

@hook.event("player.AsyncPlayerChatEvent", "low")
def onChat(event):
  sender  = event.getPlayer()
  message = event.getMessage().lower()
  for regex in faq_regex:
    if regex.search(message):
      plugHeader(sender, "AnswerBot")
      msg(sender, "&aIt looks like you aksed a question that is likely answered in our FAQ.")
      msg(sender, "&aPlease take a look at the &4&l/faq&a command and read through the pages.")
      event.setCancelled(True)
      log("(Answerbot) hiding message from %s: '%s'" % (sender.getName(), message))
      break