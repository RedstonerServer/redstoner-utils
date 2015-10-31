from helpers import *
import threading
import time

calc_users        = open_json_file("calc", [])
math_operators    = ["+", "-", "*", "/", "%", ">", "<", "^", "&", "|"]
allowed_strings   = ["0b", "0x", "(", ")", "hex(", "bin(", "abs(", "int(", "min(", "max(", "round(", "float("]
allowed_alpha     = ["a", "b", "c", "d", "e", "f"]
calc_perm = "utils.calc"
calc_perm_power = "utils.calc.power"

def calc(sender, text):
    try:
        return do_calc(sender, text.lower())
    except:
        return None

def do_calc(sender, text):
    """
    extracts a mathematical expression from `text`
    returns (expression, result) or None
    """
    expression = ""
    should_calc = False
    i = 0
    while True:
        if i >= len(text):
            break
        char = text[i]
        if i < len(text) - 5 and str(char + text[i+1] + text[i+2] + text[i+3] + text[i+4] + text[i+5]) in allowed_strings:
            expression += char
            expression += text[i + 1]
            expression += text[i + 2]
            expression += text[i + 3]
            expression += text[i + 4]
            expression += text[i + 5]
            i += 5
            should_calc = True
        elif i < len(text) - 3 and str(char + text[i+1] + text[i+2] + text[i+3]) in allowed_strings:
            expression += char
            expression += text[i + 1]
            expression += text[i + 2]
            expression += text[i + 3]
            i += 3
            should_calc = True
        elif i < len(text) - 1 and str(char + text[i + 1]) in allowed_strings:
            expression += char
            expression += text[i + 1]
            i += 1
            should_calc = True
        elif char.isdigit() or char in allowed_alpha or (expression and char == ".") or (should_calc and char == " ") or (should_calc and char == ","):
            expression += char
            should_calc = True
        elif char in math_operators or char in ["(", ")"]:
            # calculation must include at least 1 operator
            should_calc = True
            expression += char
        elif should_calc and char.isalpha():
            # don't include any more text in the calculation
            break
        i += 1
    last_char = ' '
    for char in expression:
        if last_char == '*' and char == '*':
            if sender.hasPermission(calc_perm_power):
                break
            else:
                return None
        last_char = char
    if should_calc:
        try:
            result = str(eval(expression)) # pylint: disable = W0123
        except: # pylint: disable = W0702
            # we can run into all kinds of errors here
            # most probably SyntaxError
            return None
        return (expression, result)
    return None

def thread_calc(message, sender):
    output = calc(sender, message)
    if output and sender.isOnline():
        msg(sender, "&2=== Calc: &e" + output[0] + " &2= &c" + output[1])

@hook.event("player.AsyncPlayerChatEvent", "monitor")
def on_calc_chat(event):
    sender = event.getPlayer()
    message = event.getMessage()
    if not event.isCancelled() and uid(sender) in calc_users and sender.hasPermission(calc_perm):
        thread = threading.Thread(target=thread_calc, args=(message, sender))
        thread.daemon = True
        thread.start()


@hook.command("calc", description="Toggles chat calculations")
def on_calc_command(sender, command, label, args):
    plugin_header(sender, "Chat Calculator")
    if not sender.hasPermission(calc_perm):
        noperm(sender)
        return True
    if not checkargs(sender, args, 0, 1):
        return True
    if not is_player(sender):
        msg(sender, "&cYou are not a player!")
        return True

    toggle(sender, calc_users, name = "Calc")
    save_json_file("calc", calc_users)

    return True
