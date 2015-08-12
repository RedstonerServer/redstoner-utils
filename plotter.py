#!/usr/bin/python

"""
*Very basic* start of a custom plot-plugin like PlotMe
on hold because the PlotMe developer continued to develop PlotMe
"""

from helpers import *
from basecommands import simplecommand

plot_size   = 20
padding     = 3
padded_size = plot_size + padding

def base_coords(x, z):
    pid = plot_id(x, z)
    return [pid[0] * padded_size, pid[1] * padded_size] if pid else None

def bounds(x, z):
    base = base_coords(x, z)
    return [base, [base[0] + plot_size, base[1] + plot_size]] if base else None

def is_border(x, z):
    xborder = plot_size < x % padded_size < padded_size
    zborder = plot_size < z % padded_size < padded_size
    return xborder or zborder

def plot_id(x, z):
    idx = x // padded_size
    idz = z // padded_size
    return None if is_border(x, z) else [idx, idz]


@simplecommand("plotter",
    aliases = ["pt"],
    senderLimit = 0,
    helpSubcmd = True,
    description = "Plot commands",
    usage = "")
def plotter_command(sender, command, label, args):
    loc = sender.getLocation()
    x = loc.getX()
    z = loc.getZ()
    msg(sender, "id: %s" % plot_id(x, z))
    msg(sender, "base: %s" % base_coords(x, z))
    msg(sender, "bounds: %s" % bounds(x, z))
