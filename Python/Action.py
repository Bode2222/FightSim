"""
File describing actions contestants can take during a fight
"""

from enum import Enum
from common import BodyPart


class Range(Enum):
    PUNCH = 0
    KICK = 1
    PUSH_KICK = 2
    OUT_OF_RANGE = 3
    NULL = 4


# Tags describing each action
class ActionTag:
    QUICK = 0
    current_id = 1

    @classmethod
    def get_unique_id(cls):
        old_id = cls.current_id
        cls.current_id += 1
        return old_id


class AttackTag(ActionTag):
    LIGHT = ActionTag.get_unique_id()
    HEAVY = ActionTag.get_unique_id()
    STRAIGHT_PATH = ActionTag.get_unique_id()


class ReactionTag(ActionTag):
    NON_CONTACT = ActionTag.get_unique_id()
    CONTACT = ActionTag.get_unique_id()
    RETURN = ActionTag.get_unique_id()


class _ActionInterface:

    def __init__(
        self,
        target_body_locations,
        init_weight_distribution,
        final_weight_distribution,
        weight_distribution_necessity,
        likely_vulnerabilites_after_execution,
        range,
        tags,
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
        pass

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
    ):
        super().__init__(
            target_body_locations,
            init_weight_distribution,
            final_weight_distribution,
            weight_distribution_necessity,
            likely_vulnerabilites_after_execution,
            range,
            tags,
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
    ):
        super().__init__(
            target_body_locations,
            init_weight_distribution,
            final_weight_distribution,
            weight_distribution_necessity,
            likely_vulnerabilites_after_execution,
            range,
            tags,
        )

    pass


# map each action to other actions as well as it's similarity to that other action
action_ambiguity_map = None
