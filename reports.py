from helpers import *
import simplejson as json
import time
import thread

reports_filename = "plugins/redstoner-utils.py.dir/files/reports.json"
time_format      = "%Y.%m.%d %H:%M"
reports          = []
check_reports    = True
check_delay      = 60*10 # seconds
try:
  reports = json.loads(open(reports_filename).read())
except Exception, e:
  error("Failed to load reports: %s" % e)

def printHelp(sender):
  msg(sender, " &2/report <text> &eReport something")
  msg(sender, " &2/rp list          &eList unresolved reports (id, player, text)")
  msg(sender, " &2/rp tp <id>      &eTeleport to report's location & show details")
  msg(sender, " &2/rp del <id>     &eResolve a report")

def printList(sender):
  msg(sender, "&a" + str(len(reports)) + " reports:")
  for i, report in enumerate(reports):
    msg(sender, "&8[&e" + str(i) + " &c" + report['time'] + "&8] &3" + report['player'] + "&f: &a" + report['msg'])

def tp(sender, rep_id):
  if rep_id >= len(reports) or rep_id < 0:
    msg(sender, "&cReport &3#" + str(rep_id) + "&c does not exist!")
    return True
  else:
    report = reports[rep_id]
    safetp(sender, server.getWorld(report['world']), report['x'], report['y'], report['z'], report['yaw'], report['pitch'])
    msg(sender, "&aTeleported to report #%s" % rep_id )


def deleteReport(sender, rep_id):
  report = reports.get(rep_id)
  if report:
    reports.pop(rep_id)
    saveReports()
    msg(sender, "&aReport #%s deleted." % rep_id)
    reporter = server.getOfflinePlayer(report['player'])
    plugHeader(reporter, "Report")
    msg(reporter, "&aReport '&e%s&a' was resolved by %s." % (report['msg'], sender.getName()))
  else:
    msg(sender, "&cThat report does not exist!")

def saveReports():
  try:
    reports_file = open(reports_filename, "w")
    reports_file.write(json.dumps(reports))
    reports_file.close()
  except Exception, e:
    error("Failed to write reports: " + str(e))

@hook.command("rp")
def onRpCommand(sender, args):
  if sender.hasPermission("utils.rp"):
    plugHeader(sender, "Reports")
    if len(args) > 0:
      if args[0] == "list":
        printList(sender)
      else:
        if not checkargs(sender, args, 2, 2):
          return True
        try:
          repid = int(args[1])
        except ValueError:
          msg(sender, "&cDoesn't look like &3" + args[1] + "&c is a valid number!")
          printHelp(sender)
          return True
        if args[0] == "tp":
          if not isPlayer(sender):
            msg(sender, "&conly players can do this")
            return True
          tp(sender, repid)
        elif args[0] == "del":
          deleteReport(sender, repid)
        else:
          printHelp(sender)
    else:
      printHelp(sender)
  else:
    noperm(sender)
  return True

@hook.command("report")
def onReportCommand(sender, args):
  plugHeader(sender, "Report")
  if not isPlayer(sender):
    msg(sender, "&conly players can do this")
    return True
  if not checkargs(sender, args, 1, -1):
    return True
  text = " ".join(args)
  loc = sender.getLocation()
  reporter = sender.name
  report = {
    'player': reporter,
    'msg': text,
    'x': int(loc.x),
    'y': int(loc.y),
    'z': int(loc.z),
    'yaw': int(loc.yaw),
    'pitch': int(loc.pitch),
    'world': loc.getWorld().name,
    'time': time.strftime(time_format)
  }
  reports.append(report)
  saveReports()
  broadcast("utils.rp", "&aReport #" + str(len(reports) -1) + ": " + reporter + "&f: " + text)
  msg(sender, "&aReported \"&e" + text + "&a\"")
  return True

def checkForReports(): # needs 2 args for unknown reason
  while True:
    for i in range(0, check_delay*2):
      time.sleep(0.5) # check every 0.5 seconds if we should kill the thread
      if not check_reports:
        log("Reports reminder thread killed.")
        thread.exit()
    if len(reports) > 0:
      broadcast("utils.rp", "&2--=[ Reports ]=--")
      broadcast("utils.rp", "&aThere are %s pending reports!" % len(reports))

def stopChecking():
  global check_reports
  log("Ending reports reminder thread")
  check_reports = False

thread.start_new_thread(checkForReports, ())
