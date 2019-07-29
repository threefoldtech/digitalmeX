

# Copyright (C) 2019 :  TF TECH NV in Belgium see https://www.threefold.tech/
# This file is part of jumpscale at <https://github.com/threefoldtech>.
# jumpscale is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# jumpscale is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License v3 for more details.
#
# You should have received a copy of the GNU General Public License
# along with jumpscale or jumpscale derived works.  If not, see <http://www.gnu.org/licenses/>.


from Jumpscale import j

JSBASE = j.application.JSBaseClass

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import gipc


def monitor_changes_parent(gedis_instance_name):
    gipc.start_process(monitor_changes_subprocess, (gedis_instance_name,))


def monitor_changes_subprocess(gedis_instance_name,):
    """
    js_shell 'j.servers.rack.monitor_changes("test")'
    """
    import time

    print("log: init monitor fs")
    from watchdog.observers import Observer

    connected = False
    while not connected:
        try:
            time.sleep(2)
            cl = j.clients.gedis.get(gedis_instance_name)
            connected = True
        except Exception:
            connected = False

    print("log: gedis connected")

    event_handler = ChangeWatchdog(client=cl)
    observer = Observer()

    res = cl.system.filemonitor_paths()
    for source in res.paths:
        print("log: monitor:%s" % source)
        observer.schedule(event_handler, source, recursive=True)

    print("log: are now observing filesystem changes")

    observer.start()
    print("started")
    try:
        while True:
            time.sleep(2)
            print("filesystem monitor alive")
    except KeyboardInterrupt:
        pass


class ChangeWatchdog(FileSystemEventHandler, JSBASE):
    def __init__(self, client):
        JSBASE.__init__(self)
        self.client = client

    def handler(self, event, action=""):

        print("%s:%s" % (event, action))

        changedfile = event.src_path

        if changedfile.find("/.git/") != -1:
            return
        elif changedfile.find("/__pycache__/") != -1:
            return
        elif changedfile.endswith(".pyc"):
            return

        self.client.system.filemonitor_event(
            is_directory=event.is_directory, src_path=event.src_path, event_type=event.event_type
        )

    def on_any_event(self, event):
        self.handler(event, action="")

    # def on_moved(self, event):
    #     self.handler(event, action="")

    # def on_created(self, event):
    #     self.handler(event)

    # def on_deleted(self, event):
    #     self.handler(event, action="")

    # def on_modified(self, event):
    #     self.handler(event)
