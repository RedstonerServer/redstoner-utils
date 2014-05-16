import mysqlhack
import thread
from re import match
from com.ziclix.python.sql import zxJDBC
from helpers import *
from secrets import *
from secrets import *
from random import randrange

# table schema:
# string "uuid",  limit: 32, null: false
# string "token", limit: 6,  null: false
# string "email",            null: false


def mysql_query(query, args, fetch=True):
  conn    = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
  curs    = conn.cursor()
  curs.execute(query, args)
  if fetch:
    results = curs.fetchall()
  else:
    results = conn.commit()
  curs.close()
  conn.close()
  return results

def generate_token(length):
  cons = 'bcdfghjklmnpqrstvwxyz'
  vows = 'aeiou'

  token = ''
  start = randrange(2)
  for i in range(0, length):
    if i % 2 == start:
      token += cons[randrange(21)]
    else:
      token += vows[randrange(5)]
  return token

def set_token(uuid):
  token = generate_token(6)
  # REPLACE INTO website.register_token uuid={uuid}, token={token};
  return token

def get_token(uuid):
  # ae795aa86327408e92ab25c8a59f3ba1
  results = mysql_query("SELECT DISTINCT `token`, `email` FROM register_tokens WHERE `uuid` = ? LIMIT 1", (uuid,))
  return results[0] if len(results) == 1 else None
  
  
def token_command(sender, args, foo):
  plugHeader(sender, "Website Token")
  if isPlayer(sender):
    try:
      token = get_token(sender.getUniqueId().toString().replace("-", ""))
      if token:
        msg(sender, "&aEmail: &e%s" % token[1])
        msg(sender, "&aToken: &e%s" % token[0])
      else:
        msg(sender, "&cYou don't have a token yet! Use &e/tokengen <email>&c.")
    except Exception, e:
      error(e)
      msg(sender, "&cError getting your token, please contact an admin!")
  else:
    msg(sender, "&cThis is only for players..")

def tokengen_command(sender, args, foo):
  plugHeader(sender, "Website Token")
  if isPlayer(sender):
    if checkargs(sender, args, 1, -1):
      # email regex, needs something followed by an @ followed by something
      mail = " ".join(args) # email may contain spaces
      if match("^.+@(.+\..{2,}|\[[0-9a-fA-F:.]+\])$", mail) != None:
        token = generate_token(6)
        uuid  = sender.getUniqueId().toString().replace("-", "")
        try:
          mysql_query("DELETE FROM register_tokens WHERE `uuid` = ?", (uuid,), False)
          mysql_query("INSERT INTO register_tokens (`uuid`, `token`, `email`) VALUES (?, ?, ?)", (uuid, token, mail), False)
          msg(sender, "&aToken generated!")
          msg(sender, "&aEmail: &e%s" % mail)
          msg(sender, "&aToken: &e%s" % token)
        except Exception, e:
          error(e)
          msg(sender, "&cError getting your token, please contact an admin!")
      else:
        msg(sender, "&c'&6%s&c' doesn't look like a valid email adress!" % mail)
  else:
    msg(sender, "&cThis is only for players..")



@hook.command("token")
def onCommand(sender, args):
  thread.start_new_thread(token_command, (sender, args, "foo"))
  return True
  
@hook.command("tokengen")
def onCommand(sender, args):
  thread.start_new_thread(tokengen_command, (sender, args, "foo"))
  return True
  
  
  
  
  
  
