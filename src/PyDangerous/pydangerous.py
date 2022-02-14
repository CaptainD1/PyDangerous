import time
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Union
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from structures.events import EliteEvent, ScanEvent
from structures.exploration.bodies import System, Planet

def test_scan_event(event: ScanEvent, output: set):
    if type(event.body) == Planet:
        body: Planet = event.body
        if body.efficient_mapped_value > 200_000:
            output.add(body)

def main():
    now = datetime.utcnow().replace(tzinfo=timezone.utc)

    print(f"Time is: {now.isoformat()}")

    event_handler = EliteAPI()

    output = set()

    event_handler.bind(ScanEvent, lambda event: test_scan_event(event, output))

    systems = System.get_all_systems()

    event_handler.start(rescan=True)

    for body in output:
        print(f"{body.name} - Type: {body.planet_class}, Value: {body.efficient_mapped_value}")

    while False:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    event_handler.stop()
    event_handler.join()

class EliteAPI:

    def __init__(self, journal_directory: Path = None):
        if not journal_directory:
            journal_directory = Path.joinpath(Path.home(), "Saved Games", "Frontier Developments", "Elite Dangerous")

        # TODO: Have proper exception for this
        assert Path.exists(journal_directory)

        self._journal_directory = journal_directory
        self._journal_file = None
        self._bound_events = {}
        self._observer = None

        self.bind("scan", System.from_body_data)

    def __del__(self):
        self.stop()

    class JournalUpdateEventHandler(FileSystemEventHandler):
        def __init__(self, api):
            self._api = api
            self.on_created = api._on_file_created
            self.on_modified = api._on_file_modified

    def _on_file_created(self, event):
        if Path.match(event.src_path, "Journal*.log"):
            self.set_journal(event.src_path)

    def _on_file_modified(self, event):
        if Path(self._journal_file.name).samefile(event.src_path):
            self.update_events()

    def bind(self, event_name: Union[str,type], callback: Callable):
        if type(event_name) == str:
            event_name = event_name.lower()
        if event_name not in self._bound_events:
            self._bound_events[event_name] = set()
        self._bound_events[event_name].add(callback)

    def unbind(self, event_name: Union[str,type], callback: Callable):
        if type(event_name) == str:
            event_name = event_name.lower()
        if event_name in self._bound_events and callback in self._bound_events[event_name]:
            self._bound_events[event_name].remove(callback)

    def set_journal(self, journal_file_path: Path):
        if self._journal_file:
            self._journal_file.close()
        self._journal_file = journal_file_path.open("rt")
        print("Journal file:", journal_file_path)

    def start(self, rescan = False):
        self.set_journal(self.get_latest_journal())
        if rescan:
            self.update_events()
        else:
            self._journal_file.seek(0, 2)

        self._observer = Observer()
        self._observer.schedule(self.JournalUpdateEventHandler(self), self._journal_directory)
        self._observer.start()

    def stop(self):
        if self._journal_file:
            self._journal_file.close()
        if self._observer:
            self._observer.stop()

    def join(self):
        if self._observer:
            self._observer.join()

    def get_latest_journal(self):
        return max(self._journal_directory.glob("Journal*.log"))

    def update_events(self):
        line = self._journal_file.readline().strip()
        while line:
            try:
                data = json.loads(line)
                self.create_event(data)
            except json.JSONDecodeError:
                print("Error: Invalid json in log")
                continue

            line = self._journal_file.readline().strip()

    def invoke(self, event: EliteEvent):
        if event.name in self._bound_events:
            for callback in self._bound_events[event.name]:
                callback(event)
        if type(event) in self._bound_events:
            for callback in self._bound_events[type(event)]:
                callback(event)

    def create_event(self, data):
        if data["event"] == "Scan":
            event = ScanEvent(self, data)
        else:
            event = EliteEvent(self, data)
        
        self.invoke(event)

if __name__ == "__main__":
    main()