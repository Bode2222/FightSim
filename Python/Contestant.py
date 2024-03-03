"""
This file describes a contestant in a match
"""

import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)
else:
    sys.path.remove(dir)
    sys.path.append(dir)

import numpy as np
from enum import Enum
from common import BodyPart, PhysicsAttr, ConcreteBodyPart, Vec3, Location
from ActionList import Reaction, Attack
from Action import AttackImpl, _ActionInterface
from logger import logger


body_weight_impact_contribution = 0.1


# Action with concrete target locations
class ConcreteAction(_ActionInterface):
    def __init__(self, action: _ActionInterface, locations):
        super().__init__(
            action.target_body_locations,
            action.init_weight_distribution,
            action.final_weight_distribution,
            action.weight_distribution_necessity,
            action.likely_vulnerabilites_after_execution,
            action.range,
            action.tags,
            action.name,
        )
        self.action_locations = locations

    def __repr__(self):
        return f"ConcreteAction (name: {self.name})"


class ContestantState:
    def __init__(self, contestant, action_list):
        self.contestant = contestant
        self.action_list = action_list


class Personlity(Enum):
    # Non contact reactions preferred
    CANT_TOUCH_THIS = 0
    # contact reactions preferred, reduced mobility
    STAND_AND_BANG = 1
    # combos with low committments preferred (i.e. feints)
    FAKER = 2


