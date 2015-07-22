#Snowbrawl
from helpers import *
import time, threading, copy
import org.bukkit.inventory.ItemStack as ItemStack
import org.bukkit.Material as Material
import org.bukkit.potion.PotionEffect as PotionEffect
import org.bukkit.potion.PotionEffectType as PotionEffectType
from java.lang import Runnable
from java.util.UUID import fromString as juuid
from operator import __contains__
from traceback import format_exc as trace
import random
from synchronize import make_synchronized

#file names
file = "snowbrawl"

#permissions
list_perm = "utils.snowbrawl.list"
modify_perm = "utils.snowbrawl.modify"
teleport_perm = "utils.snowbrawl.tp"
create_perm = "utils.snowbrawl.create"
info_perm = "utils.snowbrawl.info"
join_perm = "utils.snowbrawl.join"
quit_perm = "utils.snowbrawl.quit"

#commands - tp command does not exist
list_command = "list"
del_command = "del"
set_command = "set"
name_command = "name"
pos_command = "pos"
create_command = "create"
info_command = "info"
modify_command = "modify"
modify_command_alias = "m"
quit_command = "quit"



class Arena(object):

    def __init__(self, name):
        self.queue = Queue()
        self.name = name
        self.refill = None
        self.player_limit = None
        self.start_time = None
        self.match_goal = None # amount of deaths or time until the match ends (depends on arena_type)
        self.arena_type = None # arena type (death or time)
        self.explosion_damage = None
        
        self.player_stats = {}
        self.players = Queue()
        self.spawn_location = []
        self.respawn_location = []
        self.sign_location = []
        self.sign_click = []

        self.corner1 = None # The corner1 given by the player (really bad for 3D position compare)
        self.corner2 = None # The corner2 given by the player (really bad for 3D position compare)
        self.tpp = None # The top, positive x, positive z corner
        self.bnn = None # The bottom, negative x, negative z corner     

    #set corners of arena
    def set_corner(self, sender, type):
        loc = sender.getLocation()
        if type == "1":
            self.corner1 = Coords(loc)
        elif type == "2":
            self.corner2 = Coords(loc)
        msg(sender, "&a-&e Arena corner %s set" % type)
        self.update_corner_points()

    #Compares the corner1 and corner2 locations and figures out tpp and bnn so that we dont have to do it everytime we run in_arena()
    def update_corner_points(self):
        self.tpp = None
        self.bnn = None                                                    
        if self.corner1 == None or self.corner2 == None:
            return
        corn1 = self.corner1.get_location()
        corn2 = self.corner2.get_location()
        if not corn1.getWorld().getName() == corn2.getWorld().getName():
            return
        
        top = corn1.y if corn1.y > corn2.y else corn2.y
        bottom = corn1.y if corn1.y < corn2.y else corn2.y
        pos_x = corn1.x if corn1.x > corn2.x else corn2.x
        pos_z = corn1.z if corn1.z > corn2.z else corn2.z
        neg_x = corn1.x if corn1.x < corn2.x else corn2.x
        neg_z = corn1.z if corn1.z < corn2.z else corn2.z
        
        self.tpp = Coords(corn1.getWorld(), pos_x, top, pos_z, 0, 0)
        self.bnn = Coords(corn2.getWorld(), neg_x, bottom, neg_z, 0, 0)

    #add sign to sign list
    def add_sign(self, sender, name):
        mats = set()
        mats = None
        block = sender.getTargetBlock(mats, 3).getState()
        if isinstance(block, bukkit.block.Sign):
            self.sign_click.append(NamedCoords(name, Coords(block.getLocation())))
            msg(sender, "&a-&e Arena tp sign %s created and set" % name)

    #Delete a sign from the sign list
    def del_sign(self, sender, name):
        for sign in self.sign_click:
            if sign.get_name() == name:
                self.sign_click.remove(sign)
                msg(sender, "&a-&e Arena tp sign %s removed" % sign.get_name())
                return
        msg(sender, "&a-&e Arena tp sign with this name doesn't exist")

    #Adds a player to the queue if they aren't already there.
    def add_player(self, player):
        if not self.queue.contains(player):
            self.queue.put(player)
            self.start_match()
            return True
        return False
    
    #remove a player from the queue
    def remove_player(self, player):        
        if self.queue.contains(player):
            self.queue.remove(player)
            return True
        return False

    #return true if loc is inside the arena boundries
    def in_arena(self, loc):
        if self.tpp == None or self.bnn == None:
            return False
        loc_tpp = self.tpp.get_location()
        loc_bnn = self.bnn.get_location()
        
        if loc.y > loc_tpp.y:
            return False
        if loc.y < loc_bnn.y:
            return False
        if loc.x > loc_tpp.x:
            return False
        if loc.x < loc_bnn.x:
            return False
        if loc.z > loc_tpp.z:
            return False
        if loc.z < loc_bnn.z:
            return False
        return True

    def get_respawn(self):
        id = random.randint(0, len(self.respawn_location) - 1)
        return self.respawn_location[id]


    def spawn_player(self, player):
        id = random.randint(0, len(self.spawn_location) - 1)
        loc = self.spawn_location[id].get_location().get_location()
        safetp(player, loc.getWorld(), loc.x, loc.y, loc.z, loc.yaw, loc.pitch)

    #Start match
    def start_match(self):
        if self.player_limit == None or self.match_goal == None or self.arena_type == None or len(self.spawn_location) == 0 or len(self.respawn_location) == 0 or len(self.sign_location) == 0:
            return
        if len(self.queue.read()) >= self.player_limit and len(self.players.read()) == 0:
            self.start_time = time.time()
            for i in range(self.player_limit):
                player = self.queue.get()
                self.players.put(player)
            for player in self.players.read():
                self.player_stats[player.getName() + "_deaths"] = 0
                self.spawn_player(player)
                msg(player, "&6The match has started!")

    def bubbleSort(self, alist):
        for passnum in range(len(alist)-1,0,-1):
            for i in range(passnum):
                if self.player_stats[alist[i].getName()+"_deaths"]>self.player_stats[alist[i+1].getName()+"_deaths"]:
                    temp = alist[i]
                    alist[i] = alist[i+1]
                    alist[i+1] = temp
        return alist
    
    @make_synchronized #Jython synchronized block
    def end_match(self): #End match, sort the players and print the 3 players with least amount of deaths
        
        sorted_list = self.bubbleSort(self.players.read())
        
        for player in self.players.read():
            if player.isOnline():
                loc = self.sign_location[0].get_location().get_location()
                safetp(player, loc.getWorld(), loc.x, loc.y, loc.z, loc.yaw, loc.pitch)
                msg(player, "&6================= Match over =================")
                msg(player, "&c&c")
                if not len(sorted_list) < 1:
                    msg(player, "&e1. %s (%s)" % (sorted_list[0].getName(), self.player_stats[sorted_list[0].getName()+"_deaths"]))
                if not len(sorted_list) < 2:
                    msg(player, "&e2. %s (%s)" % (sorted_list[1].getName(), self.player_stats[sorted_list[1].getName()+"_deaths"]))
                if not len(sorted_list) < 3:
                    msg(player, "&e3. %s (%s)" % (sorted_list[2].getName(), self.player_stats[sorted_list[2].getName()+"_deaths"]))
                msg(player, "&c&c")
                msg(player, "&e Your deaths:&6 %s" % str(self.player_stats[player.getName() + "_deaths"]))
                msg(player, "&c&c")
                msg(player, "&6==============================================")
        self.players.clear()
        self.player_stats = {}
        self.start_match()

    def check_deaths(self):
        if self.arena_type == "death":
            for player in self.players.read():
                if self.player_stats[player.getName() + "_deaths"] >= self.match_goal:
                    return True
        return False

    def is_running(self):
        if len(self.players.read()) == 0:
            return False
        return True

    def set_explosion_damage(self, dmg):
        self.explosion_damage = dmg

    def get_explosion_damage(self):
        if self.explosion_damage == None:
            return 1
        return self.explosion_damage

    def in_players(self, player):
        return self.players.contains(player)

    def set_player_limit(self, limit):
        self.player_limit = limit

    def set_end_goal(self, value):
        self.match_goal = value

    def set_type(self, type):
        self.arena_type = type

    def get_name(self):
        return self.name

    def set_refill(self, amount):
        self.refill = int(amount)

    def set_name(self, name):
        self.name = name

    def get_refill(self):
        if self.refill == None:
            return 16
        return self.refill

    def get_tp_signs(self):
        return self.sign_location

    def get_click_signs(self):
        return self.sign_click
    
    #Check if player is in the queue
    def in_queue(self,player):
        if self.queue.contains(player):
            return True
        return False

    #Returns queue contents in list. use "".join(queue) to get a string
    def get_queue_contents(self):
        return self.queue.read()
    #Returns queue object
    def get_queue(self):
        return self.queue

    #Returns list of location objects of type, type.
    def get_location(self, type):
        if type == "spawn":
            return self.spawn_location
        elif type == "respawn":
            return self.respawn_location
        elif type == "sign":
            return self.sign_location

    #Add a location to list of type location
    def add_location(self, name, location, type):
        named_loc = NamedCoords(name, Coords(location))
        if type == "spawn":
            self.spawn_location.append(named_loc)
        elif type == "respawn":
            self.respawn_location.append(named_loc)
        elif type == "sign":
            self.sign_location.append(named_loc)

    #Change location of location of type, type
    def change_location(self, name, location, type):
        if type == "spawn":
            for spawn in self.spawn_location:
                if spawn.get_name() == name:
                    spawn.get_location().set_location(location)
                    break
        elif type == "respawn":
            for respawn in self.respawn_location:
                if respawn.get_name() == name:
                    respawn.get_location().set_location(location)
                    break
        elif type == "sign":
            for sign in self.sign_location:
                if sign.get_name() == name:
                    sign.get_location().set_location(location)
                    break

    #Remove location out of location 
    def delete_location(self, name, type):
        if type == "spawn":
            for spawn in self.spawn_location[:]:
                if spawn.get_name() == name:
                    self.spawn_location.remove(spawn)
                    break
        elif type == "respawn":
            for respawn in self.respawn_location[:]:
                if respawn.get_name() == name:
                    self.respawn_location.remove(respawn)
                    break
        elif type == "sign":
            for sign in self.sign_location[:]:
                if sign.get_name() == name:
                    self.sign_location.remove(sign)
                    break

    def get_data(self):
        spawns = []
        for spawn in self.spawn_location:
            spawns.append(spawn.get_data())
        respawns = []
        for respawn in self.respawn_location:
            respawns.append(respawn.get_data())
        signs = []
        for sign in self.sign_location:
            signs.append(sign.get_data())
        sign_clicks = []
        for click in self.sign_click:
            sign_clicks.append(click.get_data())
        corners = []
        corners.append(self.corner1.get_data() if not self.corner1 == None else None)
        corners.append(self.corner2.get_data() if not self.corner2 == None else None)
        corners.append(self.tpp.get_data() if not self.tpp == None else None)
        corners.append(self.bnn.get_data() if not self.bnn == None else None)
        data = {
        "spawns": spawns,
        "respawns": respawns,
        "signs": signs,
        "clicks": sign_clicks,
        "corners": corners,
        "explosion": self.explosion_damage,
        "players": self.player_limit,
        "refill": self.refill,
        "type": self.arena_type,
        "goal": self.match_goal,
        "name": self.name
        }
        return data

    def load(self, data):
        self.explosion_damage = float(data["explosion"])
        self.player_limit = int(data["players"])
        self.refill = int(data["refill"])
        self.arena_type = str(data["type"])
        self.match_goal = int(data["goal"])
        self.corner1 = Coords(None).load(data["corners"][0]) if not data["corners"][0] == None else None
        self.corner2 = Coords(None).load(data["corners"][1]) if not data["corners"][1] == None else None
        self.tpp = Coords(None).load(data["corners"][2]) if not data["corners"][2] == None else None
        self.bnn = Coords(None).load(data["corners"][3]) if not data["corners"][3] == None else None
        for subdata in data["spawns"]:
            self.spawn_location.append(NamedCoords(None, None).load(subdata))
        for subdata in data["respawns"]:
            self.respawn_location.append(NamedCoords(None, None).load(subdata))
        for subdata in data["signs"]:
            self.sign_location.append(NamedCoords(None, None).load(subdata))
        for subdata in data["clicks"]:
            self.sign_click.append(NamedCoords(None, None).load(subdata))
        self.name = data["name"]
        return self

