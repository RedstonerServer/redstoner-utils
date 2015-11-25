__plugin_name__      = "RedstonerUtils"
__plugin_version__   = "3.0"
__plugin_mainclass__ = "foobar"

import sys
from traceback import format_exc as print_traceback

# damn pythonloader changed the PATH
sys.path += ['', '/usr/lib/python2.7', '/usr/lib/python2.7/plat-linux2', '/usr/lib/python2.7/lib-tk', '/usr/lib/python2.7/lib-old', '/usr/lib/python2.7/lib-dynload', '/usr/local/lib/python2.7/dist-packages', '/usr/lib/python2.7/dist-packages', '/usr/lib/pymodules/python2.7', '/usr/lib/pyshared/python2.7']

try:
    # Library that adds a bunch of re-usable methods which are used in nearly all other modules
    from helpers import *
    from wrapper import *
except:
    print("[RedstonerUtils] ERROR: Failed to import Wrapper:")
    print(print_traceback())



@hook.enable
def on_enable():
    info("RedstonerUtils enabled!")


@hook.disable
def on_disable():
    #shared["modules"]["reports"].stop_reporting()
    info("RedstonerUtils disabled!")


info("Loading RedstonerUtils...")



# Import all modules, in this order
shared["load_modules"] = ["test", "login"]

shared["modules"] = {}
for module in shared["load_modules"]:
    try:
        shared["modules"][module] = __import__(module)
        info("Module %s loaded." % module)
    except:
        error("Failed to import module %s:" % module)
        error(print_traceback())
