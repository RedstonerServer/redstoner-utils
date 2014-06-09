__plugin_name__      = "RedstonerUtils"
__plugin_version__   = "3.0"
__plugin_mainclass__ = "foobar"

# damn pythonloader changed the PATH
import sys
sys.path += ['', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-linux2', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages', '/usr/lib/pymodules/python2.7', '/usr/lib/pyshared/python2.7']

try:
  from helpers import log, error
except Exception, e:
  print("[RedstonerUtils] ERROR: Failed to import helpers: %s" % e)

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


@hook.enable
def onEnable():
  log("RedstonerUtils enabled!")

@hook.disable
def onDisable():
  mod["reports"].stopChecking()
  log("RedstonerUtils disabled!")