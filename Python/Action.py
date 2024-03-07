"""
File describing actions contestants can take during a fight
"""

from enum import Enum
from common import BodyPart


class Range(Enum):
    NULL = 0
    PUNCH = 1
    KICK = 2
    PUSH_KICK = 3
    OUT_OF_RANGE = 4


# Tags describing each action
class ActionTag:
    current_id = 0

    def __init__(self):
        self.id = ActionTag.get_unique_id()

    @classmethod
    def get_unique_id(cls):
        old_id = cls.current_id
        cls.current_id += 1
        return old_id


class AttackTag(ActionTag):
    pass


class ReactionTag(ActionTag):
    pass


class _ActionInterface:

    def __init__(
        self,
        target_body_locations,
        init_weight_distribution,
        final_weight_distribution,
        weight_distribution_necessity,
        likely_vulnerabilites_after_execution,
        range,
        tags: set(),
        name="",
    ):
        # target locations of each involved body part. doubles as a way to check for body parts involved
        self.target_body_locations = target_body_locations
        # init weight distribution required
        self.init_weight_distribution = init_weight_distribution
        # final weight dist
        self.final_weight_distribution = final_weight_distribution
        # list of likely vulnerability id's exposed on contestant
        self.likely_vulnerabilites_after_execution = (
            likely_vulnerabilites_after_execution
        )
        self.range = range
        # tags: describes this action (e.g. weave=non-contact dodge reaction) or light/fast vs slow/heavy
        self.tags = tags
        # how necessary is it that contestant is in a certain position?
        self.weight_distribution_necessity = weight_distribution_necessity
        self.name = name

    # Returns true if this action uses <body_part> of contestant in execution.
    def involves_part(self, body_part: BodyPart):
        return body_part in self.target_body_locations.keys()


class AttackImpl(_ActionInterface):
    def __init__(
        self,
        target_body_locations,
        init_weight_distribution,
        final_weight_distribution,
        weight_distribution_necessity,
        likely_vulnerabilites_after_execution,
        range,
        tags,
        name="",
    ):
        super().__init__(
            target_body_locations,
            init_weight_distribution,
            final_weight_distribution,
            weight_distribution_necessity,
            likely_vulnerabilites_after_execution,
            range,
            tags,
            name,
        )

    # impact function (how hard this attack hit)
    # calc impact proportional to weight distr diff movement of body parts
    def impact(self, weight_shifted, distance_travelled):
        pass

    pass


class ReactionImpl(_ActionInterface):
    def __init__(
        self,
        target_body_locations,
        init_weight_distribution,
        final_weight_distribution,
        weight_distribution_necessity,
        likely_vulnerabilites_after_execution,
        range,
        tags,
        name="",
    ):
        super().__init__(
            target_body_locations,
            init_weight_distribution,
            final_weight_distribution,
            weight_distribution_necessity,
            likely_vulnerabilites_after_execution,
            range,
            tags,
            name,
        )

    pass


class ComboImpl(_ActionInterface):
    def __init__(self, actions: list, name="", range=None):
        self.actions = actions
        # get all target locations of all actions
        self.target_body_locations = {}
        # get all likely vulnerabilities after execution
        self.likely_vulnerabilites_after_execution = []
        # get all tags of all actions
        self.tags = []
        # get the action whose weight distr matters the most. set init and final weight distr to that action
        most_weighted_action = actions[0]
        calculated_range = Range.NULL
        for action in actions:
            for body_part, loc in action.target_body_locations.items():
                self.target_body_locations[body_part] = loc
            if (
                action.weight_distribution_necessity
                >= most_weighted_action.weight_distribution_necessity
            ):
                most_weighted_action = action
            if action.range.value > calculated_range.value:
                calculated_range = action.range
            self.likely_vulnerabilites_after_execution.extend(
                action.likely_vulnerabilites_after_execution
            )
            self.tags.extend(action.tags)
        self.init_weight_distribution = most_weighted_action.init_weight_distribution
        self.final_weight_distribution = most_weighted_action.final_weight_distribution
        self.weight_distribution_necessity = (
            most_weighted_action.weight_distribution_necessity
        )
        # get the range of the combo
        self.range = calculated_range
        if range:
            self.range = range
        self.name = name


# map each action to other actions as well as it's similarity to that other action
action_ambiguity_map = None
