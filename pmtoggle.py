from helpers import *
import org.bukkit.Bukkit as Bukkit

toggle_list = {}
permission = "utils.pmtoggle"

@hook.command("tm")
def on_toggle_message_command(sender, args):
    name = sender.getName()
    if not sender.hasPermission(permission) or name == "CONSOLE":
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
            toggle_list[uuid] = uid(target)
            msg(sender, "&2Enabled toggle so that you're now sending only to %s &2by default" % target.getDisplayName())
        else:
            msg(sender, "&cThat player could not be found")
    else if uuid in toggle_list:
        del toggle_list[uuid]
        msg(sender, "&2Disabled toggle successfully")
    else:
        msg(sender, "&cExpected a player as argument")
    return True

@hook.event("Player.AsyncPlayerChatEvent", "normal")
def on_chat(event):
    player = event.getPlayer()
    uuid = uid(player)
    if uuid in toggle_list:
        event.setCancelled(True)
        target = Bukkit.getPlayer(toggle_list[uuid]).getName()
        runas(player, "msg %s %s" % (target, event.getMessage()))


@hook.event("Player.PlayerQuitEvent", "normal")
def on_quit(event):
    uuid = uid(event.getPlayer())
    if uuid in toggle_list:
        del toggle_list[uuid]
    for pid in toggle_list:
        if toggle_list[pid] == uuid:
            del toggle_list[pid]
            msg(Bukkit.getPlayer(pid), "%s &cwent off so your Private Message Toggle has been disabled!" % Bukkit.getPlayer(uuid).getDisplayName())

