from enum import Enum


# All info about getting hit
# when I've been hit i need to know which body part was struck, how hard, who
# hit me, which direction is the body part headed
class Hit:
    def __init__(self, body_part_hit, impact, contestant_id, path_tag):
        self.affected_body_part = body_part_hit
        self.impact = impact
        pass


class BodyPart(Enum):
    HAND_L = 0
    HAND_R = 1
    LEG_L = 2
    LEG_R = 3
    HEAD = 4
    TORSO = 5


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
