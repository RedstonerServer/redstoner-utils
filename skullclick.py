#pylint: disable = F0401
import org.bukkit as bukkit
from helpers import msg

@hook.event("player.PlayerInteractEvent", "monitor")
def on_block_interact(event):
    if (str(event.getAction()) == "RIGHT_CLICK_BLOCK"):
        sender = event.getPlayer()
        block  = event.getClickedBlock().getState()
        if (isinstance(block, bukkit.block.Skull) and not event.isCancelled()):
            owner = block.getOwner()
            if (owner):
                msg(sender, "&eThat's %s." % owner)
            else:
                msg(sender, "&cThis skull has no name (Steve)")
            event.setCancelled(True)
