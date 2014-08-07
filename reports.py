from helpers import *
from java.util.UUID import fromString as juuid
import time
import thread


time_format   = "%Y.%m.%d %H:%M"
reports       = open_json_file("reports", [])
check_reports = True
check_delay   = 60 * 10 # Every 10 minutes, staff will be notified about pending reports.
rp_permission = "utils.rp"


def print_help(sender):
  msg(sender, " &2/report <text> &eReport something")
  msg(sender, " &2/rp list          &eList unresolved reports (id, player, text)")
  msg(sender, " &2/rp tp <id>      &eTeleport to report's location & show details")
  msg(sender, " &2/rp del <id>     &eResolve a report")


def print_list(sender):
  try: # new thread, anything can happen.
    msg(sender, "&a" + str(len(reports)) + " reports:")
    for i, report in enumerate(reports):
      name = retrieve_player(report["uuid"]).getName()
      msg(sender, "&8[&e%s &c%s&8] &3%s&f: &a%s" % (i, report["time"], name, report["msg"]))
  except:
    warn("Failed to complete report's print_list() thread")


def tp_report(sender, rep_id):
  if rep_id >= len(reports) or rep_id < 0:
    msg(sender, "&cReport &3#" + str(rep_id) + "&c does not exist!")
    return True
  else:
    report = reports[rep_id]
    safetp(sender, server.getWorld(report["world"]), report["x"], report["y"], report["z"], report["yaw"], report["pitch"])
    msg(sender, "&aTeleported to report #%s" % rep_id )


def delete_report(sender, rep_id):
  if len(reports) > rep_id >= 0:
    report = reports[rep_id]
    reports.pop(rep_id)
    save_reports()
    msg(sender, "&aReport #%s deleted." % rep_id)
    reporter = server.getOfflinePlayer(juuid(report["uuid"]))
    plugin_header(reporter, "Report")
    msg(reporter, "&aReport '&e%s&a' was resolved by %s." % (report["msg"], sender.getName()))
  else:
    msg(sender, "&cThat report does not exist!")


def save_reports():
  save_json_file("reports", reports)


@hook.command("rp")
def on_rp_command(sender, args):
  if sender.hasPermission(rp_permission):
    plugin_header(sender, "Reports")
    if len(args) > 0:
      if args[0] == "list":
        # needs to run in seperate thread because of getOfflinePlayer
        thread.start_new_thread(print_list, (sender,))
      else:
        if not checkargs(sender, args, 2, 2):
          return True
        try:
          repid = int(args[1])
        except ValueError:
          msg(sender, "&cDoesn't look like &3" + args[1] + "&c is a valid number!")
          print_help(sender)
          return True
        if args[0] == "tp":
          if not is_player(sender):
            msg(sender, "&conly players can do this")
            return True
          tp_report(sender, repid)
        elif args[0] == "del":
          delete_report(sender, repid)
        else:
          print_help(sender)
    else:
      print_help(sender)
  else:
    noperm(sender)
  return True


@hook.command("report")
def on_report_command(sender, args):
  plugin_header(sender, "Report")
  if not is_player(sender):
    msg(sender, "&conly players can do this")
    return True
  if not checkargs(sender, args, 1, -1):
    return True
  text = " ".join(args)
  loc = sender.getLocation()
  reporter = sender.name
  reporter_id = uid(sender)
  report = {
    "uuid": reporter_id,
    "msg": text,
    "x": int(loc.x),
    "y": int(loc.y),
    "z": int(loc.z),
    "yaw": int(loc.yaw),
    "pitch": int(loc.pitch),
    "world": loc.getWorld().name,
    "time": time.strftime(time_format)
  }
  reports.append(report)
  save_reports()
  broadcast(rp_permission, "&aReport #" + str(len(reports) -1) + ": " + reporter + "&f: " + text)
  msg(sender, "&aReported \"&e" + text + "&a\"")
  return True


def reports_reminder(): # needs 2 args for unknown reason
  while True:
    for i in range(0, check_delay*2):
      time.sleep(0.5) # check every 0.5 seconds if we should kill the thread
      if not check_reports:
        info("Reports reminder thread killed.")
        thread.exit()
    if len(reports) > 0:
      broadcast(rp_permission, "&2--=[ Reports ]=--")
      broadcast(rp_permission, "&aThere are %s pending reports!" % len(reports))


def stop_reporting():
  global check_reports
  info("Ending reports reminder thread")
  check_reports = False


thread.start_new_thread(reports_reminder, ())