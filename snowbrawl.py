#Snowbrawl
from helpers import *

arenas = {}

"""
ArenaName
PlayersPerGame
Objective
PlayersInQue
"""

@hook.event("entity.ProjectileHitEvent", "high")
def onHit(event):
    print "thrown"
    if event.getEntity().getType() != EntityType.SNOWBALL:
        print "Not a snowball?"
        return
    if event.getEntity().getWorld().getName() != "minigames":
        print "Not in minigames"
        return
    print "all good."
    event.getEntity().getWorld().createExplosion(event.getEntity().getLocation(),1)

        

@hook.event("PlayerInteractEvent")
def onClick(event):
    if (event.getAction() != Action.RIGHT_CLICK_BLOCK):
        return
    block = event.getClickedBlock()
    if not block.getMaterial() in [Material.SIGN_POST, Material.WALL_SIGN]:
        return
    sign_state = block.getState()
    lines      = bukkit.block.Sign.getLines(sign_state)
    

"""
class Queue(Object):
    
    queue = []
    
    def __init__(self):

    def add(name):
        queue.append(name)
    def rem(names):
        for name in names:
            queue.remove(name)
    def shrink():
        queue.remove(0)
        
class Arena(Object):

    queue = Queue()
    size = 0
    coordinate = Coordinate(0, 0)

    def __init__(self, coordinate, size):
        self.coordinate = coordinate
        self.size = size

    def getLocation():
        return coordinate
    def getSize():
        return size
    def getQueue():
        return queue

class Coordinate(Object):

    x = 0
    z = 0

    def __init__(self, x, z):
        self.x = x
        self.z = z

    def getX():
        return x
    def getZ():
        return z

    def inRange(location, range):
        xd = location.getBlockX() - getX()
        zd = location.getBlockZ() - getZ()
        return xd >= 0 and xd <= range_ and zd >= 0 and zd <= range_
class Match(Object):

    names = []

    def __init__(self, ):
def getArena(location):
    for name in arenas:
        arena = arenas.get(name)
        if arena.getLocation().inRange(location, arena.getSize() - 1)
            return arena
    return None
"""