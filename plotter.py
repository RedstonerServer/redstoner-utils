#!/usr/bin/python

"""
*Very basic* start of a custom plot-plugin like PlotMe
on hold because the PlotMe developer continued to develop PlotMe
"""

from helpers import *
from basecommands import simplecommand

x_plot_size = 3
z_plot_size = 3
padding     = 1

def base_coords(x, z):
    pid = plot_id(x, z)
    return [pid[0] * (x_plot_size + padding), pid[1] * (z_plot_size + padding)]

def bounds(x, z):
    base = base_coords(x, z)
    return [base, [base[0] + x_plot_size, base[1] + z_plot_size]]

def plot_id(x, z):
    return [x // (x_plot_size + padding), z // (z_plot_size + padding)]


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
