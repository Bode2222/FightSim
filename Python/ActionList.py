"""
Every possible action that can be taken.
"""

from enum import Enum
from common import BodyPart, Location
from Action import (
    AttackImpl,
    ReactionImpl,
    Range,
    AttackTag,
    ReactionTag,
)


# Attacks
Attack = {
    "JAB_HEAD": AttackImpl(
        # For attacks the target location is assumed to be a opp contestant BodyLocation
        target_body_locations={BodyPart.HAND_L: Location.CHIN},
        weight_distribution_necessity=0,
        init_weight_distribution=(50, 50),
        final_weight_distribution=(50, 50),
        likely_vulnerabilites_after_execution=[
            Location.RIBS_L_LOW,
            Location.RIBS_L_HIGH,
        ],
        range=Range.PUNCH,
        tags=[AttackTag.QUICK, AttackTag.LIGHT],
        name="jab head",
    )
}


# Reactions
# Nomenclature: name_tagRespondingTo_attackTargetRespondingTo
# TODO: Add reactions for returning body parts to normal locations
Reaction = {
    # Can only trigger if we've reacted and that hand enters range
    "SIDE_PARRY_STRAIGHT_HEAD": ReactionImpl(
        target_body_locations={BodyPart.HAND_R: Location.CHEEK_L},
        init_weight_distribution=(50, 50),
        final_weight_distribution=(50, 50),
        weight_distribution_necessity=0,
        likely_vulnerabilites_after_execution=[
            Location.CHEEK_L,
            Location.RIBS_L_HIGH,
            Location.RIBS_L_LOW,
        ],
        range=Range.NULL,
        tags=[ReactionTag.CONTACT, ReactionTag.QUICK],
        name="parry jab",
    ),
    "RETURN_HAND_L_LOW_GUARD": ReactionImpl(
        target_body_locations={BodyPart.HAND_L: Location.CHEEK_L},
        init_weight_distribution=(50, 50),
        final_weight_distribution=(50, 50),
        weight_distribution_necessity=0,
        likely_vulnerabilites_after_execution=[Location.FOREHEAD],
        range=Range.NULL,
        tags=[ReactionTag.RETURN, ReactionTag.QUICK],
        name="return hand",
    ),
}


# map each action to other actions as well as it's similarity to that other action
action_ambiguity_map = None
