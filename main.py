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
except:
    print("[RedstonerUtils] ERROR: Failed to import helpers:")
    print(print_traceback())

def getDefaultWorldGenerator(world_name, ID):
    return shared["modules"]["plotgen"].get_generator()

@hook.enable
def on_enable():
    info("RedstonerUtils enabled!")


@hook.disable
def on_disable():
    shared["modules"]["reports"].stop_reporting()
    info("RedstonerUtils disabled!")


info("Loading RedstonerUtils...")

# Import all modules, in this order
shared["load_modules"] = [
    # Collection of tiny utilities
    "misc",
    # Adds chat for staff using /ac <text or ,<text>
    "adminchat",
    # Adds /badge, allows to give players achievements
    "badges",
   	# Adds a few block placement corrections/mods
   	"blockplacemods",
    # Adds /calc, toggles automatic solving of Math expressions in chat
    "calc",
    # Plugin to locate laggy chunks. /lc <n> lists chunks with more than n entities
    "lagchunks",
    # Adds /report and /rp, Stores reports with time and location
    "reports",
    # Adds group-chat with /chatgroup and /cgt to toggle normal chat into group mode
    "chatgroups",
    # Adds /token, reads and writes from the database to generate pronouncable (and thus memorable) registration-tokens for the website
    "webtoken",
    # Adds /lol, broadcasts random funyy messages. A bit like the splash text in the menu
    "saylol",
    # Shows the owner of a skull when right-clicked
    "skullclick",
    # Adds /listen, highlights chat and plays a sound when your name was mentioned
    "mentio",
    # Adds /cycler, swaps the hotbar with inventory when player changes slot from right->left or left->right
    "cycle",
    # Adds /getmotd & /setmotd to update the motd on the fly (no reboot)
    "motd",
    # AnswerBot. Hides stupid questions from chat and tells the sender about /faq or the like
    "abot",
    # Adds '/forcefield', creates forcefield for players who want it.
    "forcefield",
    # Adds /damnspam, creates timeout for buttons/levers to mitigate button spam.
    "damnspam",
    # Adds /check, useful to lookup details about a player
    "check",
    # Adds /an, a command you can use to share thoughts/plans/news
    "adminnotes",
    # Adds /imout, displays fake leave/join messages
    "imout",
    #adds snowbrawl minigame
    "snowbrawl",
    # Adds /tm [player] for a messages to be sent to this player via /msg
    "pmtoggle",
    # Replacement for LoginSecurity
    "loginsecurity",
    # Centralized Player class
    "playermanager",
    # Plot generator
    "plotgen"
]
shared["modules"] = {}
for module in shared["load_modules"]:
    try:
        shared["modules"][module] = __import__(module)
        info("Module %s loaded." % module)
    except:
        error("Failed to import module %s:" % module)
        error(print_traceback())
