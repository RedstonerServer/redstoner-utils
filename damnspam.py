#pylint: disable = F0401
from helpers import *
from time import time as now
import org.bukkit.event.block.BlockBreakEvent as BlockBreakEvent
import json

spam_filename   = "plugins/redstoner-utils.py.dir/files/damnspam.json"
inputs          = {} # format "x;y;z;World"
accepted_inputs = ["WOOD_BUTTON", "STONE_BUTTON", "LEVER"]

try:
  inputs = json.loads(open(spam_filename).read())
except Exception, e:
  error("Failed to load buttons and levers: %s" % e)


def save_inputs():
  try:
    spam_file = open(spam_filename, "w")
    spam_file.write(json.dumps(inputs))
    spam_file.close()
  except Exception, e:
    error("Failed to save damnspam: " + str(e))


def location_str(block):
  return ";".join([block.getWorld().getName(), str(block.getX()), str(block.getY()), str(block.getZ())])


def add_input(creator, block, timeout_off, timeout_on):
  global inputs
  inputs[location_str(block)] = {
    "creator"     : str(creator.getUniqueId()),
    "timeout_off" : timeout_off,
    "timeout_on"  : timeout_on,
    "last_time"   : 0
  }


@hook.command("damnspam")
def on_dammnspam_command(sender, args):
  global inputs

  plugin_header(sender, "DamnSpam")
  if len(args) in [1,2]:

    if not str(sender.getGameMode()) == "CREATIVE":
      msg(sender, "&cYou can only do this in Creative mode.")
      return True

    # /damnspam <secs>
    if len(args) == 1:
      timeout_on = args[0]
      try:
        timeout_on  = round(float(timeout_on), 2)
        timeout_off = timeout_on
        if not 0 <= timeout_on <= 60:
          msg(sender, "&cThe timeout must be within 0-60.")
          return True
      except ValueError:
        msg(sender, "&cThe timeout must be a number")
        return True

    # /damnspam <off> <on>
    elif len(args) == 2:
      timeout_on  = args[0]
      timeout_off = args[1]
      try:
        timeout_on  = round(float(timeout_on), 2)
        timeout_off = round(float(timeout_off), 2)
        if not 0 <= timeout_on <= 60 or not 0 <= timeout_off <= 60:
          msg(sender, "&cThe timeout must be within 0-60.")
          return True
      except ValueError:
        msg(sender, "&cThe timeout must be a number")
        return True

    # get the block we're looking at
    target = sender.getTargetBlock(None, 10)
    ttype  = str(target.getType())
    if ttype not in accepted_inputs:
      msg(sender, "&cPlease look at a button or lever while executing this command!")
      return True

    test_event = BlockBreakEvent(target, sender)
    server.getPluginManager().callEvent(test_event)
    if test_event.isCancelled():
      msg(sender, "&cYou are not allowed to modify this button")
      return True

    # add block to inputs
    add_input(sender, target, timeout_off, timeout_on)
    save_inputs()
    msg(sender, "&aSuccessfully set a timeout for this %s." % ttype.lower())
    return True

  else:
    msg(sender, "&c/damnspam <seconds> &e(Buttons/Levers)")
    msg(sender, "&c/damnspam <seconds after off> <seconds after on> &e(Levers only)")


@hook.event("block.BlockBreakEvent", "normal")
def on_block_break(event):
  global inputs

  sender = event.getPlayer()
  block = event.getBlock()
  if str(block.getType()) in accepted_inputs and not event.isCancelled():
    pos_str = location_str(block)
    if inputs.get(pos_str):
      plugin_header(sender, "DamnSpam")
      if sender.isSneaking():
        inputs.pop(pos_str) # remove
        save_inputs()
        msg(sender, "&eSuccessfully removed the input!")
        return True
      else:
        event.setCancelled(True)
        msg(sender, "&cYou cannot destroy this input!")
        msg(sender, "&c&nSneak&c and break if you want to remove it.")
        return True


@hook.event("player.PlayerInteractEvent", "normal")
def on_interact(event):
  if (str(event.getAction()) == "RIGHT_CLICK_BLOCK") and not event.isCancelled():
    sender  = event.getPlayer()
    block   = event.getClickedBlock()
    btype   = str(block.getType()).lower()
    powered = (block.getData() & 0x8) == 0x8 if btype == "lever" else False # data > 7, but this is how bukkit does it
    pos_str = location_str(block)
    data    = inputs.get(pos_str)
    if data:
      checktime = data["timeout_on"] if powered else data["timeout_off"]
      if data["last_time"] + checktime > now():
        event.setCancelled(True)
        plugin_header(sender, "DamnSpam")
        msg(sender, "&cThis %s has a timeout of %ss." % (btype, checktime))
      else:
        inputs[pos_str]["last_time"] = round(now(), 2)