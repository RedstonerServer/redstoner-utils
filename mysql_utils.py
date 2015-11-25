import mysqlhack
from secrets import *
from thread_utils import *
from com.ziclix.python.sql import zxJDBC
from traceback import format_exc as trace

class mysql_connect:
    def __init__(self):
        self.conn = zxJDBC.connect(mysql_database, mysql_user, mysql_pass, "com.mysql.jdbc.Driver")
        self.curs = self.conn.cursor()

    def execute(self, query, args=None):
        if args is None:
            return self.curs.execute(query)
        else:
            print query
            print args
            return self.curs.execute(query, args)

    def fetchall(self):
        return self.curs.fetchall()

    @property
    def columns(self):
        self.execute("SHOW COLUMNS FROM utils_players")
        fetched = self.fetchall()
        columns = []

        for row in fetched:
            columns.append(row[0])
        return columns

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_inst, exc_tb):
        if exc_type is None:
            try:        
                self.conn.commit()
                self.curs.close()
                self.conn.close()
            except:
                print(trace())
        else:
            print(exc_tb)
