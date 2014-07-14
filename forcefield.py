from helpers import *

forcefield_permission = "utils.forcefield"
forcefield_prefix = "&8[&aFF&8]"
fd = 4 # forcefield distance

forcefield_toggle = []

#forcefield toggle
@hook.command("forcefield")
def onActCommand(sender, args):
  if not sender.hasPermission(forcefield_permission):
    noperm(sender)
    return True
  UUID = str(sender.getUniqueId())
  if UUID in forcefield_toggle:
    forcefield_toggle.remove(UUID)
    msg(sender, "%s &aForceField toggle: &cOFF" % forcefield_prefix)
  else:
    forcefield_toggle.append(UUID)
    msg(sender, "%s &aForceField toggle: &2ON" % forcefield_prefix)
  return True


@hook.event("player.PlayerMoveEvent")
def onMove(event):
  player = event.getPlayer()
  if not player.hasPermission(forcefield_permission):
    for entity in player.getNearbyEntities(fd, fd, fd):
      if isPlayer(entity) and str(entity.getUniqueId()) in forcefield_toggle:
        event.setCancelled(True)
        msg(sender, "%s &cYou are not allowed to get closer than %sm to %s" % (forcefield_prefix, fd, entity.getDisplayName()))
        break