#coord = an instance of Coords class, adds a name to it.
class NamedCoords(object):

    def __init__(self, name, coord):
        self.name = name
        self.coord = coord

    def get_name(self):
        return self.name

    def get_location(self):
        return self.coord

    def get_data(self):
        coords = self.coord.get_location()
        data = {
        "x": coords.x,
        "y": coords.y,
        "z": coords.z,
        "yaw": coords.yaw,
        "pitch": coords.pitch,
        "world": coords.getWorld().getName(),
        "name": self.name
        }
        return data

    def load(self, data):
        self.name = str(data["name"])
        self.coord = Coords(None).load(data)
        return self

class Coords(object):

    def __init__(self, world = None, x = None, y = None, z = None, yaw = None, pitch = None):
        if world == None:
            self.world = None
            self.x = None
            self.y = None
            self.z = None
            self.yaw = None
            self.pitch = None
            return
        if not isinstance(world, Location):
            self.x = x
            self.y = y
            self.z = z
            self.yaw = yaw
            self.pitch = pitch
            self.world = world.getName()
        else:
            location = world
            self.x = location.x
            self.y = location.y
            self.z = location.z
            self.yaw = location.yaw
            self.pitch = location.pitch
            self.world = location.getWorld().getName()

    def get_location(self):
        return Location(server.getWorld(str(self.world)), float(self.x), float(self.y), float(self.z), int(self.yaw), int(self.pitch))

    def set_location(self, location):
        self.x = location.x
        self.y = location.y
        self.z = location.z
        self.yaw = location.yaw
        self.pitch = location.pitch
        self.world = location.getWorld().getName()

    def get_data(self):
        data = {
        "x": self.x,
        "y": self.y,
        "z": self.z,
        "yaw": self.yaw,
        "pitch": self.pitch,
        "world": self.world
        }
        return data

    def load(self, data):
        self.x = float(data["x"])
        self.y = float(data["y"])
        self.z = float(data["z"])
        self.yaw = int(data["yaw"])
        self.pitch = int(data["pitch"])
        self.world = str(data["world"])
        return self

