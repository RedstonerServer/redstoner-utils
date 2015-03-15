from helpers import *
import org.bukkit.Bukkit as Bukkit
from java.util.UUID import fromString as juuid

toggle_dict = {}
permission = "utils.pmtoggle"

@hook.command("tm")
def on_toggle_message_command(sender, args):
    if not sender.hasPermission(permission) or not is_player(sender):
        noperm(sender)
        return True
    plugin_header(sender, "Private Message Toggle")
    uuid = uid(sender)
    if len(args) > 0:
        if len(args) > 1:
            msg(sender, "&cToo many arguments!")
            return True
        target = Bukkit.getPlayer(args[0])
        if target:
            toggle_dict[uuid] = uid(target)
            msg(sender, "&2Enabled toggle so that you're now sending only to %s &2by default" % target.getDisplayName())
        else:
            msg(sender, "&cThat player could not be found")
    elif uuid in toggle_dict:
        del toggle_dict[uuid]
        msg(sender, "&2Disabled toggle successfully")
    else:
        msg(sender, "&cExpected a player as argument")
    return True


@hook.event("player.AsyncPlayerChatEvent", "normal")
def on_chat(event):
    if event.isCancelled():
        return
    player = event.getPlayer()
    uuid = uid(player)
    if uuid in toggle_dict:
        event.setCancelled(True)
        target = Bukkit.getPlayer(juuid(toggle_dict[uuid])).getName()
        runas(player, "msg %s %s" % (target, event.getMessage()))


@hook.event("player.PlayerQuitEvent", "normal")
def on_quit(event):
    uuid = uid(event.getPlayer())
    if uuid in toggle_dict:
        del toggle_dict[uuid]
    for pid in toggle_dict:
        if toggle_dict[pid] == uuid:
            del toggle_dict[pid]
            msg(Bukkit.getPlayer(juuid(pid)), "%s &cwent off so your Private Message Toggle has been disabled!" % Bukkit.getPlayer(juuid(uuid)).getDisplayName())