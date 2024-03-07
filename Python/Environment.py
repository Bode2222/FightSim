import sys
import os

dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)

from Blender.PoseEngine import PoseEngine, IKSkeleton, PhysAnimSkeleton
import Blender.PoseEngine
from Contestant import ContestantState
from logger import logger
import importlib, Contestant

importlib.reload(Contestant)
importlib.reload(Blender.PoseEngine)


# Information about a contestant in a step. Works on a 'per-contestant' basis
class EnvInfoPacket:
    def __init__(self, contestant, action_tags=[], hits=[]):
        self.contestant = contestant
        self._action_tags = action_tags
        self._hits = hits
        # extra info needed to choose an action added to info packet here
        # stuff like positions, momentums, etc
        pass


# takes in contestant states as input to update()
# gives out info packets as as output to info()
class Environment:
    def __init__(self, contestant_team_map, sim_frame_rate=10, anim_frame_rate=24):
        self.contestant_team_map = contestant_team_map
        self._sim_frame_rate = sim_frame_rate
        self._anim_frame_rate = anim_frame_rate
        self._game_over = False

        # Make space for the info packet of each contestant
        self._info_packets = {}
        self.clear_info_packets()

        contestants = contestant_team_map.keys()
        # instantiate engine to handle skeleton posing
        self._pose_engine = PoseEngine(contestants, sim_frame_rate, anim_frame_rate)

        # Give each contestant an Ik skeleton and a PhysAnim skeleton
        for contestant in contestants:
            body_locations = self._pose_engine.get_contestant_ik_target_locations(
                contestant
            )
            contestant.set_body_locations(body_locations)

    def update(self, contestant_state: ContestantState):
        contestant = contestant_state.contestant
        actions = []
        strike_attempts = {}

        # store action tags
        contestant_info_packet = self._info_packets[contestant.id]
        for action in contestant._current_actions:
            # store tags to be passed to other contestants
            action.tags.append(action.tags)
            # store actions to be passed to pose engine
            actions.append(action)
            # store mapping between who is being hit and with what bodypart

        # use skeletons to check if hits occurred
        hits = self._calculate_hits(strike_attempts)
        # update the contestants skeletons
        self._pose_engine.update(contestant, actions, hits)
        # give contestant their new body info
        body_locations = self._pose_engine.get_contestant_ik_target_locations(
            contestant
        )
        contestant.set_body_locations(body_locations)

    def _calculate_hits(self, strike_attempts):
        return []

    # Given all the contestant skeletons display on screen
    def draw(self):
        return

    def extract_ik_targets_from_skeleton(self, skeleton):
        return skeleton.get_ik_targets()

    def current_state(self):
        return self._info_packets

    def clear_info_packets(self):
        for contestant in self.contestant_team_map:
            self._info_packets[contestant.id] = EnvInfoPacket(contestant)

    def simulation_is_over(self):
        return self._game_over
