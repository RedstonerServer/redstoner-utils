#pylint: disable=F0401
from helpers import *


mio_permission = "utils.mio"

@hook.event("player.PlayerChatEvent", "normal")
def onChat(event):
	symbol = u"\u272a"
	sender = event.getPlayer()
	messages = event.getMessage()
	messagesList = messages.split(" ")
	for message in messagesList:
		for recipient in server.getOnlinePlayers().tolist():
			if message[:3].lower() in recipient.getName().lower() and len(message) > 2:
				msg(recipient, "&6" + symbol + " &f%s &6mentioned you" % sender.getDisplayName())
				# Couldn't figure out how to do this
				# recipient.playSound(recipient.getLocation(), Sound.CHICKEN_EGG_POP, 1, 1)