class Queue(object):

    def __init__(self):
        self.queue = []
    
    #Appends to queue
    def put(self,args):
        self.queue.append(args)
    
    #Returns the first item in the queue and removes it
    def get(self):
        if len(self.queue) > 0:
            return self.queue.pop(0)
    
        else:
            return False

    #Returns the queue's list object
    def read(self):
        return self.queue

    #Removes the value args from the queue
    def remove(self,args):
        self.queue.remove(args)

    #Check if queue contains player
    def contains(self, player):
        if player in self.queue:
            return True
        return False
    
    #Clear the queue
    def clear(self):
        self.queue = []

##############################################################################################
# Initialization
##############################################################################################

def save_snowbrawl():
    out = []
    for arena in arenas:
        out.append(arena.get_data())
    save_json_file(file, out)

def load_snowbrawl():
    out = []
    buffer = open_json_file(file, [])
    for data in buffer:
        out.append(Arena(None).load(data))
    return out

arenas = load_snowbrawl()

##############################################################################################
# Threads
##############################################################################################

class timings_runnable(Runnable):

    def __init__(self, arena):
        self.arena = arena

    def run(self):
        self.arena.end_match()        

#timings thread to end arenas if their type is time
def timings():
    while True:
        for arena in arenas:
            if arena.is_running():
                if arena.arena_type == "time":
                    current_time = time.time()
                    start_time = arena.start_time
                    if arena.start_time + arena.match_goal < current_time:
                        timing = timings_runnable(arena)
                        server.getScheduler().runTask(server.getPluginManager().getPlugin("RedstonerUtils"), timing)
   
        time.sleep(0.1)

    
