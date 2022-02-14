from __future__ import annotations
from abc import abstractmethod
from enum import Enum
from typing import Union

EARTH_MASS = 5.972e24
SOLAR_MASS = 1.98847e30

TerraformState = Enum("TerraformState", "Terraformable Terraforming Terraformed NotTerraformable")

StarClass = Enum("StarClass", "O B A F G K M L T Y TTS AeBe W WN WNC WC WO CS C CN CJ CH CHd MS S D DA DAB DAO DAZ DAV \
    DB DBZ DBV DO DOV DQ DC DCV DX N H X SupermassiveBlackHole A_BlueWhiteSuperGiant F_WhiteSuperGiant M_RedSuperGiant \
    M_RedGiant K_OrangeGiant RoguePlanet Nebula StellarRemnantNebula")

PlanetClass = Enum("PlanetClass", "MetalRich HighMetalContent Rocky Icy RockyIce Earthlike Water Ammonia WaterGiant \
    WaterGiantLife GasGiantWaterLife GasGiantAmmoniaLife GasGiant1 GasGiant2 GasGiant3 GasGiant4 GasGiant5 HeliumRichGiant HeliumGiant")

planet_class_converter = {
    "Metal rich body": PlanetClass.MetalRich,
    "High metal content body": PlanetClass.HighMetalContent,
    "Rocky body": PlanetClass.Rocky,
    "Icy body": PlanetClass.Icy,
    "Rocky ice body": PlanetClass.RockyIce,
    "Earthlike body": PlanetClass.Earthlike,
    "Water world": PlanetClass.Water,
    "Ammonia world": PlanetClass.Ammonia,
    "Water giant": PlanetClass.WaterGiant,
    "Water giant with life": PlanetClass.WaterGiantLife,
    "Gas giant with water based life": PlanetClass.GasGiantWaterLife,
    "Gas giant with ammonia based life": PlanetClass.GasGiantAmmoniaLife,
    "Sudarsky class I gas giant": PlanetClass.GasGiant1,
    "Sudarsky class II gas giant": PlanetClass.GasGiant2,
    "Sudarsky class III gas giant": PlanetClass.GasGiant3,
    "Sudarsky class IV gas giant": PlanetClass.GasGiant4,
    "Sudarsky class V gas giant": PlanetClass.GasGiant5,
    "Helium rich gas giant": PlanetClass.HeliumRichGiant,
    "Helium gas giant": PlanetClass.HeliumGiant
}

class OrbitalData:
    """Representation of orbit data for a scanned body."""

    def __init__(self, data: dict):
        self._semimajor_axis = data["SemiMajorAxis"]
        self._eccentricity = data["Eccentricity"]
        self._orbital_inclination = data["OrbitalInclination"]
        self._periapsis = data["Periapsis"]
        self._orbital_period = data["OrbitalPeriod"]
        self._rotation_period = data["RotationPeriod"]

class Barycenter:
    """Represents a barycenter for multiple objects orbiting one another"""

    def __init__(self, id):
        self._id = id

class SimpleBody:
    """Generic representation of a stellar body from scan data."""

    def __init__(self, data: dict = None):
        self.raw_data = data

        if(data):
            self.update(data)

    def update(self, data: dict):
        self.raw_data = data

        self._system = System.get_system(data["StarSystem"], data["SystemAddress"])
        self._name = data["BodyName"]
        self._id = data["BodyID"]
        self._arrival_distance_ls = data["DistanceFromArrivalLS"]
        self._was_discovered = data["WasDiscovered"]
        self._was_mapped = data["WasMapped"]

        if "Parents" in data:
            pass
            self._parents = [self.system.get_body_by_id(id, type) for parent in data["Parents"] for type, id in parent.items()]
        else:
            self._parents = []

        if "SemiMajorAxis" in data: # TODO: Better check?
            self._orbit = OrbitalData(data)
        else:
            self._orbit = None

    @property
    def system(self) -> System:
        """The system the body resides in."""
        return self._system

    @property
    def name(self) -> str:
        """The name of the body."""
        return self._name

    @property
    def id(self) -> int:
        """The id of the body."""
        return self._id

    @property
    def arrivial_distance_ls(self) -> float:
        """The distance from arrivial in light seconds."""
        return self._arrival_distance_ls

    @property
    def was_discovered(self) -> bool:
        """Whether this body was already discovered before this scan."""
        return self._was_discovered

    @property
    def was_mapped(self) -> bool:
        """Whether this body was already mapped before this scan."""
        return self._was_mapped

    @property
    def parents(self) -> list[Body]:
        """The list of parent bodies this body is orbiting."""
        return self._parents

    @property
    def orbit(self) -> OrbitalData:
        """The orbital data of the body, or None if the main star."""
        return self._orbit

    @property
    @abstractmethod
    def mass(self) -> float:
        """Mass of body in kilograms. Maybe it should be megatons?"""
        pass

