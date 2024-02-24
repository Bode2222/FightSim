from common import Hit, ConcreteBodyPart, PhysicsAttr
from PoseEngine import PoseEngine


# Information about a contestant in a step. Works on a 'per-contestant' basis
class EnvInfoPacket:
    def __init__(self, contestant, action_tags=[], hits=[]):
        self.contestant = contestant
        self._action_tags = action_tags
        self._hits = hits
        pass


class ContestantState:
    def __init__(self, contestant, action_list):
        self.contestant = contestant
        self.action_list = action_list


# dummy class for eventual skeleton object gotten from blender
class IKSkeleton:
    pass


# dummy class. This will contain the size and joint limits and strengths for each
# 'mass' in the physics body
class PhysAnimSkeleton:
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
            self._skeleton_map[contestant] = [IKSkeleton(), PhysAnimSkeleton()]

        # extra info needed to choose an action added to info packet here
        # stuff like positions, momentums, etc

    def update(self, contestant_state: ContestantState):
        contestant = contestant_state.contestant
        ik_skeleton, phys_skeleton = self._skeleton_map[contestant]
        actions = []
        strike_attempts = {}

        # store action tags
        contestant_info_packet = self._info_packets[contestant.id]
        for action in contestant._current_actions:
            # store tags to be passed to other contestants
            contestant_info_packet.tags.append(action.tags)
            # store actions to be passed to pose engine
            actions.append(action)
            # store mapping between who is being hit and with what bodypart

        # use skeletons to check if hits occurred
        hits = self._calculate_hits(strike_attempts)
        # update the contestants skeletons
        self._skeleton_map[contestant][0] = self._pose_engine.update(
            ik_skeleton, phys_skeleton, actions, hits
        )
        # give contestant their new body info
        body_position = self.extract_ik_targets_from_skeleton(
            self._skeleton_map[contestant]
        )
        contestant.update_body(body_position)

    def _calculate_hits(strike_attempts):
        return []

    # Given all the contestant skeletons display on screen
    def draw(self):
        return

    def extract_ik_targets_from_skeleton(self, skeleton):
        return []

    def current_state(self):
        return self._info_packets

    def clear_info_packets(self):
        for contestant in self.contestant_team_map:
            self._info_packets[contestant.id] = EnvInfoPacket(contestant)

    def simulation_is_over(self):
        return self._has_finished