timingsThread = threading.Thread(target = timings)
timingsThread.daemon = True #Thread dies if main thread dies
timingsThread.start()





##############################################################################################
# Events
##############################################################################################

@hook.event("player.PlayerMoveEvent", "high")
def onMove(event):
    if event.getPlayer().getWorld().getName() != "minigames":
        return
    player = event.getPlayer()
    for arena in arenas:
        if arena.in_players(player):
            loc = player.getLocation()
            block = player.getWorld().getBlockAt(int(loc.x), int(loc.y) - 1, int(loc.z))
            if block != None:
                material = block.getType()
                if material == Material.SPONGE:
                    player.addPotionEffect(PotionEffect(PotionEffectType.JUMP, 60, 0))
                elif material == Material.GLASS or material == Material.STAINED_GLASS:
                    player.addPotionEffect(PotionEffect(PotionEffectType.SPEED, 60, 0))
                elif material == Material.OBSIDIAN:
                    player.addPotionEffect(PotionEffect(PotionEffectType.DAMAGE_RESISTANCE, 300, 0))
            break

@hook.event("entity.PlayerDeathEvent", "high")
def onDeath(event):
    if event.getEntity().getWorld().getName() != "minigames":
        return
    if not isinstance(event.getEntity(), bukkit.entity.Player):
        return
    for arena in arenas:
        if arena.in_players(event.getEntity()):
            arena.player_stats[event.getEntity().getName() + "_deaths"] += 1
            if arena.check_deaths():
                arena.end_match()
            break

