from helpers import *
import socket
import threading
import time
from java.lang import Runnable
from adminchat import adminchat

"""
Module to allow our servercontrol telnet server forward chat and speak in AC


"""
host = ""
port = 1122

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)

try:
	sock.bind((host,port))
	sock.setblocking(True)
	sock.listen(5)
except socket.error as e:
	print(str(e))

def command_process(text):
    text = list(text)
    args = []
    arg = ""
    
    for char in text:
        if char != " " and char != "\n" and char != "\r" and char != "\t":
            arg += char
        elif arg != "":
            args.append(arg)
            arg = ""
    if arg != "":
        args.append(arg)
    return args

clients = []
clients_l = threading.Lock()

class client():
	def __init__(self,conn,address,name):
		self.conn = conn
		self.address = address
		self.name = name
		
		with clients_l:
			clients.append(self)

		self.conn.setblocking(False)

		self.client_thread = threading.Thread(target=self.client_t)
		self.client_thread.daemon = True
		self.client_thread.start()

	def getName(self):
		return self.name


	def close_connection(self):
		try:
			self.conn.close()
			with clients_l:
				clients.remove(self)
		except:
			pass


	def client_t(self):

		while True:
			time.sleep(0.1)
			try:
				data = self.conn.recv(1024)
			except:
				if self not in clients:
					self.close_connection()
				continue

			if self not in clients: #If the connection was closed, kill the thread
				break

			adminchat(self,data)


def handle_conn():
	while True:
		try:
			conn, address = sock.accept()
		except:
			time.sleep(0.1)
			continue

		#Send name
		data = conn.recv(1024)
		data = command_process(data)
		print "servercontrol connected! %s " %data[0]
		client_c = client(conn, address,data[0])


handle_conn_t = threading.Thread(target=handle_conn)
handle_conn_t.daemon = True
handle_conn_t.start()


@hook.event("player.AsyncPlayerChatEvent","low")
def on_chat(event):
	sender = event.getPlayer().getName()
	msg = event.getMessage()
	
	for entry in clients:
		entry.conn.sendall(sender + " " + msg)