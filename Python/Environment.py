from common import Hit, ConcreteBodyPart, PhysicsAttr


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


# takes in contestant states as input to update()
# gives out info packets as as output to info()
class Environment:
    def __init__(self, contestant_team_map):
        self.contestant_team_map = contestant_team_map
        self._has_finished = False
        self._info_packets = {}
        self.clear()

    def update(self, contestant_state: ContestantState):
        contestant = contestant_state.contestant

        # check to see if anyone was hit using body position
        # get action executed
        def action_executed_without_interruption(
            part: ConcreteBodyPart, phys_attr: PhysicsAttr
        ):
            # check if body part reached target without interference
            if len(phys_attr._forces) != 1:
                return None
            force = phys_attr._forces[0]
            pos, vel, acc = force.get_kinematics()
            if pos < 1:
                return None
            # Get the action that caused this
            action_executed = [
                action
                for action in contestant._current_actions
                if part.body in action.target_body_locations.keys()
            ]
            return action_executed

        # TODO: get any contestant parts in path of action
        def body_part_in_action_path():
            return None

        for part, phys_attr in contestant.body.items():
            # if only one force is applied to it (i.e. only one action being carried
            # out and it didn't get blocked or parried.)
            action_executed = action_executed_without_interruption(part, phys_attr)
            if action_executed:
                body_part_hit = body_part_in_action_path()
                if not body_part_hit:
                    continue
                hit = Hit(
                    body_part_hit,
                    contestant.get_action_impact(action_executed),
                    contestant.id,
                    action_executed.tags,
                )
                self._info_packets[body_part_hit.contestant_id].hits.append(hit)

        # pass action tags and body positions to everyone
        contestant_info_packet = self._info_packets[contestant.id]
        for action in contestant._current_actions:
            contestant_info_packet.tags.append(action.tags)

    def current_state(self):
        return self._info_packets

    def clear(self):
        for contestant in self.contestant_team_map:
            self._info_packets[contestant.id] = EnvInfoPacket(contestant)

    def simulation_is_over(self):
        return self._has_finished
