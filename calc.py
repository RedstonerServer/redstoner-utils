from helpers import *

evals_toggle_list = []
calc_perm = "utils.calc"

def lex(msg):
  fullmessage = msg
  msg = list(msg)
  msg.append("f")
  print(msg)
  tok = ""
  expression = False
  counter = 0
  startPos = 0
  startPos_set = False
  endPos = 0
  for char in msg: 
    counter += 1
    if char.isnumeric():
      if not expression:
        startPos = counter
      expression = True
      tok += char
    elif char == "+" or char == "-" or char == "*" or char == "/":
      tok += char
    elif tok == " ":
      if not expression:
        tok = ""
      else:
        tok += char
    elif char.isalpha():
      if expression:
        print("It is an expression")
        msg = "".join(msg)

        print("Before evaluating: "+msg)
        print("Before evaluating (Token): "+tok)
        print("So that's str eval tok" +str(eval(tok)))

        return_value = msg[0:startPos-1]
        return_value += str(eval(tok))
        return_value += msg[counter:]
        print("Evaluated it: "+msg)
        expression = False
        return return_value
      else:
        print("It is NOT an expression - " + tok)
        tok = ""
  return fullmessage
 


@hook.event("player.AsyncPlayerChatEvent", "high")
def on_calc_chat(event):
  try:
    sender = event.getPlayer()
    message = event.getMessage()
    if sender.getName() not in evals_toggle_list:
      return
    output = lex(message)
    event.setMessage(colorify(str(output)))
  except Exception as e:
    print(e)
  
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