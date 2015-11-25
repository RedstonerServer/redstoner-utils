from wrapper import *
from util_events import utils_event, utils_events
from wrapper_player import *
from traceback import format_exc as print_traceback

class py_event(object):
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

    @property
    def message(self):
        try:
            return self.event.getMessage()
        except:
            raise AttributeError
    
    @message.setter
    def message(self, msg):
        try:
            self.event.setMessage(msg)
        except:
            raise AttributeError

def event_handler(event_name = None, priority = "normal", utils = False):
    if not utils:
        def decorator(wrapped):
            @hook.event(event_name, priority)
            def wrapper(event):
                try:
                    wrapped(py_event(event))
                except:
                    print(print_traceback())
        return decorator
    elif utils:
        def decorator(wrapped):
            @utils_event(event_name, priority, create_event = utils_events)
            def wrapper(*args):
                try:
                    wrapped(*args)
                except:
                    print(print_traceback())
        return decorator


