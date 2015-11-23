import time
import mysqlhack
from mysql_utils import *
from thread_utils import *
from players_secret import *
from datetime import datetime
from com.ziclix.python.sql import zxJDBC

class py_player:
    def __init__(self,player):
        self.player = player
        self.login_time = time.time()
        self.logging_in = False

        self.nickname = self.name
        self.registered = False
        self.password = "None"
        self.banned = False
        self.banned_reason = "You have been banned!"
        self.played_time = time.time() - self.login_time
        self.last_login = datetime.now()
        self.first_seen = datetime.now()

    def kick(self, kick_message = "You have been kicked from the server!"):
        self.player.KickPlayer(kick_message)

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
    properties = (player.uuid, player.name, player.nickname, player.registered, 
                        player.password, player.banned, 
                        player.banned_reason, player.played_time, 
                        player.last_login, player.first_seen)

    with mysql_connect() as sql:
        sql.execute("SELECT * FROM utils_players WHERE uuid = ?", (player.uuid,))
        result = sql.fetchall()

    if len(result) is 0:
        with mysql_connect() as sql:
            sql.execute("INSERT INTO utils_players \
                (uuid, name, nickname, registered, password, banned, \
                banned_reason, played_time, last_login, first_seen) \
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                
                args=properties)

    elif len(result) is 1:
        props = result[0]
        print props
        for prop in properties:
            prop = props[properties.index(prop)]


        


@hook.event("player.PlayerJoinEvent","lowest")
def on_join(event):
    player = py_player(event.getPlayer())
    py_players.append(player)
    fetch_player(player)


@hook.event("player.PlayerQuitEvent","highest")
def on_leave(event):
    py_players.remove(py_players[event.getPlayer()])