@hook.event("player.PlayerRespawnEvent", "high")
def onRespawn(event):
    if event.getPlayer().getWorld().getName() != "minigames":
        return
    player = event.getPlayer()
    for arena in arenas:
        if arena.in_players(player):
            event.setRespawnLocation(arena.get_respawn().get_location().get_location())
            break

@hook.event("entity.ProjectileHitEvent", "high")
def onHit(event):
    if event.getEntity().getWorld().getName() != "minigames":
        return
    if event.getEntity().getName() != "Snowball":
        return
    location = event.getEntity().getLocation()
    for arena in arenas:
        if arena.in_arena(location):
            event.getEntity().getWorld().createExplosion(location.x, location.y, location.z, float(arena.get_explosion_damage()), False, False)
            break

@hook.event("player.PlayerInteractEvent", "high")
def onClick(event):
    if event.getPlayer().getWorld().getName() != "minigames":
        return
    if str(event.getAction()) != "RIGHT_CLICK_BLOCK":
        return
    block = event.getClickedBlock().getState()
    if event.getClickedBlock().getType() == Material.SNOW_BLOCK:
        for arena in arenas:
            if arena.in_players(event.getPlayer()):
                inv = event.getPlayer().getInventory()
                inv.remove(Material.SNOW_BALL)
                inv.setItemInHand(ItemStack(Material.SNOW_BALL, arena.get_refill()))
                event.getPlayer().updateInventory()
                break

    elif isinstance(block, bukkit.block.Sign):
        line = str(block.getLine(1))
        if not event.getPlayer().hasPermission(join_perm):
            msg(event.getPlayer(), "&a-&e You don't have permission to join snowbrawl matches")
            return
        #go through arenas, if name matches line then add player to it
        for arena in arenas:
            if line == arena.get_name():
                for sign in arena.get_click_signs():
                    sign_loc = sign.get_location().get_location()
                    loc = block.getLocation()
                    if sign_loc.getWorld().getName() == loc.getWorld().getName() and sign_loc.x == loc.x and sign_loc.y == loc.y and sign_loc.z == loc.z:
                        if arena.add_player(event.getPlayer()):
                            msg(event.getPlayer(),"&a- &eYou have been added to the queue")
                        else:
                            msg(event.getPlayer(),"&a- &eYou are already in the queue")
                        break
        return


