from enum import Enum
import numpy as np


# All info about getting hit
# when I've been hit i need to know which body part was struck, how hard, who
# hit me, which direction is the body part headed
class Hit:
    def __init__(self, body_part_hit, impact, contestant_id, path_tag):
        self.affected_body_part = body_part_hit
        self.impact = impact
        pass


class Vec3:
    def __init__(self, data: list = [0, 0, 0]):
        self._data = data

    @property
    def x(self):
        return self._data[0]

    @property
    def y(self):
        return self._data[1]

    @property
    def z(self):
        return self._data[2]

    @property
    def data(self):
        return self._data

    def __repr__(self):
        return f"Vec3 ({self.__str__()})"

    def __str__(self):
        return f"[{self.x}, {self.y}, {self.z}]"

    def __getitem__(self, index):
        if index > 2:
            raise OutOfBoundsError(f"Vec3 index out of bounds getter: {index}")
        return self._data[index]

    def __setitem__(self, index, value: float):
        if index > 2:
            print("Vec3 index out of bounds setter")
        self._data[index] = value

    def __sub__(self, other):
        return Vec3([self.x - other.x, self.y - other.y, self.z - other.z])

    def __add__(self, other):
        return Vec3([self.x + other.x, self.y + other.y, self.z + other.z])

    def __mul__(self, other):
        if isinstance(other, (float, int)):
            return Vec3([self.x * other, self.y * other, self.z * other])
        else:
            raise ValueError("Figure this out later Bk")

    def magnitude(self):
        return self.x**2 + self.y**2 + self.z**2

    # normalize the vector
    def normalize(self):
        mag = self.magnitude()
        return Vec3([self.x / mag, self.y / mag, self.z / mag])

    @staticmethod
    def close(v1, v2, threshold=0.1):
        return (v1 - v2).magnitude() < threshold


# convert a global position to a position relative to an object's transformation matrix
def global_to_local(glob_pos: Vec3, object_transformation_matrix):
    # Convert the position to a 4x1 matrix
    global_position = glob_pos.data.copy()
    global_position.extend([1])
    global_position_matrix = np.array(global_position).reshape(4, 1)

    # Calculate the inverse of the object's transformation matrix
    inverse_matrix = np.linalg.inv(object_transformation_matrix)

    # Multiply the global position by the inverse matrix
    local_position_matrix = np.dot(inverse_matrix, global_position_matrix)

    # Convert the result back to a Vec3 and return it
    return Vec3(local_position_matrix[:3, 0].tolist())


def local_to_global(local_pos: Vec3, object_transformation_matrix):
    local_position = local_pos.data.copy()
    local_position.extend([1])
    # Convert the position to a 4x1 matrix
    local_position_matrix = np.array(local_position).reshape(4, 1)

    # Multiply the local position by the object's transformation matrix
    global_position_matrix = np.dot(object_transformation_matrix, local_position_matrix)

    # Convert the result back to a Vec3 and return it
    return Vec3(global_position_matrix[:3, 0].tolist())


class BodyPart:
    HAND_L = 0
    HAND_R = 1
    FOOT_L = 2
    FOOT_R = 3
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
    FOOT_L = _LocationImpl.get_unique_id()
    FOOT_R = _LocationImpl.get_unique_id()
    pass


# every possible targetable location by an action. superset of vulnerabilities
class Location(BodyLocations):
    FOOT_OUTSIDE_OFFSET = 0.3
    FOOT_L_OUTSIDE = _LocationImpl.get_unique_id()
    FOOT_R_OUTSIDE = _LocationImpl.get_unique_id()
    FOOT_L_BACK = _LocationImpl.get_unique_id()


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
