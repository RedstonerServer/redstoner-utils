from helpers import *
from java.util.UUID import fromString as juuid
import time
import thread
from traceback import format_exc as trace


time_format   = "%Y.%m.%d %H:%M"
reports       = open_json_file("reports", [])
check_reports = True
check_delay   = 60 * 10 # Every 10 minutes, staff will be notified about pending reports.
rp_permission = "utils.rp"


def print_help(sender):
    msg(sender, " &2/report <text>     &eReport something")
    msg(sender, " &2/rp open            &eList open reports (id, player, text)")
    msg(sender, " &2/rp closed         &eList closed reports (id, player, text)")
    msg(sender, " &2/rp tp <id>         &eTeleport to report's location & show details")
    msg(sender, " &2/rp close <id>     &eResolve an open report")
    msg(sender, " &2/rp reopen <id>   &eReopen a resolved report")
    msg(sender, " &2/rp del <id>        &eDelete a report (admin only)")


def print_list(sender, closed):
    try: # new thread, anything can happen.
        targeted_reports = dict(enumerate(reports))
        for i in list(targeted_reports):
            report = targeted_reports[i]
            if report["closed"] != closed:
                targeted_reports.pop(i)

        msg(sender, "&a%s %s reports:" % (len(targeted_reports), "closed" if closed else "open"))
        for i in targeted_reports:
            report = targeted_reports[i]
            name = retrieve_player(report["uuid"]).getName()
            msg(sender, "&8[&e%s &c%s&8] &3%s&f: &a%s" % (i, report["time"], name, report["msg"]))
    except:
        warn("Failed to complete report's print_list() thread")
        error(trace())


def tp_report(sender, rep_id):
    if rep_id >= len(reports) or rep_id < 0:
        msg(sender, "&cReport &3#" + str(rep_id) + "&c does not exist!")
    else:
        report = reports[rep_id]
        safetp(sender, server.getWorld(report["world"]), report["x"], report["y"], report["z"], report["yaw"], report["pitch"])
        msg(sender, "&aTeleported to %s&areport #%s" % ("&cclosed " if report["closed"] else "", rep_id))


# resolve == True: You're resolving, False: reopening
def resolve_reopen_report(sender, rep_id, resolve):
    action = "resolved" if resolve else "reopened"
    report = edit_report(sender, rep_id)
    if report != None:
        if report["closed"] == resolve:
            msg(sender, "&cReport &3#%s&c was already %s!" % (rep_id, action))
        else:
            report["closed"] = resolve
            save_reports()
            msg(sender, "&aReport #%s %s" % (rep_id, action))
            message_reporter(sender, report, action)


def delete_report(sender, rep_id):
    if not sender.hasPermission(rp_permission + ".del"):
        noperm(sender)
        return
    action = "&cdeleted"
    report = edit_report(sender, rep_id)
    if report != None:
        reports.remove(report)
        save_reports()
        msg(sender, "&aReport #%s %s" % (rep_id, action))
        message_reporter(sender, report, action)


def edit_report(sender, rep_id):
    if len(reports) > rep_id >= 0:
        return reports[rep_id]
    msg(sender, "&cThat report does not exist!")
    return None


def message_reporter(sender, report, action):
    reporter = get_reporter(report)
    message = "&aReport '&e%s&a' was %s &aby %s." % (report["msg"], action, sender.getName())
    if reporter.isOnline():
        plugin_header(reporter, "Reports")
        msg(reporter, message)
    else:
        server.dispatchCommand(sender, "mail send %s %s" % (reporter.getName(), message))


def save_reports():
    save_json_file("reports", reports)


@hook.command("rp")
def on_rp_command(sender, command, label, args):
    if sender.hasPermission(rp_permission):
        plugin_header(sender, "Reports")
        if len(args) > 0:
            if args[0] == "closed":
                # needs to run in seperate thread because of getOfflinePlayer
                thread.start_new_thread(print_list, (sender, True,))
            elif args[0] == "open":
                thread.start_new_thread(print_list, (sender, False,))
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
                elif args[0] == "close":
                    resolve_reopen_report(sender, repid, True)
                elif args[0] == "del":
                    delete_report(sender, repid)
                elif args[0] == "reopen":
                    resolve_reopen_report(sender, repid, False)
                else:
                    print_help(sender)
        else:
            print_help(sender)
    else:
        noperm(sender)
    return True


@hook.command("report")
def on_report_command(sender, command, label, args):
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
        "time": time.strftime(time_format),
        "closed": False
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
        targeted_reports = get_reports(False)
        if len(targeted_reports) > 0:
            broadcast(rp_permission, "&2--=[ Reports ]=--\n&aThere are %s open reports!" % len(targeted_reports))


def stop_reporting():
    global check_reports
    info("Ending reports reminder thread")
    check_reports = False


def get_reports(closed):
    targeted_reports = []
    for report in reports:
        if report["closed"] == closed:
            targeted_reports.add(report)
    return targeted_reports


def get_reporter(report):
    return server.getOfflinePlayer(juuid(report["uuid"]))

thread.start_new_thread(reports_reminder, ())