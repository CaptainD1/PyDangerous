import time
import json
from datetime import datetime, timezone
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def main():

    journal_directory = Path.joinpath(Path.home(), "Saved Games", "Frontier Developments", "Elite Dangerous")

    assert Path.exists(journal_directory)

    event_handler = JournalUpdateHandler(journal_directory)

    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break

    event_handler.stop()
    event_handler.join()

def parse_event_dict(event_dict):
    event_dict["timestamp"] = datetime.strptime(event_dict["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    offset = now - event_dict["timestamp"]
    print(f"Event occurred {offset} ago.")

class JournalUpdateHandler(FileSystemEventHandler):

    def __init__(self, journal_directory):
        self._journal_directory = journal_directory
        self._journal_file = None

        self.set_journal(self.get_latest_journal())
        self._journal_file.seek(0, 2)

        self._observer = Observer()
        self._observer.schedule(self, self._journal_directory)
        self._observer.start()

    def __del__(self):
        if self._journal_file:
            self._journal_file.close()

    def set_journal(self, journal_file_path):
        if self._journal_file:
            self._journal_file.close()
        self._journal_file = journal_file_path.open("rt")

    def on_created(self, event):
        if Path.match(event.src_path, "Journal*.log"):
            self.set_journal(event.src_path)

    def on_modified(self, event):
        if Path(self._journal_file.name).samefile(event.src_path):
            self.update_events()

    def stop(self):
        self._observer.stop()

    def join(self):
        self._observer.join()

    def get_latest_journal(self):
        return max(self._journal_directory.glob("Journal*.log"))

    def update_events(self):
        line = self._journal_file.readline().strip()
        while line:
            try:
                data = json.loads(line)
                parse_event_dict(data)
            except json.JSONDecodeError:
                print("Error: Invalid json in log")
                continue

            print(data)
            line = self._journal_file.readline().strip()

if __name__ == "__main__":
    main()