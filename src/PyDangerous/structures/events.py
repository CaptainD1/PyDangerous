from datetime import datetime, timezone

from structures.exploration.bodies import SimpleBody, System

class EliteEvent:

    def __init__(self, source, dictionary):
        self.timestamp = datetime.strptime(dictionary["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        self.name = dictionary["event"].lower()
        self.source = source

        self.json = dictionary

    def __getitem__(self, key):
        return self.json[key]

    def __contains__(self, item):
        return item in self.json

class ScanEvent(EliteEvent):

    def __init__(self, source, dictionary):
        super().__init__(source, dictionary)
        self._system, self._body = System.from_body_data(dictionary)

    @property
    def body(self):
        return self._body

    @property
    def system(self):
        return self._system