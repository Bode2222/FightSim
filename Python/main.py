"""
Main program logic of the fight sim
"""

import numpy as np
from utils import string_to_32bit_int
from Contestant import Contestant
from Environment import ContestantState, Environment, EnvInfoPacket


# Main simulation loop. at each time step all contestants are updated and useful info
# is transmitted via a shared EnvironmentState info packet.
def fight(contestants):
    DELTA = 0.2
    TIME_LIMIT = 10

    # Initialize environment
    team_map = {}
    for contestant in contestants:
        team_map[contestant] = contestant.id
    env = Environment(team_map)
    last_env = []
    cur_env = []
    # Update every contestant at each time step
    for i in np.arange(0, TIME_LIMIT, DELTA):
        for contestant in contestants:
            env.update(contestant.update(last_env))

        # set current environment state to last environment state
        last_env = env.current_state()
        cur_env = []

        if env.simulation_is_over():
            break

    return contestants[0].name


# Goal: 2 contestants body sparring in a rock paper scissors type situation.
# e.g. jab > teep > cross? idk
if __name__ == "__main__":
    hash_str = "Hello world!"

    seed = string_to_32bit_int(hash_str)
    np.random.seed(seed)

    Jack = Contestant("Jack", reaction_time=10)
    Jill = Contestant("Jill")
    winner = fight([Jack, Jill])
    print(f"{winner} won!")
