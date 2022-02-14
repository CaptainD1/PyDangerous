from datetime import datetime, timezone

class EliteEvent:

    def __init__(self, dictionary):
        self.timestamp = datetime.strptime(dictionary["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        self.name = dictionary["event"].lower()

        self.json = dictionary