@hook.event("player.PlayerQuitEvent", "normal")
def on_quit(event):
    #remove the player from the queue
    player = event.getPlayer().getName()
    for arena in arenas:
        if arena.in_queue(player):
            arena.remove_player(player)



##############################################################################################
# Command handling
############################################################################################## 


def create_arena(sender, args):
    if len(args) == 0:
        msg(sender, "&c/sb %s <name>" % create_command)
        return
    arena = Arena(args[0])
    arenas.append(arena)
    msg(sender, "&a-&e Arena %s created" % args[0])

def list_arenas(sender):
    if len(arenas) == 0:
        msg(sender, "&a-&e There are currently no arenas")
        return
    for arena in arenas:
        msg(sender, "&a-&e %s" % arena.get_name())

def arena_info(sender, args):
    if len(args) == 0:
        msg(sender, "&a-&e /sb info <name>")
        return
    if len(arenas) == 0:
        msg(sender, "&a-&e There are currently no arenas")
        return
    for arena in arenas:
        if arena.get_name() == args[0]:
            msg(sender, "&a-&e %s" % arena.get_name())
            #msg(sender, "&ePlayers:&6 " + "&e,&6 ".join(arena.get_queue_contents()))
            spawn_list = []
            for spawn in arena.get_location("spawn"):
                spawn_list.append(spawn.get_name())
            msg(sender, "&eSpawns:&6 " + "&e,&6 ".join(spawn_list))
            respawn_list = []
            for respawn in arena.get_location("respawn"):
                respawn_list.append(respawn.get_name())
            msg(sender, "&eRespawns:&6 " + "&e,&6 ".join(respawn_list))
            sign_list = []
            for sign in arena.get_location("sign"):
                sign_list.append(sign.get_name())
            msg(sender, "&eSigns:&6 " + "&e,&6 ".join(sign_list))
            break

def quit_match(sender):
    for arena in arenas:
        if arena.in_queue(sender):
            arena.remove_player(sender)
            msg(sender, "&a-&e Quit arena")
            return
    msg(sender, "&a-&e You're not in a queue")

def print_help(sender):
    msg(sender, "&a-&e Alias: &6/sb")
    if sender.hasPermission(teleport_perm):
        msg(sender, "&a-&e /sb <name>     Teleport to an arena")
    if sender.hasPermission(quit_perm):
        msg(sender, "&a-&e /sb %s   Quit a queue" % quit_command)
    if sender.hasPermission(list_perm):
        msg(sender, "&a-&e /sb %s   List all existing arenas" % list_command)
    if sender.hasPermission(create_perm):
        msg(sender, "&a-&e /sb %s   Create an arena" % create_command)
    if sender.hasPermission(info_perm):
        msg(sender, "&a-&e /sb %s   Show info about an arena" % info_command)
    if sender.hasPermission(modify_perm):
        msg(sender, "&a-&e /sb %s   Deletes an arena" % del_command)
        msg(sender, "&a-&e /sb %s   Sets a teleport for an arena to a sign" % set_command)
        msg(sender, "&a-&e /sb %s   Renames an arena" % name_command)
        msg(sender, "&a-&e /sb %s   Sets the locations for an arena" % pos_command)
        msg(sender, "&a-&e /sb %s   Modifies the arena" % modify_command)
        msg(sender, "&a-&e Modify Aliases: &6/sbm&e,&6 /sb %s" % modify_command_alias)

