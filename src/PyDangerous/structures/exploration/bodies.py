from abc import abstractmethod
from dataclasses import dataclass

@dataclass
class Body:
    """Class containing generic data representing a stellar body"""
    name: str
    id: int
    system_name: str
    system_address: str
    mass: float
    radius: float
    arrival_distance_ls: float
    rotation_period: float

    def __init__(self, data):
        self.system = data["Star System"]
        self.system_address = data["SystemAddress"]
        self.name = data["Bodyname"]
        self.id = data["BodyID"]
        self.arrival_distance_ls = data["DistanceFromArrivalLS"]
        self.mass = 0 # TODO: calculate
        self.radius = 0 # TODO: calculate
        self.rotation_period = data["RotationPeriod"]

    @property
    @abstractmethod
    def mass(self):
        pass

    @property
    @abstractmethod
    def radius(self):
        pass