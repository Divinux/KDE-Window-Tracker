import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
import datetime
import json
import os

LOG_FILE = os.path.expanduser("~/.window_activity.jsonl")

class ActiveWindowLogger(dbus.service.Object):
    def __init__(self):
        # Register the service on the session bus
        bus_name = dbus.service.BusName('kwin.windowtracker', bus=dbus.SessionBus())
        dbus.service.Object.__init__(self, bus_name, '/Logger')

    @dbus.service.method('kwin.windowtracker', in_signature='ss')
    def Log(self, app_class, title):
        timestamp = datetime.datetime.now().isoformat()
        log_entry = json.dumps({
            "timestamp": timestamp, 
            "class": app_class, 
            "title": title
        })
        
        with open(LOG_FILE, "a") as f:
            f.write(log_entry + "\n")
            
        print(f"Logged: {log_entry}")

    @dbus.service.method('kwin.windowtracker', in_signature='', out_signature='s')
    def Ping(self):
        return "ok"

if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)
    loop = GLib.MainLoop()
    logger = ActiveWindowLogger()
    print(f"Listening for window events... Logging to {LOG_FILE}")
    loop.run()