def set_location(sender, args):
    if len(args) < 3:
        msg(sender, "&c/sb pos <arena name> respawn/spawn/sign set/add/del <name>")
        msg(sender, "&c/sb pos <arena name> bounds corner1/corner2")
        return
    if "bounds" not in args:
        if len(args) < 4:
            msg(sender, "&c/sb pos <arena name> respawn/spawn/sign set/add/del <name>")
            msg(sender, "&c/sb pos <arena name> bounds corner1/corner2")
            return
    if len(arenas) == 0:
        msg(sender, "&a-&e There are currently no arenas")
        return
    for arena in arenas:
        if arena.get_name() == args[0]:
            if args[1] == "respawn":
                set_location_of_type(sender, args[2:], "respawn", arena)
            elif args[1] == "spawn":
                set_location_of_type(sender, args[2:], "spawn", arena)
            elif args[1] == "sign":
                set_location_of_type(sender, args[2:], "sign", arena)
            elif args[1] == "bounds":
                set_location_of_type(sender, args[2:], "bounds", arena)
            break

def set_location_of_type(sender, args, type, arena):
    if len(args) == 0:
        msg(sender, "&c/sb pos <arena name> respawn/spawn/sign set/add/del <name>")
        msg(sender, "&c/sb pos <arena name> bounds corner1/corner2")
        return
    location = sender.getLocation()
    if args[0] == "set":
        arena.change_location(args[1], location, type)
        msg(sender, "&a-&e Location of name %s and type %s changed to your current location" % (args[1], type))
    elif args[0] == "add":
        arena.add_location(args[1], location, type)
        msg(sender, "&a-&e Location of name %s and type %s created at your current location" % (args[1], type))
    elif args[0] == "del":
        arena.delete_location(args[1], type)
        msg(sender, "&a-&e Location of name %s deleted" % args[1])
    elif args[0] == "corner1":
        arena.set_corner(sender, "1")
    elif args[0] == "corner2":
        arena.set_corner(sender, "2")

def rename_arena(sender, args):
    if len(args) < 2:
        msg(sender, "&c/sb name <name> <new name>")
        return
    for arena in arenas:
        if arena.get_name() == args[0]:
            arena.set_name(args[1])
            msg(sender, "&a-&e Arena %s renamed to %s" % (args[0], args[1]))
            return
    msg(sender, "&a-&e Arena with this name doesn't exist")

def delete_arena(sender, args):
    if len(args) == 0:
        msg(sender, "&c/sb del <name>")
        return
    for arena in arenas:
        if arena.get_name() == args[0]:
            arenas.remove(arena)
            msg(sender, "&a-&e Arena %s deleted" % arena.get_name())
            return
    msg(sender, "&a-&e Arena with this name doesn't exist")

def teleport_to_arena(sender, name, id):
    try:
        int(id)
    except ValueError:
        msg(sender, "&c/sb <name> <id of teleport>")
        return
    for arena in arenas:
        if arena.get_name() == name:
            i = 0
            if int(id) > len(arena.get_tp_signs()):
                msg(sender, "&cGiven tp id is out of range")
                return
            for sign in arena.get_tp_signs():
                i += 1
                if i == int(id):
                    loc = sign.get_location().get_location()
                    safetp(sender, loc.getWorld(), loc.x, loc.y, loc.z, loc.yaw, loc.pitch)
                    break
            msg(sender, "&a-&e Teleporting to arena %s" % name)
            return
    msg(sender, "&a-&e Arena with this name doesn't exist")

