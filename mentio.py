from helpers import *
from re import compile as reg_compile
from traceback import format_exc as print_traceback


mentions   = open_json_file("mentio", {}) # contains a list of keywords for each player (uuid)
max_amount = 1000
arrow      = colorify(u"&r&7\u2192&r")
colors_reg = reg_compile(u"\u00A7[\\da-fk-or]") # finds color codes


def saveMentions():
    save_json_file("mentio", mentions)


@hook.event("player.AsyncPlayerChatEvent", "monitor")
def onChat(event):
    if not event.isCancelled():
        sender     = event.getPlayer()
        words      = event.getMessage().split(" ")
        recipients = event.getRecipients() # set of <Player>, may be a lazy or unmodifiable collection

        for recipient in list(recipients):
            recuid = uid(recipient)

            if recuid in mentions:
                keywords = mentions[uid(recipient)]
            else:
                # player
                keywords = [recipient.getName().lower(), stripcolors(recipient.getDisplayName()).lower()]

            rec_words = words[:] # copy
            for index, word in enumerate(rec_words):
                isMentioned = False

                for keyword in keywords:
                    if keyword in word.lower(): # is the keyword mentioned
                        isMentioned = True

                if isMentioned:
                    # join all color codes used upto this word
                    colors = "".join(colors_reg.findall("".join(words[:index+1])))
                    # highlight the word containing mention, then apply all previous color codes
                    rec_words[index] = colorify("&r&a&o") + stripcolors(word) + colorify("&r") + colors
                    # No need to
                    break

            # player was mentioned
            if rec_words != words:
                try:
                    recipients.remove(recipient) # don't send original message
                except:
                    # list might not be mutable, ignoring. Receiver will get the message twice
                    pass
                message = " "+" ".join([sender.getDisplayName(), arrow] + rec_words)
                msg(recipient, message, usecolor = False)
                recipient.playSound(recipient.getLocation(), "mob.chicken.plop", 1, 2)


def get_keywords(player):
    sender_id = uid(player)
    if sender_id in mentions.keys():
        keywords = mentions[sender_id]
    else:
        keywords = []
    return keywords


def add_keyword(sender, args):
    keywords = get_keywords(sender)
    new_word = stripcolors(args[1].lower())

    if (len(keywords) >= max_amount) and (max_amount >= 0):
        msg(sender, "&cYou are already listening for %s words! Try &6/mentio del <word>" % max_amount)
        return True

    if len(new_word) > 20:
        msg(sender, "&cThis word is longer than 20 characters. Pick a shorter one!")
        return True

    if new_word in keywords:
        msg(sender, "&cYou are already listening for this word! Try &6/mentio list")
        return True

    keywords.append(new_word)
    if keywords:
        mentions[uid(sender)] = keywords

    msg(sender, "&aYou are now listening for '&2%s&2'!" % new_word)
    saveMentions()
    return True


def del_keyword(sender, args):
    keywords = get_keywords(sender)
    del_word = stripcolors(args[1].lower())

    if not keywords:
        msg(sender, "&cYou are currently listening for no words! Try &6/mentio add <word>")
        return

    if del_word in keywords:
        keywords.remove(del_word)
        sender_id = uid(sender)
        if keywords:
            mentions[sender_id] = keywords
        elif sender_id in mentions:
            del mentions[sender_id]
        saveMentions()
        msg(sender, "&aYou are no longer listening for '&2%s&2'!" % del_word)
    else:
        msg(sender, "&cWe can't remove something that doesn't exist! Try &6/mentio list")


def show_help(player):
    msg(player, "&a/mentio add <word>")
    msg(player, "&a/mentio del <word>")
    msg(player, "&a/mentio list")


@hook.command("mentio")
def onListenCommand(sender, command, label, args):
    plugin_header(sender, "Mentio")

    argnum = len(args)
    if argnum:
        cmd = args[0].lower()

        # /mentio add <word>
        if argnum == 2 and cmd == "add":
            add_keyword(sender, args)

        # /mentio del <word>
        elif argnum == 2 and cmd == "del":
            del_keyword(sender, args)

        # /mentio list
        elif argnum == 1 and cmd == "list":
            msg(sender, "&aWords you're listening for:")
            keywords = get_keywords(sender)
            for word in keywords:
                msg(sender, "&c- &3%s" % word)
            if not keywords:
                msg(sender, "&cYou are currently listening for no words! Try &6/mentio add <word>")
        else:
            show_help(sender)
    else:
        show_help(sender)
    return True
