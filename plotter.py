#!/usr/bin/python

"""
*Very basic* start of a custom plot-plugin like PlotMe
on hold because the PlotMe developer continued to develop PlotMe
"""

from helpers import *
from basecommands import simplecommand


@simplecommand("plotter",
    aliases = ["pt"],
    senderLimit = 0,
    description = "Plot commands")
def plotter_command(sender, command, label, args):
    loc = sender.getLocation()
    x = loc.getX()
    z = loc.getZ()
    plot = Plot.get(x, z)

    if plot:
        msg(sender, "id: %s" % [plot.idx, plot.idz])
        msg(sender, "bottom: %s" % [plot.bottomx, plot.bottomz])
        msg(sender, "top: %s" % [plot.topx, plot.topz])
    else:
        msg(sender, "&cThis is not a plot.")

class Plot:
    plot_size   = 20
    padding     = 3
    padded_size = plot_size + padding

    def __init__(self, x, z):
        x = int(x)
        z = int(z)
        self.idx     = x
        self.idz     = z
        self.bottomx = x * self.padded_size
        self.bottomz = z * self.padded_size
        self.topx    = self.bottomx + self.plot_size
        self.topz    = self.bottomz + self.plot_size

    @staticmethod
    def is_border(x, z):
        xborder = Plot.plot_size < x % Plot.padded_size < Plot.padded_size
        zborder = Plot.plot_size < z % Plot.padded_size < Plot.padded_size
        return xborder or zborder

    @staticmethod
    def get(x, z):
        idx = x // Plot.padded_size
        idz = z // Plot.padded_size
        return None if Plot.is_border(x, z) else Plot(idx, idz)