class Body(SimpleBody):

    def __init__(self, data: dict = None):
        super().__init__(data)
        if data:
            self.update(data)

    def update(self, data: dict):
        super().update(data)
        self._rotation_period = data["RotationPeriod"]
        self._radius = data["Radius"]
        self._surface_temperature = data["SurfaceTemperature"]
        self._axial_tilt = data["AxialTilt"]

    @property
    def rotation_period(self) -> float:
        """The rotational period of the body in seconds."""
        return self._rotation_period

    @property
    def radius(self) -> float:
        """The radius of the body in (unknown units. kms?)"""
        return self._radius

    @property
    def surface_temperature(self) -> float:
        """The surface temperature of the body in Kelvin."""
        return self._surface_temperature

    @property
    def axial_tilt(self) -> float:
        """The axial tilt of the body."""
        return self._axial_tilt

class Star(Body):
    """Representation of a star from scan data."""

    def __init__(self, data: dict = None):
        super().__init__(data)
        if data:
            self.update(data)

    def update(self, data: dict):
        super().update(data)
        self._absolute_magnitude = data["AbsoluteMagnitude"]
        self._star_type = StarClass[data["StarType"]]
        self._subclass = data["Subclass"] # TODO: Figure out what this is
        self._age = data["Age_MY"]
        self._luminosity = data["Luminosity"]
        self._mass = data["StellarMass"] * SOLAR_MASS

    @property
    def absolute_magnitude(self) -> float:
        return self._absolute_magnitude

    @property
    def star_type(self) -> StarClass:
        return self._star_type

    @property
    def subclass(self) -> int:
        return self._subclass

    @property
    def age(self) -> float:
        """Age of the star in millions of years."""
        return self._age

    @property
    def luminosity(self) -> str:
        return self._luminosity

    @property
    def mass(self) -> float:
        return self._mass

    @property
    def stellar_mass(self) -> float:
        return self._mass / SOLAR_MASS

    @property
    def value(self) -> int:
        return get_body_value(get_base_value(self.star_type), self.stellar_mass, not self.was_discovered, False, not self.was_mapped, False, True, False)

class Planet(Body):
    """Representation of a planet or moon from scan data."""

    def __init__(self, data: dict = None):
        super().__init__(data)
        if data:
            self.update(data)

    def update(self, data: dict):
        super().update(data)
        self._tidal_lock = data["TidalLock"]
        self._terraform_state = TerraformState[data["TerraformState"]] if data["TerraformState"] else TerraformState.NotTerraformable
        self._planet_class = planet_class_converter[data["PlanetClass"]]
        self._atmosphere = data["Atmosphere"] # TODO: Properly handle atmosphere, including AtmosphereComposition (list of dicts) and AtmosphereType
        self._volcanism = data["Volcanism"] # TODO: Convert to Enum/bool
        self._mass = data["MassEM"] * EARTH_MASS
        self._surface_gravity = data["SurfaceGravity"]
        self._surface_pressure = data["SurfacePressure"]
        self._landable = data["Landable"]

    @property
    def tidal_lock(self) -> bool:
        return self._tidal_lock

    @property
    def terraform_state(self) -> TerraformState:
        return self._terraform_state

    @property
    def planet_class(self) -> PlanetClass:
        return self._planet_class

    @property
    def atmosphere(self) -> str:
        return self._atmosphere

    @property
    def volcanism(self) -> str:
        return self._volcanism

    @property
    def mass(self) -> float:
        return self._mass

    @property
    def surface_gravity(self) -> float:
        return self._surface_gravity

    @property
    def surface_pressure(self) -> float:
        return self._surface_pressure

    @property
    def landable(self) -> bool:
        return self._landable

    @property
    def mass_em(self) -> float:
        return self._mass / EARTH_MASS

    def get_value(self, mapped = True, efficient = True) -> int:
        return get_body_value(get_base_value(self.planet_class), self.mass_em, not self.was_discovered, mapped, not self.was_mapped, efficient, True, False)

    @property
    def unmapped_value(self) -> int:
        return self.get_value(False)

    @property
    def efficient_mapped_value(self) -> int:
        return self.get_value()

    @property
    def inefficient_mapped_value(self) -> int:
        return self.get_value(True, False)

