from common import Hit


# Information about a contestant in a step. Works on a 'per-contestant' basis
class EnvInfoPacket:
    def __init__(
        self, contestant_id=None, location_momentum=None, action_tags=[], hits=[]
    ):
        self._location_momentum = location_momentum
        self._action_tags = action_tags
        self._hits = hits
        self._contestant_id = contestant_id
        pass


class ContestantState:
    def __init__(self, contestant, action_list):
        self.contestant = contestant
        self.action_list = action_list


# takes in contestant states as input to update()
# gives out info packets as as output to info()
class Environment:
    def __init__(self, contestant_team_map):
        self.contestant_team_map = contestant_team_map
        self._has_finished = False
        self._info_packets = {}
        pass

    def update(self, contestant_state):
        # check to see if anyone was hit using body position
        # if no pass action tags and body positions to everyone
        # if yes pass impact info and location to everyone

        contestant_info_packet = EnvInfoPacket()
        self._info_packets[contestant_state.contestant.id] = contestant_info_packet

    def current_state(self):
        return self._info_packets

    def clear(self):
        self._info_packets = {}

    def simulation_is_over(self):
        return self._has_finished
