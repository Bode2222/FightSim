"""
Every possible action that can be taken.
"""

import sys
import os

# dir = os.path.dirname(bpy.data.filepath)
dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)

from enum import Enum
from common import BodyPart, Location
from Action import AttackImpl, ReactionImpl, Range, AttackTag, ReactionTag, ComboImpl

Tag = {
    "QUICK": AttackTag(),
    "LIGHT": AttackTag(),
    "HEAVY": AttackTag(),
    "STRAIGHT_PATH": AttackTag(),
    "NON_CONTACT": ReactionTag(),
    "CONTACT": ReactionTag(),
    "RETURN": ReactionTag(),
}


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
        tags=[Tag["QUICK"], Tag["LIGHT"], Tag["STRAIGHT_PATH"]],
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
        tags=[Tag["CONTACT"], Tag["QUICK"]],
        name="parry jab",
    ),
    "RETURN_HAND_L_LOW_GUARD": ReactionImpl(
        target_body_locations={BodyPart.HAND_L: Location.CHEEK_L},
        init_weight_distribution=(50, 50),
        final_weight_distribution=(50, 50),
        weight_distribution_necessity=0,
        likely_vulnerabilites_after_execution=[Location.FOREHEAD],
        range=Range.NULL,
        tags=[Tag["RETURN"], Tag["QUICK"], Tag["NON_CONTACT"]],
        name="return hand",
    ),
}


Movement = {
    "STEP": ReactionImpl(
        target_body_locations={BodyPart.FOOT_L: Location.FOOT_L_OUTSIDE},
        init_weight_distribution=(50, 50),
        final_weight_distribution=(50, 50),
        weight_distribution_necessity=0,
        likely_vulnerabilites_after_execution=[],
        range=Range.NULL,
        tags=[Tag["QUICK"]],
        name="step",
    ),
    "STEP_ACROSS_BODY": ReactionImpl(
        target_body_locations={BodyPart.FOOT_L: Location.FOOT_R_OUTSIDE},
        init_weight_distribution=(50, 50),
        final_weight_distribution=(50, 50),
        weight_distribution_necessity=0,
        likely_vulnerabilites_after_execution=[],
        range=Range.NULL,
        tags=[Tag["QUICK"]],
        name="step across body",
    ),
}

Combo = {
    "STEP_JAB_HEAD": ComboImpl([Movement["STEP"], Attack["JAB_HEAD"]], "step jab head"),
}


# map each action to other actions as well as it's similarity to that other action
action_ambiguity_map = None
