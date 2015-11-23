from wrapper_player import *

def command(command = "help"):
    def decorator(wrapped):        
        @hook.command(command)
        def wrapper(sender, command, label, args):
            try:
                return wrapped(sender = py_players[sender], command = command, label = label, args = args)
            except:
                print(print_traceback())
    return decorator