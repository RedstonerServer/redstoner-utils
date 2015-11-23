from wrapper import *
from wrapper_player import *
from traceback import format_exc as print_traceback

class py_event:
	def __init__(self,event):
		self.event = event
		try:
			self.player = py_players[event.getPlayer()]
		except:
			warn("Player doesn't exist")

	@property
	def cancelled(self):
		return self.event.isCancelled()

	@cancelled.setter
	def cancelled(self, value):
		self.event.setCancelled(value)

def event_handler(event_name = None, priority = "normal"):
	def decorator(wrapped):
		@hook.event(event_name, priority)
		def wrapper(event):
			try:
				wrapped(py_event(event))
			except:
				print(print_traceback())
	return decorator

