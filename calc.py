from helpers import *

evals_toggle_list = []
math_operators    = ["+", "-", "*", "/", "&", "|"]
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
  if not event.isCancelled() and sender.getName() in evals_toggle_list and sender.hasPermission(calc_perm):
    output = calc(message)
    if output:
      msg(sender, "&2=== Calc: &e" + output[0] + " &2= &c" + output[1])


@hook.command("calc", description="Toggles chat calculations")
def on_calc_command(sender, args):
  plugin_header(sender, "Chat Calculator")
  if len(args):
    if not sender.hasPermission(calc_perm):
      noperm(sender)
      return
    target = args[0].lower()
    if not is_player(target):
      msg(sender, "&cLooks like %s isn't a player at all!" % target)
      return
    target = server.getPlayer(target)

    status = "disabled"
    if target.getName() in evals_toggle_list:
      evals_toggle_list.remove(target.getName())
    else:
      status = "enabled"
      evals_toggle_list.append(target.getName())
    msg(target, "&6We just &e%s&6 Chat Calculator for you!" % status)
    msg(sender, "&6We &e%s&6 this player's Chat Calculator" % status)

    return

  status = "disabled"
  if sender.getName() in evals_toggle_list:
    evals_toggle_list.remove(sender.getName())
  else:
    status = "enabled"
    evals_toggle_list.append(sender.getName())
  msg(sender, "&6We just &e%s&6 Chat Calculator for you!" % status)