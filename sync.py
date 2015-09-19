from helpers import *
from java.lang import Runnable

class Sync_class(Runnable):

	def __init__(self,function,*args,**kwargs):
		self.function = function
		self.args = args
		self.kwargs = kwargs

	def run(self):
		self.function(self.args,self.kwargs)



def sync(function):
	def wrapper(*args,**kwargs):
		sync_function = Sync_class(function)
		server.getScheduler().runTask(server.getPluginManager().getPlugin("RedstonerUtils"),sync_function)
		return None
	return wrapper