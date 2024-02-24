class PoseEngine:
    def __init__(self):
        pass

    def update(self, ik_skeleton, phys_skeleton, actions, hits):
        return ik_skeleton, phys_skeleton

    # update body locations and momentums to execute current action and body
    # mechanics of being hit if I was hit (i.e. head turning then snapping back)
    # into place. i.e. execute all queued actions
    # (the execution time of an action is based on distance travelled of striking
    # part at given speed)
    # check to see if anyone was hit?
    # TODO: implement execution_action
    def execute_action(self):
        return
