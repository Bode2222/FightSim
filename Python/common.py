from enum import Enum


# All info about getting hit
# when I've been hit i need to know which body part was struck, how hard, who
# hit me, which direction is the body part headed
class Hit:
    def __init__(self, body_part_hit, impact, contestant_id, path_tag):
        self.affected_body_part = body_part_hit
        self.impact = impact
        pass


class BodyPart:
    HAND_L = 0
    HAND_R = 1
    LEG_L = 2
    LEG_R = 3
    HEAD = 4
    TORSO = 5


class ConcreteBodyPart:
    def __init__(self, contestant_id, body_part: BodyPart = None):
        self.contestant_id = contestant_id
        self.body_part = body_part


# Every possible place you would want to strike on a contestant
class _LocationImpl:
    current_id = 0

    @classmethod
    def get_unique_id(cls):
        old_id = cls.current_id
        cls.current_id += 1
        return old_id


class HeadVulnerability(_LocationImpl):
    CHIN = _LocationImpl.get_unique_id()
    FOREHEAD = _LocationImpl.get_unique_id()
    CHEEK_L = _LocationImpl.get_unique_id()
    CHEEK_R = _LocationImpl.get_unique_id()
    NOSE = _LocationImpl.get_unique_id()


class TorsoVulnerability(_LocationImpl):
    RIBS_L_HIGH = _LocationImpl.get_unique_id()
    RIBS_L_LOW = _LocationImpl.get_unique_id()
    RIBS_R_HIGH = _LocationImpl.get_unique_id()
    RIBS_R_LOW = _LocationImpl.get_unique_id()
    SOLAR_PLEXUS = _LocationImpl.get_unique_id()


# class that holds all targetable vulnerabilites
class BodyLocations(HeadVulnerability, TorsoVulnerability):
    LEG_L = _LocationImpl.get_unique_id()
    LEG_R = _LocationImpl.get_unique_id()
    pass


# every possible targetable location by an action. superset of vulnerabilities
class Location(BodyLocations):
    LEG_L_OUTSIDE = _LocationImpl.get_unique_id()
    LEG_L_BACK = _LocationImpl.get_unique_id()


# A location as it relates to specific contestants
class ConcreteLocation:
    def __init__(self, contestant_id, loc: Location = None):
        self.contestant_id = contestant_id
        self.location = loc


# keep track of where the direction is going. from contestant to opponent for example
# so when a counter direction comes we can cancel out this direction. for now we'll
# ignore left to right cancellation and only focus on contestant to opp
class Direction:
    def __init__(
        self, initial_loc: ConcreteLocation, final_loc: ConcreteLocation = None
    ):
        self.initial_loc = initial_loc
        self.final_loc = final_loc
        if not final_loc:
            self.final_loc = initial_loc
        self._dir_str = f"{initial_loc.contestant_id}{final_loc.contestant_id}"

    def in_same_axis(self, dir):
        return self._dir_str == dir._dir_str[::-1] or self._dir_str == dir._dir_str

    # if we meet a direction in the same axis, this function will tell us whether we
    # should add the magnitude of that vector or subtract it
    def get_added_velocity_coefficient(self, dir):
        assert self.in_same_axis(dir)
        if self._dir_str == dir._dir_str:
            return 1
        return -1


class Vector:
    def __init__(self, direction: Direction, kinematics: tuple = (0, 0, 0)):
        self.position, self.velocity, self.acceleration = kinematics
        self.direction = direction

    def set_kinematics(self, kinematics):
        self.position, self.velocity, self.acceleration = kinematics

    def get_kinematics(self, kinematics):
        return (self.position, self.velocity, self.acceleration)

    def add_velocity(self, velocity):
        self.velocity += velocity


# An object that has a weight and takes up space (specifically has a location and
# momentum for now)
# forces: List of vectors
class PhysicsAttr:
    def __init__(self, mass: float = 10, forces: list = []):
        self._mass = mass
        self._forces = forces

    def apply_force(self, impact, direction: Direction):
        velocity = impact / self._mass
        # if a force is acting opposite thi
        for force in self._forces:
            if force.direction.in_same_axis(direction):
                force.add_velocity(
                    force.direction.get_added_velocity_coefficient(direction) * velocity
                )
                return
        # else start moving this object at this velocity with no acceleration
        self._forces.append(Vector(direction, (0, velocity, 0)))