class System:
    """Representation of a star system from cumulative scan data."""

    __initializedSystems = dict()

    @staticmethod
    def get_system(system_name: str, system_address: int) -> System:
        """Return the specified system if it exists, or create a new one and return it if not."""
        if system_address not in System.__initializedSystems:
            return System(system_name, system_address)
        return System.__initializedSystems[system_address]
    
    @staticmethod
    def __getitem__(system_address: int) -> System:
        """Return the specified system."""
        return System.__initializedSystems[system_address]

    @staticmethod
    def from_body_data(body_scan: dict) -> tuple[System, SimpleBody]:
        address = body_scan["SystemAddress"]
        system_name = body_scan["StarSystem"]
        system = System.get_system(system_name, address)
        return system, system.construct_body(body_scan)

    @staticmethod
    def get_all_systems():
        return System.__initializedSystems

    def __init__(self, system_name: str, system_address: int):

        self._system_name = system_name
        self._system_address = system_address
        self._main_bodies = []
        self._bodies = dict()

        System.__initializedSystems[system_address] = self

    def add_body(self, body: SimpleBody, id: int, is_main: bool):
        self._bodies[id] = body
        if is_main:
            self._main_bodies.append(body)

    def construct_body(self, body_data: dict) -> SimpleBody:
        id = body_data["BodyID"]
        if "StarType" in body_data:
            body_type = "Star"
        elif "PlanetClass" in body_data:
            body_type = "Planet"
        else:
            body_type = "Ring" # Can also be Null
        body = self.get_body_by_id(id, body_type)
        body.update(body_data)
        if "Parents" not in body_data: # TODO: Better parent assignment
            self._main_bodies.append(body)
        
        return body

    def get_body_by_id(self, id: int, body_type: str):
        if id not in self._bodies:
            if body_type == "Star":
                self._bodies[id] = Star()
            elif body_type == "Planet":
                self._bodies[id] = Planet()
            elif body_type == "Ring":
                self._bodies[id] = SimpleBody()
            else:
                self._bodies[id] = Barycenter(id)
        return self._bodies[id]

def get_body_value(base_value: int, mass: float, is_first_discoverer: bool, is_mapped: bool, is_first_mapped: bool, with_efficiency_bonus: bool, is_odyssey: bool, is_fleet_carrier_sale: bool):
    """Calculates the cartographic value of a body.
    
    Adapted from https://forums.frontier.co.uk/threads/exploration-value-formulae.232000/
    """

    q = 0.56591828
    mapping_multiplier = 1
    if(is_mapped):
        if(is_first_discoverer and is_first_mapped):
            mapping_multiplier = 3.699622554
        elif is_first_mapped:
            mapping_multiplier = 8.0956
        else:
            mapping_multiplier = 3.3333333333
    
    value = (base_value + base_value * q * mass**0.2) * mapping_multiplier

    if is_mapped:
        if is_odyssey:
            value += value * 0.3 if ((value * 0.3) > 555) else 555
        if with_efficiency_bonus:
            value *= 1.25

    value = max(500, value)
    value *= 2.6 if is_first_discoverer else 1
    value *= 0.75 if is_fleet_carrier_sale else 1

    return int(round(value))

def get_base_value(body_type: Union[StarClass,PlanetClass], terraform_state: TerraformState = TerraformState.NotTerraformable):
    if type(body_type) == PlanetClass:
        if body_type == PlanetClass.MetalRich:
            return 21790
        if body_type == PlanetClass.Ammonia:
            return 96932
        if body_type == PlanetClass.GasGiant1:
            return 1656
        if body_type in (PlanetClass.GasGiant2, PlanetClass.HighMetalContent):
            if terraform_state == TerraformState.NotTerraformable:
                return 9654
            else:
                return 100677
        if body_type in (PlanetClass.Water, PlanetClass.Earthlike):
            if terraform_state == TerraformState.NotTerraformable:
                return 64831
            else:
                return 116295
        else:
            if terraform_state == TerraformState.NotTerraformable:
                return 300
            else:
                return 93328
    elif type(body_type) == StarClass:
        if body_type in (StarClass.N, StarClass.H, StarClass.SupermassiveBlackHole):
            return 22628
        if body_type in (StarClass.D, StarClass.DA, StarClass.DAB, StarClass.DAO, StarClass.DAZ, StarClass.DAV, StarClass.DB,
                StarClass.DBZ, StarClass.DBV, StarClass.DO, StarClass.DOV, StarClass.DQ, StarClass.DC, StarClass.DCV, StarClass.DX):
            return 14057
        else:
            return 1200
    else:
        raise ValueError(f"body_type should be either StarClass or PlanetClass, not {type(body_type)}")