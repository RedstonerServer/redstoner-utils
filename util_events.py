from thread_utils import *

MONITOR_PRIORITY = "monitor"
HIGHEST_PRIORITY = "highest"
HIGH_PRIORITY    = "high"
NORMAL_PRIORITY  = "normal"
LOW_PRIORITY     = "low"
LOWEST_PRIORITY  = "lowest"

priorities = ["lowest","low","normal","high","highest","monitor"]
events = []

class base_event():
    def __init__(self,event_name):
        self.name = event_name
        self.canceled = False
        self._handlers = [ [],[],[],[],[],[] ]

        self.canceled_lock = threading.Lock()

    def add_handler(self,function,priority):
        for prior in priorities:
            if prior == priority:
                self._handlers[priorities.index(prior)].append(function)

    def fire(self,*args):
        for priority in self._handlers:
            for handler in priority:
                handler(self,*args)

    def set_canceled(self,state):
        with self.canceled_lock:
            self.canceled = state


class utils_events(base_event):
    def __init__(self,event_name):
        base_event.__init__(self,event_name)


def add_event(event_name,event = base_event): #Adds a new event
    event = event(event_name)
    events.append(event)

def fire_event(event_name,*args): #Fires the event
    for event in events:
        if event.name == event_name:
            event.fire(*args)
            return event

def check_events(event_name): #Returns false if the even does not exist.
    for event in events:
        if event.name == event_name:
            return True
    return False


#Decorator
def utils_event(event_name, priority, create_event=base_event):
    def event_decorator(function):
        def wrapper(*args, **kwargs):
            pass

        if not check_events(event_name): #Check if the event exists, if not create it.
            add_event(event_name,create_event)

        for event in events: #Go through the list of events, find the one we need and call all of its handlers
            if event.name == event_name:
                event.add_handler(function,priority)
        return wrapper
    return event_decorator