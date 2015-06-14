#Snowbrawl
from helpers import *
import time
import thread
import copy
import org.bukkit.Material as Material
import org.bukkit.inventory.ItemStack as ItemStack
from java.util.UUID import fromString as juuid

#file names
arena_file = "snowbrawl"
sign_file = "snowbrawl_sign_coords"

#permissions
list_perm = "utils.snowbrawl.list"
modify_perm = "utils.snowbrawl.modify"
teleport_perm = "utils.snowbrawl.tp"
create_perm = "utils.snowbrawl.create"
info_perm = "utils.snowbrawl.info"
join_perm = "utils.snowbrawl.join"

#commands - tp command does not exist
list_command = "list"
del_command = "del"
set_command = "set"
name_command = "name"
pos_command = "pos"
create_command = "create"
info_command = "info"

arenas = open_json_file(arena_file, [])
signs = open_json_file(sign_file, [])
matches = []
                                        ### TODO queue, more testing ###
def get_best(players):
    highest = 2147483647
    player_out = players[0]
    for i in range(len(players)):
        player = players[i]
        if player["deaths"] < highest:
            highest = player["deaths"]
            player_out = player
    return player_out
        

def add_match(name):
    for i in range(len(arenas)):
        arena = arenas[i]
        if arena["name"] == name:
            match = {
                "end_time": (time.time() + int(arena["match_time"])),
                "match_length": int(arena["match_time"]),
                "arena": name,
                "players": [],
                "started": False,
                "limit": int(arena["player_limit"])
            }
            matches.append(match)
            break


def end_match(name):
    for i in range(len(matches)):
        match = matches[i]
        if match["arena"] == name:
            for j in range(len(arenas)):
                arena = arenas[j]
                if arena["name"] == name:
                    players = match["players"]
                    players_copy = copy.deepcopy(players)
                    best1 = None if len(players_copy) < 1 else get_best(players_copy)
                    if best1 != None:
                        for o in range(len(players_copy)):
                            if players_copy[o] == best1:
                                players_copy.pop(o)
                                break
                    best2 = None if len(players_copy) < 1 else get_best(players_copy)
                    if best2 != None:
                        for o in range(len(players_copy)):
                            if players_copy[o] == best2:
                                players_copy.pop(o)
                                break
                    best3 = None if len(players_copy) < 1 else get_best(players_copy)
                    for k in range(len(players)):
                        player_array = players[k]
                        player = server.getPlayer(juuid(player_array["uuid"]))
                        deaths = player_array["deaths"]
                        msg(player, "&e==========================================")
                        msg(player, "&a&a")
                        msg(player, "&aMatch over!")
                        if best1 != None:
                            msg(player, "&61.&e %s &a-&6 %s deaths" % (server.getPlayer(juuid(best1["uuid"])).getName(), best1["deaths"]))
                        if best2 != None:
                            msg(player, "&62.&e %s &a-&6 %s deaths" % (server.getPlayer(juuid(best2["uuid"])).getName(), best2["deaths"]))
                        if best3 != None:
                            msg(player, "&63.&e %s &a-&6 %s deaths" % (server.getPlayer(juuid(best3["uuid"])).getName(), best3["deaths"]))
                        msg(player, "&a&a")
                        msg(player, "&aYour deaths:&6 %s" % deaths)
                        msg(player, "&a&a")
                        msg(player, "&e==========================================")
                        pos = server.getWorld(arena["spawn_world"]).getSpawnLocation();
                        safetp(player, server.getWorld(arena["spawn_world"]), pos.x, pos.y, pos.z, pos.yaw, pos.pitch)
                    matches.pop(i)
                    update_queue(name)
                    break


def join_match(sender, name):
    for i in range(len(matches)):
        match = matches[i]
        if match["arena"] == name:
            if len(match["players"]) >= int(match["limit"]):
                add_to_queue(sender, name)
            else:
                player = {
                    "uuid": uid(sender),
                    "deaths": 0
                }
                match["players"].append(player)
                msg(sender, "&aMatch joined")
                if len(match["players"]) >= int(match["limit"]):
                    start_match(name)
            return
    add_match(name)
    join_match(sender, name)


