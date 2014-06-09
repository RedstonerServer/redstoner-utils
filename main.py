__plugin_name__      = "RedstonerUtils"
__plugin_version__   = "3.0"
__plugin_mainclass__ = "foobar"

import sys
import thread

# damn pythonloader changed the PATH
sys.path += ['', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-linux2', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages', '/usr/lib/pymodules/python2.7', '/usr/lib/pyshared/python2.7']

try:
  from helpers import *
except Exception, e:
  print("[RedstonerUtils] ERROR: Failed to import helpers: %s" % e)



@hook.enable
def onEnable():
  log("RedstonerUtils enabled!")


@hook.disable
def onDisable():
  mod["reports"].stopChecking()
  log("RedstonerUtils disabled!")


log("Loading RedstonerUtils...")

# Import all modules
modules = ["misc", "adminchat", "lagchunks", "reports", "chatgroups", "webtoken", "saylol", "skullclick", "tilehelper"]
mod = {}
for module in modules:
  try:
    mod[module] = __import__(module)
    log("Module %s loaded." % module)
  except Exception, e:
    error("Failed to import module %s: '%s'" % (module, e))



#
# /pyeval - run python ingame
#
# has to be in main.py so we can access the modules

def evalThread(sender, code):
  try:
    msg(sender, "%s" % unicode(eval(code)), False, "a")
  except Exception, e:
    msg(sender, "%s: %s" % (e.__class__.__name__, e), False, "c")
  thread.exit()

@hook.command("pyeval")
def onPyevalCommand(sender, args):
  if sender.hasPermission("utils.pyeval"):
    if not checkargs(sender, args, 1, -1):
      return True
    msg(sender, "%s" % " ".join(args), False, "e")
    try:
      thread.start_new_thread(evalThread, (sender, " ".join(args)))
    except Exception, e:
      msg(sender, "&cInternal error: %s" % e)
  else:
    noperm(sender)
  return True