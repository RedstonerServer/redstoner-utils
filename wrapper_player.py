import time
import mysqlhack
from mysql_utils import *
from util_events import fire_event
from thread_utils import *
from players_secret import *
from datetime import datetime
from com.ziclix.python.sql import zxJDBC
from traceback import format_exc as print_traceback

class py_player(object):
    def __init__(self,player):
        self.player = player
        self.logging_in = True
        self.authenticated = False
        self.login_time = time.time()
        
        self.props ={"uuid":self.uuid,
        "name":self.name,
        "nickname":self.name,
        "registered":False,
        "password":"None",
        "banned":False,
        "banned_reason":"You have been banned!",
        "played_time":time.time() - self.login_time,
        "last_login":datetime.now(),
        "first_seen":datetime.now()}

    def __setattr__(self, attribute, value):
        if not attribute in dir(self):
            if not 'props' in self.__dict__:
                self.__dict__[attribute] = value
            else:
                self.props[attribute] = value
        else:
            object.__setattr__(self, attribute, value)

    def __getattr__(self, attribute):
        try:
            return self.props[attribute]
        except:
            pass
            
    def save(self):
        properties = []
        keys = []
        columns = []

        with mysql_connect() as sql:
            columns = sql.columns
        
        for key, value in self.props.items():
            if key not in columns:
                with mysql_connect() as sql:
                    if isinstance(value, int):
                        sql.execute("ALTER TABLE utils_players ADD %s INT" % key)
                    elif isinstance(value, str):
                        sql.execute("ALTER TABLE utils_players ADD %s TEXT" % key)
                    elif isinstance(value, bool):
                        sql.execute("ALTER TABLE utils_players ADD %s TINYINT(1)" % key)
            if key == "uuid":
                continue
            keys.append(key+"=?")
            properties.append(value)
            print value
        properties.append(self.props["uuid"])
        keys = str(tuple(keys)).replace("\'","").replace("(","").replace(")","")


        with mysql_connect() as sql:
            sql.execute("UPDATE utils_players set %s WHERE uuid = ?" % keys, properties)


    def kick(self, kick_message = "You have been kicked from the server!"):
        self.player.KickPlayer(kick_message)

    def msg(self, message):
        self.player.sendMessage(message)

    @property
    def name(self):
        return self.player.getName()

    @property
    def uuid(self):
        return str(self.player.getUniqueId())
 
    

class Py_players:
    def __init__(self):
        self.players = []

    def __len__(self):
        return len(self.players)

    def __getitem__(self, player):
        for py_player in self.players:
            if py_player.name == player.getName():
                return py_player
        else:
            return None

    def remove(self, player):
        self.players.remove(player)

    def append(self, player):
        self.players.append(player)

py_players = Py_players()

@async(daemon=True)
def fetch_player(player):

    properties = []
    keys = []
    for key, value in player.props.iteritems():
        keys.append(key)
        properties.append(value)

    with mysql_connect() as sql:
        sql.execute("SELECT * FROM utils_players WHERE uuid = ?", (player.uuid,))
        result = sql.fetchall()

    if len(result) is 0:
        with mysql_connect() as sql:
            sql.execute("INSERT INTO utils_players %s \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)" % str(tuple(keys)).replace("\'","")
                ,args=tuple(properties))

    elif len(result) is 1:
        keys = []
        props = result[0]
        with mysql_connect() as sql:
            sql.execute("SHOW COLUMNS FROM utils_players")
            result = sql.fetchall()
            for row in result:
                keys.append(row[0]) 

        for key in keys:
            player.props[key] = props[keys.index(key)]

        for prop in properties:
            print str(prop)

    else:
        player.kick("Something went wrong while loading your player data, please contact an admin")
        return
    
    player.logging_in = False
    player.msg("You have succesfully logged into redstoner!")
    fire_event("player_login", player)




blocked_events = ["block.BlockBreakEvent", "block.BlockPlaceEvent", "player.PlayerMoveEvent",
                    "player.AsyncPlayerChatEvent","player.PlayerTeleportEvent",
                    "player.PlayerCommandPreprocessEvent", "player.PlayerInteractEvent"]

for event in blocked_events:
    @hook.event(event,"highest")
    def on_blocked_event(event):
        player = py_players[event.getPlayer()]
        if player.logging_in:
            event.setCancelled(True)



@hook.event("player.PlayerJoinEvent","lowest")
def on_join(event):
    try:
        player = py_player(event.getPlayer())
    except:
        print(print_traceback())
        time.sleep(10)
    py_players.append(player)
    player.msg("Your input will be blocked for a short while")
    fetch_player(player)


@hook.event("player.PlayerQuitEvent","highest")
def on_leave(event):
    py_players.remove(py_players[event.getPlayer()])
