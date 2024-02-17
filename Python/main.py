"""
Main program logic of the fight sim
"""

import numpy as np
import hashlib
from Action import Action


class Contestant:
    # init vars:
    # Learn rate (param): How quick probabilites are updated
    # Caution (param): How much weight my knowledge bank emptiness has in my
    # aggressiveness.
    # Ambiguity map: Map every action this contestant knows to how ambiguous it is when
    # executed. If none it's randomly generated
    # Perception: Single number determining if a contestant misinterprets an ambiguous
    # action. The lower the perception the more likely vision encounters interference
    # like random noise
    # Range: Used to determine hand and leg reach.
    # action commitment precision (each action can have too little or too much
    # commitment causing constestant to 'overdo' it based on this param)
    # defensive mistake likelihood: How likely are you to drop hands or put hands in a
    # place you think it's covered while it's not. Every action you take that moves
    # your body has a chance to keep those body parts near or close to that location or
    # be slow to bring it back
    # mobility: Contestant likeliness to move after attacking or while idling. How
    # roundabout is the contestants path to opponent
    # Stamina: All actions have cost, stamina contantly replenishing but max stamina
    # constantly decreasing. Getting hit reduces max stamina. When low return to normal
    # (arms protecting face) is slower
    # Health: Each body part has a health bar. When the health of a part is lowered all
    # actions using that parts probabilites reduce
    # Personality: actions can have tags. List of weights for each tag that will be
    # applied to action probability

    # private vars:
    # map each attack to reaction and probability of selecting that action. Every time
    # that reaction is successfull it becomes slightly more likely
    # % weight on left and right feet (weight distr)
    # Knowledge bank:
    # - When I used this attack, what was opp reaction? Used to generate new combos based on learn rate
    # - Seeing a sequence of attacks (combo) makes the reactions to subsequent attacks
    # faster based on learn rate if the same sequence plays out
    # Vulnerabilites: Bit map to which parts of the contentants body is exposed at the
    # moment
    # Vision: Bit map to which parts of opps body contestant can see at the moment. If
    # I can see other fighters torso I can calculate his weight distr
    # Body position each opp. it's updated every frame. if reaction time (time btw
    # motion start and when this contestant finally is able to react) has passed and
    # that action is still happening, start reacting. if that action stops, we can
    # decide what to do from there

    # functions:
    # reaction time function is an oscillating bell curve some min and max where
    # the height of the curve is inversely proportional to the speed of oscillation
    # choose action (multiple can be chosen if they have distinct body parts)
    # - defensive mistake stat factors into, with ambiguity and perception, that chance
    # of picking the wrong reaction
    # personalize action (maybe some ppl perform certain actions faster/slower)
    # perception_update: if head is turned from a hit then depending on how far it
    # turned vulnerabilities starting from the other side of the opponents body cant be
    # seen. Or if a punch is coming at our forehead a circle is draw till it fill the
    # entire screen and vulnerabilites behind it can't be perceived.
    pass


# make this a function
def fight(contestants: list, seed: str):
    pass


def string_to_32bit_int(input_string):
    # Use the hashlib library to get a hash object
    hash_object = hashlib.md5(input_string.encode())
    # Get the hexadecimal representation of the hash
    hex_digest = hash_object.hexdigest()
    # Convert the hexadecimal string to a 32-bit integer
    hash_int = int(hex_digest, 16) & 0xFFFFFFFF  # Use bitwise AND to limit to 32 bits
    return hash_int


# Goal 2 contestants body sparring in a rock paper scissors type situation.
# e.g. jab > teep > cross? idk
if __name__ == "__main__":
    hash_str = "Hello world!"

    seed = string_to_32bit_int(hash_str)
    np.random.seed(seed)
    print(seed)