def start_match(name):
    for i in range(len(matches)):
        match = matches[i]
        if match["arena"] == name:
            for k in range(len(arenas)):
                arena = arenas[k]
                if arena["name"] == name:
                    players = match["players"]
                    for j in range(len(players)):
                        player = server.getOfflinePlayer(juuid(players[j]["uuid"]))
                        if player.isOnline():
                            msg(player, "&e==========================================")
                            msg(player, "&a&a")
                            msg(player, "&aMatch started!")
                            msg(player, "&6Player with least deaths wins!")
                            msg(player, "&a&a")
                            msg(player, "&e==========================================")                            
                            safetp(player.getPlayer(), server.getWorld(arena["spawn_world"]), arena["spawn_pos_x"], arena["spawn_pos_y"], arena["spawn_pos_z"], arena["spawn_yaw"], arena["spawn_pitch"])
                        else:
                            match["players"].pop(j)
                            j -= 1;
                    match["started"] = True
                    break


def add_to_queue(sender, name):

    msg(sender, "&aMatch is currently in progress, you will be automatically teleported once it is over")


def update_queue(name):
    print("UPDATING QUEUE")


def save_snowbrawl():
    save_json_file(arena_file, arenas)
    save_json_file(sign_file, signs)


def set_arena_sign(sender, name, sign):
    sign.setLine(0, "")
    sign.setLine(1, name)
    sign.setLine(2, "")
    sign.setLine(3, "")
    position = sign.getLocation()
    coord = {
        "x": position.x,
        "y": position.y,
        "z": position.z,
        "arena": name
    }
    signs.append(coord)
    save_snowbrawl()
    msg(sender, "&aArena sign set")


def delete_arena(sender, name):
    for i in range(len(arenas)):
        arena = arenas[i]
        if arena["name"] == name:
            end_match(name)
            arenas.pop(i)
            save_snowbrawl()
            msg(sender, "&aArena deleted")
            break


def rename_arena(sender, name, newName):
    for i in range(len(arenas)):
        arena = arenas[i]
        if arena["name"] == name:
            for j in range(len(matches)):
                match = matches[j]
                if match["arena"] == name:
                    match["arena"] = newName
                    msg(sender, "&aRunning match appended to arena&6 %s" % newName)
            arena["name"] = newName
            save_snowbrawl()
            msg(sender, "&aArena renamed to&6 %s" % newName)
            break


def respawn_arena(sender, name):
    for i in range(len(arenas)):
        arena = arenas[i]
        if arena["name"] == name:
            loc = sender.getLocation()
            arena["respawn_pos_x"] = int(loc.x)
            arena["respawn_pos_y"] = int(loc.y)
            arena["respawn_pos_z"] = int(loc.z)
            arena["respawn_yaw"] = int(loc.yaw)
            arena["respawn_pitch"] = int(loc.pitch)
            arena["respawn_world"] = loc.getWorld().name
            arena["respawn_set"] = True
            save_snowbrawl()
            msg(sender, "&aArena respawn set")
            break


def spawn_arena(sender, name):
    for i in range(len(arenas)):
        arena = arenas[i]
        if arena["name"] == name:
            loc = sender.getLocation()
            arena["spawn_pos_x"] = int(loc.x)
            arena["spawn_pos_y"] = int(loc.y)
            arena["spawn_pos_z"] = int(loc.z)
            arena["spawn_yaw"] = int(loc.yaw)
            arena["spawn_pitch"] = int(loc.pitch)
            arena["spawn_world"] = loc.getWorld().name
            arena["spawn_set"] = True
            save_snowbrawl()
            msg(sender, "&aArena spawn set")
            break


