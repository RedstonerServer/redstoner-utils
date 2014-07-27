import net.minecraft.server.v1_7_R1.EntityPlayer as EntityPlayer
import net.minecraft.server.v1_7_R1.PacketPlayOutNamedEntitySpawn as PacketPlayOutNamedEntitySpawn
import net.minecraft.server.v1_7_R1.PlayerInteractManager as PlayerInteractManager
import net.minecraft.util.com.mojang.authlib.GameProfile as GameProfile
import org.bukkit.Bukkit as bukkit


# players.txt contains 1 name per line
players = [line.strip() for line in open("players.txt").readlines()]

ground = 70    # sea level
shift  = 1.625 # amount of blocks to add on each side per row (this is for FOV 90)
amount = 6     # amount of players in first row
margin = 1     # space between players
row    = 1     # distance to first row of players
goup   = 6     # after how many rows should we go up by one?
upmul  = 0.95  # multiplicate with goup each row


def spawn(dispname, sender, x, y, z):
  """
  Sends the actual player to sender
  """
  server  = bukkit.getServer().getServer()
  world   = server.getWorldServer(0)                      # main world
  profile = GameProfile(dispname, dispname)               # set player details
  manager = PlayerInteractManager(world)
  entity  = EntityPlayer(server, world, profile, manager) # create Player's entity
  entity.setPosition(x, y, z)
  packet  = PacketPlayOutNamedEntitySpawn(entity)         # create packet for entity spawn
  sender.getHandle().playerConnection.sendPacket(packet)  # send packet


@hook.command("spawnplayer")
def on_spawnplayer_command(sender, args):
  global amount, row, ground, goup

  # X and Z position
  xpos = sender.getLocation().add(-float(row-1 * shift + (amount * margin) / 2), 0, 0).getX()
  row  = sender.getLocation().add(0, 0, -row).getZ()

  count = 0
  stop  = False
  while not stop:
    for i in range(amount):
      player = players[count]
      x = int(xpos + i*margin)
      spawn(player, sender, x, ground, row)
      print(player, x, ground, row)
      count += 1
      if count >= len(players):
        stop = True
        print "breaking"
        break
    print("next row")
    row -= 1                      # next row (-z)
    xpos -= shift                 # shift left
    amount += int(shift*margin*2) # add players left and right
    if abs(row) % int(goup) == 0:
      goup   *= upmul
      ground += 1
      print "Going up by 1: %s" % ground