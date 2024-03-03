import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from Blender.BlenderUtils import (
    select,
    duplicate_active,
    delete_active,
    set_pose_mode,
    set_object_mode,
    select_object,
    lookup_object_by_name,
    get_mode,
)
from Contestant import Contestant, ConcreteAction
from common import BodyPart, Vec3
from ActionList import Attack
from Action import _ActionInterface
from mathutils import Vector, Matrix
from logger import logger


# dummy class for eventual skeleton object gotten from blender
class IKSkeleton:
    RIG_TEMPLATE_NAME = "rig_template"

    def __init__(self, contestant: Contestant):

        self.contestant = contestant
        self.skeleton = self._instantiate_skeleton()
        self._assign_bones_to_vars()

    # return a rig object fitted to this contestant
    def _instantiate_skeleton(self):
        set_object_mode()
        armature_name = f"{self.contestant.name}_skeleton"
        target_location = Vector([self.contestant.id * 2.0, 0, 0])
        armature = lookup_object_by_name(armature_name)

        if not armature:
            # get the rig template object
            rig_template = select(IKSkeleton.RIG_TEMPLATE_NAME)
            # copy into new object that will be this rig
            duplicate_active()
            duplicated_object = bpy.context.active_object
            duplicated_object.name = armature_name
            # set it's location
            duplicated_object.location = target_location

            return duplicated_object
        else:
            # reset transforms
            select(armature_name)
            self.reset_transforms_on_active()
            bpy.ops.object.posemode_toggle()
            bpy.ops.pose.select_all(action="SELECT")
            bpy.ops.pose.loc_clear()
            bpy.ops.pose.rot_clear()
            bpy.ops.pose.scale_clear
            bpy.ops.object.posemode_toggle()
            armature.location = target_location
            return armature

    def reset_transforms_on_active(self):
        # Set the object's location to the origin (0, 0, 0)
        bpy.ops.object.location_clear(clear_delta=False)
        # Set the object's rotation to the default rotation (identity)
        bpy.ops.object.rotation_clear(clear_delta=False)
        # Set the object's scale to (1, 1, 1)
        bpy.ops.object.scale_clear(clear_delta=False)

    # assign bones to local variables for easy retrieval
    def _assign_bones_to_vars(self):
        pose_bones = self.skeleton.pose.bones
        self.hand_ik_l = self.skeleton.pose.bones["hand_ik.L"]
        self.hand_ik_r = self.skeleton.pose.bones["hand_ik.R"]
        self.foot_ik_l = self.skeleton.pose.bones["foot_ik.L"]
        self.foot_ik_r = self.skeleton.pose.bones["foot_ik.R"]
        self.head_ik = self.skeleton.pose.bones["head"]
        self.torso_ik = self.skeleton.pose.bones["torso"]
        self.shoulder_l = pose_bones["shoulder.L"]
        self.shoulder_r = pose_bones["shoulder.R"]

    # Performing an action updates it's completeness
    # for now snap body part to location
    def perform(self, action: ConcreteAction):
        for i, part_loc in enumerate(action.target_body_locations.items()):
            body_part, _ = part_loc
            self._progress_body_part_to_location(body_part, action.action_locations[i])

    # need to do processing on the target location if characters limbs can't stretch
    def _progress_body_part_to_location(self, bodypart, location):
        ik_target = self._get_body_part_ik_target(bodypart)
        set_pose_mode()
        global_target = Vector(location.data)
        local_target = self._global_loc_to_bone_space(
            self.skeleton, ik_target, global_target
        )
        ik_target.location += local_target

    # set the ik target back to the bone pos
    def _reset_ik_target(self, body_part):
        ik_target = self._get_body_part_ik_target(body_part)

    def _get_body_part_ik_target(self, bodypart: BodyPart):
        # get mapping from bodyparts to ik targets
        body_part_ik_target = {BodyPart.HAND_L: self.hand_ik_l}

        return body_part_ik_target[bodypart]

    def _global_loc_to_bone_space(self, armature, bone, global_position):
        # bone_local = self.skeleton.data.bones["hand_ik.L"].head_local
        bone_local = bone.head
        return global_position - armature.location - bone_local

    def get_ik_target_locations(self):
        set_object_mode()
        select_object(self.skeleton)
        # head, torso, hand l/r, leg l/r
        head = self.skeleton.matrix_world @ self.head_ik.head
        torso = self.skeleton.matrix_world @ self.torso_ik.head
        hand_l = self.skeleton.matrix_world @ self.hand_ik_l.head
        hand_r = self.skeleton.matrix_world @ self.hand_ik_r.head
        foot_l = self.skeleton.matrix_world @ self.foot_ik_l.head
        foot_r = self.skeleton.matrix_world @ self.foot_ik_r.head
        shoulder_l = self.skeleton.matrix_world @ self.shoulder_l.tail
        shoulder_r = self.skeleton.matrix_world @ self.shoulder_r.tail
        return [
            Vec3(list(head[:])),
            Vec3(list(torso[:])),
            Vec3(list(hand_l[:])),
            Vec3(list(hand_r[:])),
            Vec3(list(foot_l[:])),
            Vec3(list(foot_r[:])),
            Vec3(list(shoulder_l[:])),
            Vec3(list(shoulder_r[:])),
        ]


