#pylint: disable=F0401
from helpers import *
from re import compile as reg_compile
from traceback import format_exc as print_traceback

arrow = colorify(u"&r&7\u2192&r")
regex = reg_compile(u"\u00A7[\\da-fk-or]")


@hook.event("player.AsyncPlayerChatEvent", "normal")
def onChat(event):
  try:
    if not event.isCancelled():
      sender     = event.getPlayer()
      words      = event.getMessage().split(" ")
      recipients = event.getRecipients()

      for recipient in list(recipients):
        rec_words = words[:] # copy
        for i in range(len(rec_words)):
          word = rec_words[i]
          if recipient.getName().lower() in word.lower():
            colors = "".join(regex.findall("".join(words[:i+1]))) # join all color codes used upto this word
            rec_words[i] = colorify("&r&a<&6") + stripcolors(word) + colorify("&r&a>&r") + colors # extra fancy highlight

        # player was mentioned
        if rec_words != words:
          try:
            recipients.remove(recipient) # don't send original message
          except:
            # list might not be mutable, ignoring. Receiver will get the message twice
            pass
          message = " ".join([sender.getDisplayName(), arrow] + rec_words)
          msg(recipient, message, usecolor = False)
          recipient.playSound(recipient.getLocation(), "mob.chicken.plop", 1, 0)
  except:
    error("Failed to handle PlayerChatEvent:")
    error(print_traceback())