def create_arena(sender, name, limit, time):
    arena = {
        "name": name,
        "player_limit": limit,
        "match_time": time,
        "respawn_pos_x": 0,
        "respawn_pos_y": 0,
        "respawn_pos_z": 0,
        "spawn_pos_x": 0,
        "spawn_pos_y": 0,
        "spawn_pos_z": 0,
        "spawn_set": False,
        "respawn_set": False
    }
    arenas.append(arena)
    save_snowbrawl()
    msg(sender, "&aArena&6 %s &acreated" % arena["name"])


def print_help(sender):
    plugin_header(sender, "Snowbrawl")
    msg(sender, "&aAlias: &6/sb")
    if sender.hasPermission(list_perm):
        msg(sender, "&a/snowbrawl %s      &eDisplay the list of arenas" % list_command)
    if sender.hasPermission(info_perm):
        msg(sender, "&a/snowbrawl %s      &eDisplay info about an arena" % info_command)
    if sender.hasPermission(teleport_perm):
        msg(sender, "&a/snowbrawl <name>    &eTeleport to a certain arena")
    if sender.hasPermission(modify_perm):
        msg(sender, "&a/snowbrawl %s       &eSet a snowbrawl arena sign" % set_command)
        msg(sender, "&a/snowbrawl %s       &eDelete a snowbrawl arena sign" % del_command)
        msg(sender, "&a/snowbrawl %s      &eChange an arena sign name" % name_command)
        msg(sender, "&a/snowbrawl %s       &eSet the tp position for the arena" % pos_command)
    if sender.hasPermission(create_perm):
        msg(sender, "&a/snowbrawl %s    &eCreate an arena" % create_command)


def check_valid_name(name):
    if name in [list_command, del_command, set_command, name_command, pos_command]:
        return False
    exists = False
    for i in range(len(arenas)):
        arena = arenas[i]
        if name == arena["name"]:
            exists = True
            break
    if exists:
        return False
    return True


@hook.event("player.PlayerRespawnEvent", "high")
def onRespawn(event):
    if event.getPlayer().getWorld().getName() != "minigames":
        return
    player = event.getPlayer()
    for i in range(len(matches)):
        match = matches[i]
        players = match["players"]
        for j in range(len(players)):
            if uid(player) == players[j]:
                for k in range(len(arenas)):
                    arena = arenas[k]
                    if arena["name"] == match["arena"]:
                        event.setRespawnLocation(Location(server.getWorld(arena["respawn_world"]), arena["respawn_pos_x"], arena["respawn_pos_y"], arena["respawn_pos_z"], arena["respawn_yaw"], arena["respawn_pitch"]))
                        break


@hook.event("entity.PlayerDeathEvent", "high")
def onDeath(event):
    if event.getEntity().getWorld().getName() != "minigames":
        return
    player = event.getEntity()
    for i in range(len(matches)):
        match = matches[i]
        players = match["players"]
        for j in range(len(players)):
            if uid(player) == players[j]["uuid"]:
                for k in range(len(arenas)):
                    arena = arenas[k]
                    if arena["name"] == match["arena"]:
                        players[j]["deaths"] += 1
                        break


@hook.event("entity.ProjectileHitEvent", "high")
def onHit(event):
    if event.getEntity().getWorld().getName() != "minigames":
        return
    if event.getEntity().getName() != "Snowball":
        return
    entity = event.getEntity()
    location = entity.getLocation()
    entity.getWorld().createExplosion(location.getX(), location.getY(), location.getZ(), float(5), False, False)


