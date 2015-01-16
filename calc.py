from helpers import *

calc_users        = open_json_file("calc", [])
math_operators    = ["+", "-", "*", "/", "&", "|",".",]
ignore_operators  = ["**", "&&", "||"] # ** may be too intensive, the others cause syntax errors
calc_perm = "utils.calc"


def calc(text):
    """
    extracts a mathematical expression from `text`
    returns (expression, result) or None
    """
    expression = ""
    should_calc = False
    for char in text:
        if char.isdigit() or (should_calc and char in [".", " "]):
            expression += char
        elif char in math_operators:
            # calculation must include at least 1 operator
            should_calc = True
            expression += char
        elif should_calc and char.isalpha():
            # don't include any more text in the calculation
            break
    if should_calc and not any(op in expression for op in ignore_operators):
        try:
            result = str(eval(expression)) # pylint: disable = W0123
        except: # pylint: disable = W0702
            # we can run into all kinds of errors here
            # most probably SyntaxError
            return None
        return (expression, result)
    return None


@hook.event("player.AsyncPlayerChatEvent", "monitor")
def on_calc_chat(event):
    sender = event.getPlayer()
    message = event.getMessage()
    if not event.isCancelled() and uid(sender) in calc_users and sender.hasPermission(calc_perm):
        output = calc(message)
        if output:
            msg(sender, "&2=== Calc: &e" + output[0] + " &2= &c" + output[1])


@hook.command("calc", description="Toggles chat calculations")
def on_calc_command(sender, args):
    plugin_header(sender, "Chat Calculator")
    if not sender.hasPermission(calc_perm):
        noperm(sender)
        return True
    if not checkargs(sender, args, 0, 1):
        return True
    if not is_player(sender):
        msg(sender, "&cYou are not a player!" % sender)
        return True

    toggle(sender, calc_users, name = "Calc")
    save_json_file("calc", calc_users)

    return True
