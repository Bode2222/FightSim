import sys
import os

dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)

from Blender.PoseEngine import PoseEngine, IKSkeleton, PhysAnimSkeleton
from Contestant import ContestantState
from logger import logger
import importlib, Contestant

importlib.reload(Contestant)


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
    def __init__(self, contestant_team_map):
        self.contestant_team_map = contestant_team_map

        # set game-over to false
        self._has_finished = False

        # Make space for the info packet of each contestant
        self._info_packets = {}
        self.clear_info_packets()

        # instantiate engine to handle skeleton posing
        self._pose_engine = PoseEngine()

        # Give each contestant an Ik skeleton and a PhysAnim skeleton
        self._skeleton_map = {}
        for contestant in contestant_team_map.keys():
            ik_armature = IKSkeleton(contestant)
            phys_armature = PhysAnimSkeleton(contestant)
            self._skeleton_map[contestant] = [
                ik_armature,
                phys_armature,
            ]
            contestant.set_body_locations(ik_armature.get_ik_target_locations())

    def update(self, contestant_state: ContestantState):
        contestant = contestant_state.contestant
        ik_skeleton, phys_skeleton = self._skeleton_map[contestant]
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
        self._skeleton_map[contestant] = self._pose_engine.update(
            ik_skeleton, phys_skeleton, actions, hits
        )
        # give contestant their new body info
        contestant.set_body_locations(ik_skeleton.get_ik_target_locations())

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
        return self._has_finished