class Contestant:
    # unique_id for each contestant
    contestant_id = 0
    # Slowest possible time to react is if smth happened <x> frames ago
    MAX_REACTION_TIME = 20

    # everything happens within a max speed. If you need to change course you need to
    # first kill your current momentum then start accelerating to where you need to be
    # at to get there is time
    def __init__(
        self,
        name,
        reaction_time=MAX_REACTION_TIME,
        learn_rate=None,
        caution=None,
        ambiguity=None,
        perception=None,
        range=[],  # l_arm_range, r_arm_range, l_leg_rang, r_leg_range
        commitment_precision=None,
        defensive_mistake_likelihood=None,
        mobility=None,
        stamina=None,
        health=None,
        mass=None,
        personality=None,
        team_affiliation=None,
        body_locations=None,
    ):  # init vars:
        self.id = self.get_unique_id()
        # name
        self.name = name
        # how many time steps need to pass before reaction is possible
        self._reaction_time = reaction_time
        self._min_reaction_time = int(0.5 * reaction_time)
        # Learn rate (param): How quick probabilites are updated
        self._learn_rate = learn_rate
        # Caution (param): How much weight my knowledge bank emptiness has in my
        # aggressiveness.
        self._caution = caution
        # Ambiguity: a handful of likely attacks are randomly selected and the chance
        # of those attacks being misinterpreted are higher. This means the opponent is
        # more likely to react as if something else is thrown. When updating the env,
        # The tags of the action and ambiguity are provided to the environment
        self._ambiguity = ambiguity
        # Perception: Single number determining if a contestant misinterprets an ambiguous
        # action. The lower the perception the more likely vision encounters interference
        # like random noise
        self._perception = perception
        # Range: Used to determine hand and leg reach.
        # self._range = range
        if not range:
            range = (0.7, 0.7, 1, 1)
        assert len(range) == 4, "Range must have 4 items"
        self._range = {
            BodyPart.HAND_L: range[0],
            BodyPart.HAND_R: range[1],
            BodyPart.LEG_L: range[2],
            BodyPart.LEG_R: range[3],
        }
        # action commitment precision (each action can have too little or too much
        # commitment causing constestant to 'overdo' it based on this param)
        self._commitment_precision = commitment_precision
        # defensive mistake likelihood: How likely are you to drop hands or put hands in a
        # place you think it's covered while it's not. Every action you take that moves
        # your body has a chance to keep those body parts near or close to that location or
        # be slow to bring it back
        self._defensive_mistake_likelihood = defensive_mistake_likelihood
        # mobility: Contestant likeliness to move after attacking or while idling. How
        # roundabout is the contestants path to opponent
        self._mobility = mobility
        # Stamina: All actions have cost, stamina contantly replenishing but max stamina
        # constantly decreasing. Getting hit reduces max stamina. When low return to normal
        # (arms protecting face) is slower
        self._stamina = stamina
        # Characters with more mass move slower for bigger attacks like kicking
        self._mass = mass
        # Health: Each body part has a health bar. When the health of a part is lowered all
        # actions using that parts probabilites reduce
        self._health = health
        # Personality: actions can have tags. List of weights for each tag that will be
        # applied to action probability. personality types include cant-touch-this, stand-and
        # bang, heavy-fake-user,
        self._personality = personality
        # team affiliation of this contestant
        self._team_affiliation = team_affiliation
        self.location = Vec3([self.id * 2, 0, 0])

        # private vars:
        # Map from body to
        self.body = {
            ConcreteBodyPart(self.id, BodyPart.HEAD): PhysicsAttr(10),
            ConcreteBodyPart(self.id, BodyPart.TORSO): PhysicsAttr(40),
            ConcreteBodyPart(self.id, BodyPart.HAND_L): PhysicsAttr(4),
            ConcreteBodyPart(self.id, BodyPart.HAND_R): PhysicsAttr(4),
            ConcreteBodyPart(self.id, BodyPart.LEG_L): PhysicsAttr(20),
            ConcreteBodyPart(self.id, BodyPart.LEG_R): PhysicsAttr(20),
        }
        # total mass of body
        self.body_mass = self._calculate_body_mass()

        if not body_locations:
            # this should instead be Vec3's extracted from the ik target
            self.head_loc, self.torso_loc = Vec3(), Vec3()
            self.hand_l_loc, self.hand_r_loc = Vec3(), Vec3()
            self.leg_l_loc, self.leg_r_loc = Vec3(), Vec3()
            self.shoulder_l_loc, self.shoulder_r_loc = Vec3(), Vec3()
        else:
            self.set_body_locations(body_locations)

        # action we are currently executing
        self._current_actions = []
        # stack containing every action from what we last reacted to to what is
        # currently happening
        self._reaction_window = []
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

    def set_body_locations(self, body_locations):
        assert len(body_locations) == 8, "Body must have 8 ik_targets"
        (
            self.head_loc,
            self.torso_loc,
            self.hand_l_loc,
            self.hand_r_loc,
            self.leg_l_loc,
            self.leg_r_loc,
            self.shoulder_l_loc,
            self.shoulder_r_loc,
        ) = body_locations

    # list of info packets
    def update(self, environment_state: list):
        # logger.debug(f'{self.name} update:')
        logger.debug(f"-----------------{self.name}---------------")
        current_actions = []
        self._reaction_window.append(environment_state)

        # Decide the best course of action in the current state
        logger.debug(f"{len(self._reaction_window)} stored reactions")

        # Get the number of reactions to consume this update, decide what moves to make
        def react_to_environment():
            reactions_consumed_this_update = self.get_num_reactions_this_step()
            logger.debug(f"Reactions consumed: {reactions_consumed_this_update}")
            chosen_actions = []
            for _ in range(reactions_consumed_this_update):
                cur_state = self._reaction_window.pop()
                chosen_actions = self.choose_actions(cur_state)
            if chosen_actions:
                current_actions.extend(chosen_actions)
            else:
                chosen_actions = self._current_actions

        # choose what moves to make next
        react_to_environment()
        logger.debug(f"Chosen actions: {current_actions}")
        # return new state
        self._current_actions = current_actions
        return ContestantState(self, self._current_actions)

    # functions:
    # We should be randomly skipping a frame and
    # consuming two frames so we react faster or slower than normal
    # The farther away the reaction window length is from the max length, the more
    # likely we are to skip the current frame
    # We do this to oscillate the reaction time and increase the randomness
    def get_num_reactions_this_step(self):
        reactions_to_consume = 0
        win_len = len(self._reaction_window)
        if win_len < self._min_reaction_time:
            return 0
        if win_len > self._reaction_time:
            reactions_to_consume = self._reaction_time - win_len

        # <min_reaction_time>[x, x, x, _, _, _, _]<max_reaction_time>
        # pick a position in the spots we are allowed to play with within imx and max
        # reaction times. if it's occupied reactions to consume is 0. if it's not
        # reactions to consume is 2
        coin_flip = np.random.randint(0, 3)
        if self.name == "Jack":
            logger.debug(f"coin_flip: {coin_flip}")
        reactions_to_consume += coin_flip
        return reactions_to_consume

    def _calculate_body_mass(self):
        sum = 0
        for phys_attr in self.body.values():
            sum += phys_attr._mass
        return sum

    # TODO: calculate impact based on the striking part and current velocity
    def get_action_impact(self, action: AttackImpl):
        involved_body_parts = action.target_body_parts
        weight_moved = abs(
            action.init_weight_distribution[0] - action.final_weight_distribution[0]
        ) + abs(
            action.init_weight_distribution[1] - action.final_weight_distribution[1]
        )
        total_impact = 0
        for body_part in involved_body_parts:
            total_impact += (
                self.body[body_part]._mass
                * self.body[body_part]._forces[action.id].get_kinematics()[1]
            )

        total_impact += weight_moved * self.body_mass * body_weight_impact_contribution
        return total_impact

    def _body_part_to_neutral_pos(self, part: BodyPart):
        if part == BodyPart.HAND_L:
            return Reaction.RETURN_HAND_L_LOW_GUARD
        else:
            return None

    # limit/modify where we want to hit by range of contestant
    def _get_strike_locations(self, action, victim):
        result = []
        for body_part, loc in action.target_body_locations.items():
            target = Vec3()
            # select target locations
            if loc == Location.CHIN:
                target = Vec3(victim.head_loc)

            # select body locations and limit target locations
            if body_part == BodyPart.HAND_L:
                # limit target by range from shoulder
                new_target = target * 0.7 + self.shoulder_l_loc * 0.3
                target = new_target

            result.append(target)

        # limit each target location by each body part going there
        return result

    @staticmethod
    def location_along_line(a: Vec3, b: Vec3, dist_from_a: float):
        distance_ab = (
            (b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2 + (b[2] - a[2]) ** 2
        ) ** 0.5
        if distance_ab == 0:
            return Vec3()

        # Calculate the direction vector from a to b
        direction_vector = (
            (b[0] - a[0]) / distance_ab,
            (b[1] - a[1]) / distance_ab,
            (b[2] - a[2]) / distance_ab,
        )

        # Scale the direction vector to find the coordinates of point x
        x_coordinates = a[0] + direction_vector[0] * dist_from_a
        y_coordinates = a[1] + direction_vector[1] * dist_from_a
        z_coordinates = a[2] + direction_vector[2] * dist_from_a

        return Vec3([x_coordinates, y_coordinates, z_coordinates])

    # TODO: implement this
    def choose_actions(self, env_state):
        # choose action (multiple can be chosen if they have distinct body parts)
        # overwrite 'replace' actions (actions that move body parts back to their
        # neurtal positions) if necessary
        # - defensive mistake stat factors into, with ambiguity and perception, that chance
        # of picking the wrong reaction
        # perception_update: if head is turned from a hit then depending on how far it
        # turned vulnerabilities starting from the other side of the opponents body cant be
        # seen. Or if a punch is coming at our forehead a circle is draw till it fill the
        # entire screen and vulnerabilites behind it can't be perceived.
        # action execution requires a degree of committment
        # Reactions occur not to attacks, but in response to action tags. A 'jab_parry' can
        # be used not just for jabs, but a spear thrust as well. Any attack that takes a
        # straight path with it's path being safe to touch once the tip is passed can be
        # parried this way but the vulnerabilites are dependent on the weapon after
        # parrying so the attack should carry the exposed vulnerabilites
        # When reacting, the tags that occur most frequently in all the time steps occuring
        # in reaction window are reacted to

        # We are throwing a kick, momentum not too great yet, and we see the opponent
        # start to block. We should switch it to a superman punch combo. or a whip
        # kick into teep feint.
        # I see opponent throwing a kick, check every frame in reaction window to see
        # if it's still comming, if so start reacting.
        # if we are attacking and nothing has changed keep at it
        # # Update the current_actions variable if necessary

        # at this point assume we're targetting myself
        victim = self._select_victim(env_state)  # this is an EnvInfoPacket
        if not victim:
            return None
        strike_location = self._get_strike_locations(
            Attack["JAB_HEAD"], victim.contestant
        )
        return [ConcreteAction(Attack["JAB_HEAD"], strike_location)]

    def _select_victim(self, env_state):
        if len(env_state) < 2:
            return None
        # for now choose a non-me opponent
        potential_victims = [
            victim for id, victim in env_state.items() if id != self.id
        ]

        return potential_victims[0]

    @classmethod
    def get_unique_id(cls):
        old_id = cls.contestant_id
        cls.contestant_id += 1
        return old_id

        pass


class EnvPacketDummy:
    def __init__(self, contestant):
        self.contestant = contestant


def main():
    logger.info("Contestant program start.")

    Jack = Contestant("Jack")
    Jill = Contestant("Jill")

    dummy_info_packet_jack = EnvPacketDummy(Jack)
    dummy_info_packet_jill = EnvPacketDummy(Jill)

    # x = Jack.choose_actions({Jack.id: dummy_info_packet_jack, Jill.id: dummy_info_packet_jill})
    # logger.info(f"action: {x[0].action_locations}")

    Jack.update({Jack.id: dummy_info_packet_jack, Jill.id: dummy_info_packet_jill})

    logger.info("Contestant program end.")


if __name__ == "__main__":
    main()
