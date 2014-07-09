from helpers import *
from re import compile as reg_compile

rank_regex = "visitor|member|builder|trusted|helper|mod|admin"

faq_regex = [
  # Asking for ranks or WE
  "how.+ (get|be(come)?|).+ (%s|WorldEdit|WE|W.E.)" % rank_regex,
  # Asking why p clear won't work
  "why.+ can.+( /?p clear| clear.+plot)"
]

faq_regex = [reg_compile(reg) for reg in faq_regex]

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
      break