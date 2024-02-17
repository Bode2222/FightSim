"""
File describing actions contestants can take during a fight
"""

from enum import Enum


# enums
class BodyParts(Enum):
    HAND_L = 0
    HAND_R = 1
    LEG_L = 2
    LEG_R = 3


# every possible targetable location by an action
class Locations(Enum):
    LEG_L_STRIDE = 0
    LEG_L_OUTSIDE = 1
    LEG_L_BACK = 2


class Vulnerabilities(Enum):
    CHIN = 0
    FOREHEAD = 1


class Action:
    # time to peak of action
    # target locations of each involved body part
    # init weight dist required
    # final weight dist
    # Body parts involved
    # list of likely vulnerability id's exposed
    # Range
    # every action execution requires a degree of commital from the contestant
    # impact proportional to weight distr diff movement of body parts
    # attribute: describes this action (e.g. weave=non-contact dodge reaction) or light/fast vs slow/heavy
    pass


class Attack(Action):
    # impact function (how hard this attack hit)
    pass


class Reaction(Action):
    # block type: non-contact or contact
    # final weight dist is dependent on impact of attack
    pass


all_actions = []
# map each action to other actions as well as it's similarity to that other action
action_ambiguity_map = None