def modify_arena(sender, args):
    if len(args) < 3:
        msg(sender, "&c/sb modify <arena name> limit/mode/players/explosion/refill <amount/mode (death/time)>")
        return
    for arena in arenas:
        if arena.get_name() == args[0]:
            if args[1] == "limit":
                try:
                    int(args[2])
                except ValueError:
                    msg(sender, "&cLast parameter has to be a number")
                    return
                arena.set_end_goal(int(args[2]))
                msg(sender, "&a-&e Set time/death limit to:&6 %s" % int(args[2]))
            elif args[1] == "mode":
                if args[2] == "time" or args[2] == "death":
                    arena.set_type(args[2])
                    msg(sender, "&a-&e Set mode to:&6 %s" % args[2])
                else:
                    msg(sender, "&cInvalid mode (time, death)")
            elif args[1] == "players":
                try:
                    int(args[2])
                except ValueError:
                    msg(sender, "&cLast parameter has to be a number")
                    return
                arena.set_player_limit(int(args[2]))
                msg(sender, "&a-&e Set player limit to:&6 %s" % int(args[2]))
            elif args[1] == "explosion":
                try:
                    float(args[2])
                except ValueError:
                    msg(sender, "&cLast parameter has to be a number")
                    return
                arena.set_explosion_damage(float(args[2]))
                msg(sender, "&a-&e Set explosion power to:&6 %s" % float(args[2]))
            elif args[1] == "refill":
                try:
                    int(args[2])
                except ValueError:
                    msg(sender, "&cLast parameter has to be a number")
                    return
                arena.set_refill(int(args[2]))
                msg(sender, "&a-&e Set snowball refill to:&6 %s" % int(args[2]))
            return
    msg(sender, "&a-&e Arena with this name doesn't exist")

def set_arena_sign(sender, args):
    if len(args) < 3:
        msg(sender, "&c/sb set <arena name> add/del <name>")
        return
    for arena in arenas:
        if arena.get_name() == args[0]:
            if args[1] == "add":
                arena.add_sign(sender, args[2])
            elif args[1] == "del":
                arena.del_sign(sender, args[2])

@hook.command("sbm")
def on_snowbrawl_command_modify(sender, command, label, args):
    args_ = args
    args_.insert(0, modify_command)
    return on_snowbrawl_command(sender, command, label, args_)

@hook.command("sb")
def on_snowbrawl_command_short(sender, command, label, args):
    return on_snowbrawl_command(sender, command, label, args)


@hook.command("snowbrawl")
def on_snowbrawl_command(sender, command, label, args):
    if len(args) == 0:
        #print help
        plugin_header(sender, "Snowbrawl")
        print_help(sender)
        return True
    elif args[0] == list_command:
        if sender.hasPermission(list_perm):
            #print the list of arenas
            list_arenas(sender)
        else:
            noperm(sender)
        return True
    elif args[0] == del_command:
        if sender.hasPermission(modify_perm):
            #delete an arena
            delete_arena(sender, args[1:])
            save_snowbrawl()
        else:
            noperm(sender)
        return True
    elif args[0] == info_command:
        if sender.hasPermission(info_perm):
            #print info about an arena
            arena_info(sender, args[1:])
        else:
            noperm(sender)
        return True
    elif args[0] == create_command:
        if sender.hasPermission(create_perm):
            #create an arena
            create_arena(sender, args[1:])
            save_snowbrawl()
        else:
            noperm(sender)
        return True
    elif args[0] == pos_command:
        if sender.hasPermission(modify_perm):
            #set arena spawn/respawn/sign tp locations
            set_location(sender, args[1:])
            save_snowbrawl()
        else:
            noperm(sender)
        return True
    elif args[0] == name_command:
        if sender.hasPermission(modify_perm):
            #rename an arena
            rename_arena(sender, args[1:])
            save_snowbrawl()
        else:
            noperm(sender)
        return True
    elif args[0] == set_command:
        if sender.hasPermission(modify_perm):
            #set an arena tp sign
            set_arena_sign(sender, args[1:])
            save_snowbrawl()
        else:
            noperm(sender)
        return True
    elif args[0] == modify_command or args[0] == modify_command_alias:
        if sender.hasPermission(modify_perm):
            #modify the arena
            modify_arena(sender, args[1:])
            save_snowbrawl()
        else:
            noperm(sender)
        return True
    elif args[0] == quit_command:
        if sender.hasPermission(quit_perm):
            #quit match
            quit_match(sender)
        else:
            noperm(sender)
        return True
    else:
        if sender.hasPermission(teleport_perm):
            #try to tp to an arena
            if len(args) > 1:
                teleport_to_arena(sender, args[0], args[1])
            else:
                teleport_to_arena(sender, args[0], 1)
        else:
            noperm(sender)
    return True