@hook.event("player.PlayerInteractEvent", "high") # add snowblock click to refill snowballs
def onClick(event):
    if str(event.getAction()) != "RIGHT_CLICK_BLOCK":
        return
    block = event.getClickedBlock().getState()

    if event.getClickedBlock().getMaterial() == Material.SNOW_BLOCK:
        inv = event.getPlayer().getInventory()
        for slot, stack in dict(inv.all(Material.SNOW_BALL)).iteritems():
            stack.setAmount(0)
        inv.setItemInHand(ItemStack(Material.SNOW_BALL, 4))

    elif isinstance(block, bukkit.block.Sign) and not event.isCancelled():
        line = block.getLine(1)
        for j in range(len(arenas)):
            arena = arenas[j]
            if arena["name"] == line:
                for i in range(len(signs)):
                    sign = signs[i]
                    if sign["arena"] == line:
                        pos = block.getLocation()
                        if sign["x"] == pos.x and sign["y"] == pos.y and sign["z"] == pos.z:
                            if arena["spawn_set"] and arena["respawn_set"]:
                                if event.getPlayer().hasPermission(join_perm):
                                    join_match(event.getPlayer(), line)
                                else:
                                    msg(event.getPlayer(), "&a-&e You don't have permission to join snowbrawl matches")
                        break


@hook.command("sb")
def on_snowbrawl_command_short(sender, command, label, args):
    return on_snowbrawl_command(sender, command, label, args)


