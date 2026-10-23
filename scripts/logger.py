# WindowTracker logger v1.1
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import time
import json
import os
import signal
import sys

LOG_FILE = os.path.expanduser("~/.window_activity.jsonl")

def log_system_event(event_type):
    timestamp = time.time()
    log_entry = json.dumps([timestamp, "__SYSTEM__", event_type])
    try:
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
        print(f"Logged system event: {event_type}")
    except Exception as e:
        print(f"Error logging system event: {e}")

class ActiveWindowLogger(dbus.service.Object):
    def __init__(self):
        bus_name = dbus.service.BusName('kwin.windowtracker', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/Logger')

    @dbus.service.method('kwin.windowtracker', in_signature='ss')
    def Log(self, app_class, title):
        timestamp = time.time()
        log_entry = json.dumps([timestamp, app_class, title])

        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")

        print(f"Logged: {log_entry}")

    @dbus.service.method('kwin.windowtracker', in_signature='', out_signature='s')
    def Ping(self):
        return "ok"

def handle_shutdown(signum, frame):
    print("Received shutdown signal. Logging shutdown event...")
    log_system_event("Shutdown")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    log_system_event("Startup")

    DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()
    logger = ActiveWindowLogger()
    print(f"Listening for window events... Logging to {LOG_FILE}")

    try:
        loop.run()
    except KeyboardInterrupt:
        handle_shutdown(None, None)
