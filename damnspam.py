#pylint: disable=F0401
from helpers import *
import json

spam_filename = "plugins/redstoner-utils.py.dir/files/damnspam.json"
inputs = []
accepted_inputs = ["WOOD_BUTTON", "STONE_BUTTON"]

try:
  inputs = json.loads(open(spam_filename).read())
except Exception, e:
  error("Failed to load buttons and levers: %s" % e)


@hook.command("damnspam")
def onTimeoutCommand(sender, args):
  global inputs
  try:
    plugHeader(sender, "DamnSpam")
    if len(args) == 1:
      timeout = args[0]
      if not timeout.isdigit():
        msg(sender, "&cThe timeout has to be a digit.")
        return True
      tB = sender.getTargetBlock(None, 10)
      if str(tB.getType()) not in accepted_inputs:
        msg(sender, "&cPlease look at a button/lever while executing this command!")
        return True
      data = {
        "type": str(tB.getType()),
        "creator": str(sender.getUniqueId()),
        "timeout": int(args[0]),
        "x": int(tB.getX()),
        "y": int(tB.getY()),
        "z": int(tB.getZ()),
        "next": 'NULL',
        "last": 'NULL'
      }
      inputs.append(data)
      saveInputs()
      msg(sender, "&eSuccessfully set a timeout for this button")
      return True
    else:
      msg(sender, "&c/timeout <seconds>")
  except Exception, e:
    error(e)

def saveInputs():
  try:
    spam_file = open(spam_filename, "w")
    spam_file.write(json.dumps(inputs))
    spam_file.close()
  except Exception, e:
    error("Failed to save buttons and levers: " + str(e))

@hook.event("block.BlockBreakEvent", "normal")
def onBreak(event):
  try:
    sender = event.getPlayer()
    block = event.getBlock()
    if str(block.getType()) in accepted_inputs:
      for entry in inputs:
        posX = int(entry["x"])
        posY = int(entry["y"])
        posZ = int(entry["z"])
        posX2 = block.getX()
        posY2 = block.getY()
        posZ2 = block.getZ()
        if posX == posX2 and posY == posY2 and posZ == posZ2:
          if sender.isSneaking():
            inputs.remove(entry)
            saveInputs()
            msg(sender, "&eSuccessfully removed the input!")
            return True
          else:
            event.setCancelled(True)
            msg(sender, "&cYou cannot destroy this input!")
            msg(sender, "&7&lSneak&7 and break if you want to remove it.")
            return True
          break
  except Exception, e:
    error("BlockBreakEvent failed: " + str(e))