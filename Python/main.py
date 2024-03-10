# This file is the main entry point for the fight sim. It sets up the contestants and
# environment and runs the simulation loop.

# import bpy
import sys
import os

dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)

import numpy as np
import importlib
from utils import string_to_32bit_int
from contestant import Contestant
from environment import Environment as Environment
import contestant, environment
from logger import logger

SIMULATION_FRAME_RATE = 10
ANIMATION_FRAME_RATE = 24


# Main simulation loop. at each time step all contestants are updated and useful info
# is transmitted via a shared EnvironmentState info packet.
def fight(contestants, delta=0.1, time_limit=1):
    DELTA = delta
    TIME_LIMIT = time_limit

    # Initialize environment
    team_map = {}
    for contestant in contestants:
        team_map[contestant] = contestant.id
    env = Environment(
        team_map,
        sim_frame_rate=SIMULATION_FRAME_RATE,
        anim_frame_rate=ANIMATION_FRAME_RATE,
    )
    env_state = []
    # Update every contestant at each time step
    for i in np.arange(0, TIME_LIMIT, DELTA):
        for contestant in contestants:
            env.update(contestant.update(env_state))

        # set current environment state to last environment state
        env_state = env.current_state()

        # draw to screen
        env.draw()

        if env.simulation_is_over():
            break

    return contestants[0].name


# Quick tasks:
# - get test_contestant working
# - make build system
# - ensure I can run the program twice
# - rename action->action_template, comboImpl->combo_template, etc
# - when foot moves move hips to be in center of feet
# - when center of mass moves move feet to be under center of mass
# - getting punched moves rigidbody
# - if we're not facing opponent and we're not taking any action, move left leg to where it needs to be to face the opponent then move right leg.
# - if hand is out of position and we're not taking any actions, return to position
# - create relocate_in_range step action. pick a random close by spot and first move your front foot, then your rear
# - on step across body, make sure back is exposed and everything turns
# - Have fighter randomly pick between relocate in range and jab


# Goal: 2 contestants body sparring in a rock paper scissors type situation.
# e.g. jab > teep > cross? idk
def main():
    # Before we start, we need to reload the Contestant module to reset the global variables
    os.system("cls")
    importlib.reload(contestant)
    importlib.reload(Environment)

    logger.info("Program start")
    hash_str = "Hello world!"

    seed = string_to_32bit_int(hash_str)
    np.random.seed(seed)

    Jack = Contestant("Jack", reaction_time=6)
    Jill = Contestant("Jill", reaction_time=10)

    Jack.id, Jill.id = 1, 2
    winner = fight([Jack, Jill], 0.1, 0.5)
    logger.info(f"{winner} won!")


main()
