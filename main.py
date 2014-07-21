__plugin_name__      = "RedstonerUtils"
__plugin_version__   = "3.0"
__plugin_mainclass__ = "foobar"

import sys
from traceback import format_exc as print_traceback

# damn pythonloader changed the PATH
sys.path += ['', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-linux2', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages', '/usr/lib/pymodules/python2.7', '/usr/lib/pyshared/python2.7']

try:
  from helpers import *
except:
  print("[RedstonerUtils] ERROR: Failed to import helpers:")
  print(print_traceback())



@hook.enable
def on_enable():
  log("RedstonerUtils enabled!")


@hook.disable
def on_disable():
  shared["modules"]["reports"].stop_reporting()
  log("RedstonerUtils disabled!")


log("Loading RedstonerUtils...")

# Import all modules, in this order
shared["load_modules"] = [
  "misc",
  "adminchat",
  "lagchunks",
  "reports",
  "chatgroups",
  "webtoken",
  "saylol",
  "skullclick",
  "mentio",
  "cycle",
  "motd",
  "abot",
  "forcefield"
]
shared["modules"] = {}
for module in shared["load_modules"]:
  try:
    shared["modules"][module] = __import__(module)
    log("Module %s loaded." % module)
  except:
    error("Failed to import module %s:" % module)
    error(print_traceback())