@hook.command("snowbrawl")
def on_snowbrawl_command(sender, command, label, args):

    cmd = args[0] if len(args) > 0 else None
    if cmd == None: #No arguments, print help
        print_help(sender)
    elif cmd == list_command: #print the list of arenas
        if sender.hasPermission(list_perm):
            if len(arenas) > 0:
                for i in range(len(arenas)):
                    msg(sender, "&a- &e%s" % arenas[i]["name"])
            else:
                msg(sender, "&a- &eNo snowbrawl arenas exist")
        else:
            noperm(sender)
    elif cmd == set_command: #set an arena tp sign
        if not is_player(sender):
            msg(sender, "&cOnly players can do this")
            return True
        if sender.hasPermission(modify_perm):
            if len(args) > 1:
                mats = set()
                mats = None
                block = sender.getTargetBlock(mats, 3).getState()
                if isinstance(block, bukkit.block.Sign):
                    set_arena_sign(sender, str(args[1]), block)
                else:
                    msg(sender, "&cYou are not looking at a sign")
            else:
                msg(sender, "&cArena to create is not specified")
                msg(sender, "&e/snowbrawl %s <name>" % set_command)
        else:
            noperm(sender)
    elif cmd == del_command: #delete an arena
        if sender.hasPermission(modify_perm):
            if len(args) > 1:
                exists = False
                for i in range(len(arenas)):
                    arena = arenas[i]
                    if str(args[1]) == arena["name"]:
                        exists = True
                        break
                if exists:
                    delete_arena(sender, str(args[1]))
                else:
                    msg(sender, "&cArena&e %s &cdoes not exist" % str(args[1]))
            else:
                msg(sender, "&cArena to delete is not specified")
                msg(sender, "&a/snowbrawl %s <name>" % del_command)
        else:
            noperm(sender)
    elif cmd == name_command: #rename an arena
        if sender.hasPermission(modify_perm):
            if len(args) > 1:
                if len(args) > 2:
                    exists = False
                    for i in range(len(arenas)):
                        arena = arenas[i]
                        if str(args[1]) == arena["name"]:
                            exists = True
                            break
                    if exists:
                        if check_valid_name(str(args[1])):
                            rename_arena(sender, str(args[1]), str(args[2]))
                        else:
                            msg(sender, "&cArena name is invalid")
                    else:
                        msg(sender, "&cArena&e %s &cdoes not exist" % str(args[1]))
                else:
                    msg(sender, "&cNew name is not specified")
                    msg(sender, "&a/snowbrawl %s <name> <newName>" % name_command)
            else:
                msg(sender, "&cArena to rename is not specified")
                msg(sender, "&a/snowbrawl %s <name> <newName>" % name_command)
        else:
            noperm(sender)
    elif cmd == pos_command: #set a tp position for an arena
        if not is_player(sender):
            msg(sender, "&cOnly players can do this")
            return True
        if sender.hasPermission(modify_perm):
            if len(args) > 1:
                if len(args) > 2:
                    exists = False
                    for i in range(len(arenas)):
                        arena = arenas[i]
                        if str(args[2]) == arena["name"]:
                            exists = True
                            break
                    if exists:
                        if str(args[1]) == "spawn":
                            spawn_arena(sender, str(args[2]))
                        elif str(args[1]) == "respawn":
                            respawn_arena(sender, str(args[2]))
                        else:
                            msg(sender, "&cInvalid mode")
                            msg(sender, "&aValid modes: &6spawn&a,&6 respawn")
                    else:
                        msg(sender, "&cArena&e %s &cdoes not exist" % str(args[2]))
                else:
                    msg(sender, "&cSpawn/respawn not specified")
                    msg(sender, "&a/snowbrawl %s re/spawn <name>" % pos_command)
            else:
                msg(sender, "&cArena to set position of is not specified")
                msg(sender, "&a/snowbrawl %s re/spawn <name>" % pos_command)
        else:
            noperm(sender)
    elif cmd == create_command: #Create an arena
        if sender.hasPermission(create_perm):
            if len(args) > 1:
                if len(args) > 2:
                    if len(args) > 3:
                        if check_valid_name(str(args[1])):
                            if str(args[2]).isdigit():
                                if str(args[3]).isdigit():
                                    create_arena(sender, str(args[1]), int(args[2]), int(args[3]))
                                else:
                                    msg(sender, "&cTime is not in a valid format")
                                    msg(sender, "&aFormat:&6 seconds")
                            else:
                                msg(sender, "&cPlayer is not in a valid format")
                                msg(sender, "&aFormat:&6 amount of players")
                        else:
                            msg(sender, "&cArena name is invalid")
                    else:
                        msg(sender, "&cMatch time is not specified")
                        msg(sender, "&a/snowbrawl %s <name> <playerLimit> <matchTime>" % create_command)
                else:
                    msg(sender, "&cPlayer limit is not specified")
                    msg(sender, "&a/snowbrawl %s <name> <playerLimit> <matchTime>" % create_command)
            else:
                msg(sender, "&cArena name is not specified")
                msg(sender, "&a/snowbrawl %s <name> <playerLimit> <matchTime>" % create_command)
        else:
            noperm(sender)
    elif cmd == info_command: #print info about an arena
        if sender.hasPermission(info_perm):
            if len(args) > 1:
                exists = False
                arenaId = 0
                for i in range(len(arenas)):
                    arena = arenas[i]
                    if str(args[1]) == arena["name"]:
                        exists = True
                        arenaId = i
                        break
                if exists:
                    msg(sender, "&a- &e%s" % arenas[arenaId])
                else:
                    msg(sender, "&a- &eArena&6 %s &edoes not exist" % cmd)
            else:
                msg(sender, "&cArena name is not specified")
                msg(sender, "&a/snowbrawl %s <name>" % info_command)
        else:
            noperm(sender)
    else: #arguments dont match, teleport to an arena
        if not is_player(sender):
            msg(sender, "&cOnly players can do this")
            return True
        if sender.hasPermission(teleport_perm):
            exists = False
            for i in range(len(arenas)):
                arena = arenas[i]
                if cmd == arena["name"]:
                    exists = True
                    break
            if exists:
                msg(sender, "&a-&e Teleporting to arena&6 %s" % cmd)
            else:
                msg(sender, "&a- &eArena&6 %s &edoes not exist" % cmd)
        else:
            noperm(sender)
    return True


isThreadRunning = True

def countdown_timer():
    while True:
        time.sleep(1)
        if not isThreadRunning:
            thread.exit()
        for i in range(len(matches)):
            match = matches[i]
            if bool(match["started"]):
                if int(match["end_time"]) < time.time():
                    end_match(match["arena"])

def stop_match_end_thread():
    global isThreadRunning
    print("Stopping snowbrawl match end check thread")
    isThreadRunning = False


thread.start_new_thread(countdown_timer, ())