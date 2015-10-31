from helpers import *
from java.util.UUID import fromString as juuid
import org.bukkit.Material as Material

spawn_world = "Spawn"
punish_world = "Punishments"

slave_perm = "utils.minerslaves"

slaves = []

def save_slaves():
    buf = []
    for slave in slaves:
        buf.append(slave.get_data())
    save_json_file("miner_slaves", buf)

def load_slaves():
    buf = open_json_file("miner_slaves", [])
    for data in buf:
        slave = Slave(True, None, None)
        slave.load_data(data)
        slaves.append(slave)

def get_slave(player):
    for slave in slaves:
        if slave.get_uuid() == player:
            return slave
    return None

class Slave(object):

    def __init__(self, from_file, player, amount):
        if from_file:
            self.players = None
            self.blocks = None
            return
        slave = get_slave(uid(player))
        if slave != None:
            slave.set_blocks(slave.get_blocks() + amount)
        else:
            self.player = uid(player)
            self.blocks = amount
            slaves.append(self)

    def get_uuid(self):
        return self.player

    def get_blocks(self):
        return self.blocks

    def set_blocks(self, amount):
        self.blocks = amount

    def update(self):
        self.blocks -= 1
        if self.blocks <= 0:
            server.getPlayer(juuid(self.get_uuid())).teleport(server.getWorld(spawn_world).getSpawnLocation())
            slaves.remove(self)
            save_slaves()

    def get_data(self):
        return {
        "player": self.player,
        "amount": self.blocks
        }

    def load_data(self, data):
        self.player = str(data["player"])
        self.blocks = int(data["amount"])

load_slaves()

@hook.event("block.BlockBreakEvent", "low")
def event(event):
    if event.getPlayer().getWorld().getName() != punish_world:
        return
    slave = get_slave(uid(event.getPlayer()))
    if slave != None and event.getBlock().getType() == Material.OBSIDIAN:
        slave.update()

@hook.command("miner")
def command(sender, cmd, label, args):
    if not sender.hasPermission(slave_perm):
        noperm(sender)
        return True
    if len(args) == 0 or (len(args) != 1 and args[0] == "list") or (len(args) != 2 and args[0] == "rem") or (len(args) != 3 and args[0] == "add"):
        msg(sender, "&e-&a /miner add/rem/list <name> <amount>")
        return True
    if args[0] == "add":
        try:
            int(args[2])
        except:
            msg(sender, "&cArgument <amount> is not a number")
            return True
    if args[0] == "list":
        if len(slaves) == 0:
            msg(sender, "&e-&a There are no people mining obsidian")
            return True
        for slave in slaves:
            msg(sender, "&e-&a %s: %s blocks" % (server.getOfflinePlayer(juuid(slave.get_uuid())).getName(), slave.get_blocks()))
        return True
    elif args[0] == "add":
        player = server.getOfflinePlayer(str(args[1]))
        if player.isOnline():
            player.teleport(server.getWorld(punish_world).getSpawnLocation())
            Slave(False, player, int(args[2]))
            save_slaves()
            msg(player, "&e-&a You have been punished, mine %s blocks of obsidian to get out!" % args[2])
            msg(sender, "&e-&a Player %s has been added into punishments for %s blocks of obsidian" % (player.getName(), args[2]))
        else:
            msg(sender, "&cYou can only punish online players")
            return True
    elif args[0] == "rem":
        player = server.getOfflinePlayer(str(args[1]))
        if player.isOnline():
            slave = get_slave(uid(player))
            if slave != None:
                server.getPlayer(juuid(slave.get_uuid())).teleport(server.getWorld(spawn_world).getSpawnLocation())
                slaves.remove(slave)
                save_slaves()
            else:
                msg(sender, "&e-&a Player not in punishments")
        else:
            msg(sender, "&cYou can only remove online players")
            return True
    else:
        msg(sender, "&e-&a /miner add/rem/list <name> <amount>")
    return True