# dummy class. This will contain the size and joint limits and strengths for each
# 'mass' in the physics body
class PhysAnimSkeleton:
    def __init__(self, contestant: Contestant):
        self.contestant = contestant

    pass


class PoseEngine:
    def __init__(self):
        # create new animation layer and go to frame zero
        pass

    def _keyframe(self):
        logger.debug(f"keyframing...")
        pass

    def update(self, ik_skeleton, phys_skeleton, actions, hits):
        logger.debug(f"------------Start Pose-----------")
        # go to object mode
        set_object_mode()
        # select appropriate skeleton
        select(f"{ik_skeleton.contestant.name}_skeleton")
        # update ik skeleton to perform current action. procedural animation
        for action in actions:
            logger.debug(f"Action: {action.action_locations}")
            ik_skeleton.perform(action)
        # go back to object mode
        set_object_mode()

        # if there have been no hits then map phys skeleton to ik skeleton and return
        # i.e. do no physics calcs and let the animation play as is

        # if there have been hits apply hits to phys_skeleton then update ik skeleton
        # positions with hit skeleton, interpolating weight between ik and phys down
        # until zero over time
        self._keyframe()
        logger.debug(f"---------------------------------")
        return ik_skeleton, phys_skeleton

    # update body locations and momentums to execute current action and body
    # mechanics of being hit if I was hit (i.e. head turning then snapping back)
    # into place. i.e. execute all queued actions
    # (the execution time of an action is based on distance travelled of striking
    # part at given speed)
    # check to see if anyone was hit?
    # TODO: implement execution_actions
    def execute_action(self):
        return


# self._global_loc_to_bone_space is giving me zeros. why?
if __name__ == "__main__":
    logger.info("Program started.")
    Jack, Jill = Contestant("Jack"), Contestant("Jill")
    Jack.id, Jill.id = 1, 2
    Jack_skelly = IKSkeleton(Jack)
    Jack.set_body_locations(Jack_skelly.get_ik_target_locations())
    Jill_skelly = IKSkeleton(Jill)
    Jill.set_body_locations(Jill_skelly.get_ik_target_locations())

    logger.info(f"Jill head pos: {Jill.head_loc}")
    logger.info(f"Jill body: {Jill_skelly.get_ik_target_locations()}")
    jab_jills_head = ConcreteAction(Attack["JAB_HEAD"], [Jill.head_loc])

    poser = PoseEngine()
    poser.update(Jack_skelly, None, [jab_jills_head], None)

    logger.info("Program ended.")
