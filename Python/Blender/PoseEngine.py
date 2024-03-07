import bpy
import sys
import os

# dir = os.path.dirname(bpy.data.filepath)
dir = os.path.dirname(__file__)
if not dir in sys.path:
    sys.path.append(dir)

from BlenderUtils import (
    select,
    duplicate_active,
    set_pose_mode,
    set_object_mode,
    lookup_object_by_name,
)
import numpy as np
from Contestant import Contestant, ConcreteAction
from common import BodyPart, Vec3
from ActionList import Attack, Tag
from mathutils import Vector
from logger import logger
import importlib, Blender.BlenderUtils
from enum import Enum

importlib.reload(Blender.BlenderUtils)


class Path:
    class Type(Enum):
        STRAIGHT = 0
        CURVED = 1

    def __init__(self, pathType: Type, points: list, ik_target, name="Path"):
        self.pathType = pathType
        self.points = points
        self.progress = 0.0
        self.ik_target = ik_target
        self.name = name

        self.curve = None
        if pathType == Path.Type.CURVED:
            self.curve = self._generate_bezier_curve(points)
        elif pathType == Path.Type.STRAIGHT:
            self.curve = self._generate_straight_path(points)
        else:
            raise ValueError("Invalid path type")
        return

    @staticmethod
    def _generate_straight_path(points):
        assert len(points) == 2, "Straight path must have 2 points"
        curve = bpy.ops.curve.primitive_nurbs_path_add()
        curve = bpy.context.object

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.curve.select_all(action="DESELECT")
        bpy.ops.object.mode_set(mode="OBJECT")
        # move vertices 1 and 2 to desired locations
        curve.data.splines[0].points[0].co = points[0].to_4d()
        curve.data.splines[0].points[1].co = points[1].to_4d()
        # select vertices 2, 3 and 4
        curve.data.splines.active.points[2].select = True
        curve.data.splines.active.points[3].select = True
        curve.data.splines.active.points[4].select = True
        # delete selected vertices
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.curve.delete(type="VERT")
        bpy.ops.object.mode_set(mode="OBJECT")
        return curve

    @staticmethod
    def _generate_bezier_curve(points):
        pass

    def __eq__(self, other):
        return self.ik_target == other.ik_target


# dummy class for eventual skeleton object gotten from blender
class IKSkeleton:
    RIG_TEMPLATE_NAME = "rig_template"

    def __init__(self, contestant: Contestant):
        self.contestant = contestant
        self.skeleton = self._instantiate_skeleton()
        self._assign_bones_to_vars()
        # hide controller and joints
        self.current_action_paths = set()
        # actions that are being performed
        self.current_actions = set()
        # add a follow path modifier to the hands and feet
        self._add_follow_path_constraint(self.hand_ik_l, "hand_l_path")
        # instantiate physical armatures
        # copy controller and rigidbody armatures
        # parent controller to ik skeleton

        self._body_part_to_ik_target = {
            BodyPart.HAND_L: self.hand_ik_l,
            BodyPart.HAND_R: self.hand_ik_r,
            BodyPart.FOOT_L: self.foot_ik_l,
            BodyPart.FOOT_R: self.foot_ik_r,
            BodyPart.HEAD: self.head_ik,
        }

    # return a rig object fitted to this contestant
    def _instantiate_skeleton(self):
        set_object_mode()
        armature_name = f"{self.contestant.name}_skeleton"
        target_location = Vector([2 + self.contestant.id * 1.0, 0, 0])
        armature = lookup_object_by_name(armature_name)

        if not armature:
            logger.debug(f"Creating new rig for {self.contestant.name}")
            # get the rig template object
            select(IKSkeleton.RIG_TEMPLATE_NAME)
            # copy into new object that will be this rig
            duplicate_active()
            duplicated_object = bpy.context.active_object
            duplicated_object.name = armature_name
            # set it's location
            duplicated_object.location = target_location

            armature = duplicated_object

            # -1 or 1 based on even or odd id
            rotation_coefficient = (self.contestant.id % 2) * 2 - 1
            armature.rotation_euler = (0, 0, rotation_coefficient * np.pi / 2.0)
        else:
            logger.debug(f"Resetting transforms on {armature_name}")
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

    # this needs revision
    def _add_follow_path_constraint(self, ik_target, name="Follow Path"):
        # assert that we're in object mode
        set_object_mode()
        # add a follow path modifier to the ik target
        bpy.ops.object.select_all(action="DESELECT")
        self.skeleton.select_set(True)
        bpy.context.view_layer.objects.active = self.skeleton
        set_pose_mode()
        # select ik target
        ik_target.bone.select = True
        # add follow path bone constraint
        bpy.ops.pose.constraint_add(type="FOLLOW_PATH")
        # set follow path constraint properties
        follow_path_constraint.name = name
        follow_path_constraint = ik_target.constraints["Follow Path"]
        follow_path_constraint.use_curve_follow = True
        follow_path_constraint.forward_axis = "FORWARD_Y"
        follow_path_constraint.up_axis = "UP_Z"
        follow_path_constraint.offset_factor = 0.0
        follow_path_constraint.use_fixed_location = True
        follow_path_constraint.use_curve_radius = False
        follow_path_constraint.use_curve_follow = True

    # set the follow path modifier target to none and offset to zero
    def _reset_follow_path_constraint(self, ik_target):
        # remove follow path modifier from the ik target
        bpy.ops.object.select_all(action="DESELECT")
        self.skeleton.select_set(True)
        bpy.context.view_layer.objects.active = self.skeleton
        bpy.ops.object.modifier_remove(modifier="Follow Path")

    # set the follow path modifier target to given curve
    def _set_follow_path_constraint_target(self, path):
        # get follow path constraints
        follow_path_constraint = self.skeleton.modifiers[path.name]
        follow_path_constraint.target = path.curve

    # set the follow path modifier offset to given value
    def _set_follow_path_constraint_offset(self, path: Path):
        follow_path_constraint = self.skeleton.modifiers[path.name]
        follow_path_constraint.offset_factor = path.progress

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

    def _get_ik_target(self, body_part: BodyPart):
        return self._body_part_to_ik_target[body_part]

    # this function takes an action and breaks it into a series of paths
    # that the body parts will take to get to the target locations
    def _generate_action_paths(self, action: ConcreteAction):
        # get ik targets for involved body locations mapping
        parts = action.target_body_locations.keys()
        part_iks = {}
        for part in parts:
            part_iks[part] = self._body_part_to_ik_target[part]

        if Tag["STRAIGHT_PATH"] in action.tags:
            involved_ik = part_iks[parts[0]]
            init_point = self._get_world_position(involved_ik)
            final_point = action.strike_locations[0]
            # TODO: Path name should reflect body parts involved
            return [
                Path(
                    Path.Type.STRAIGHT,
                    [init_point, final_point],
                    involved_ik,
                    f"hand_l_path",
                )
            ]
        pass

    def _progress_path(self, path: Path):
        if path.progress < 1.0:
            path.progress += 0.1
            # set ik target follow path modifier offset to path progress
            self._set_follow_path_constraint_offset(path)

    # Performing an action updates it's completeness
    # for now snap body part to location
    def perform(self, action: ConcreteAction):
        # if action is already being performed, return
        if action in self.current_actions:
            return

        # if not add action to list and generate action paths
        self.current_actions.add(action)
        self.current_action_paths.add(self._generate_action_paths(action))

        # progress each body part along it's path
        for path in self.current_action_paths:
            self._progress_path(path)
            """logger.debug(f"Moving {part_loc[0].name} to {action.strike_locations[i]}")
            body_part, _ = part_loc
            self._progress_body_part_to_location(body_part, action.strike_locations[i])"""

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
        body_part_ik_target = {}
        body_part_ik_target[BodyPart.HAND_L] = self.hand_ik_l
        body_part_ik_target[BodyPart.HAND_R] = self.hand_ik_r
        body_part_ik_target[BodyPart.FOOT_L] = self.foot_ik_l
        body_part_ik_target[BodyPart.FOOT_R] = self.foot_ik_r
        body_part_ik_target[BodyPart.HEAD] = self.head_ik
        body_part_ik_target[BodyPart.TORSO] = self.torso_ik
        # body_part_ik_target[BodyPart.SHOULDER_L] = self.shoulder_l
        # body_part_ik_target[BodyPart.SHOULDER_R] = self.shoulder_r

        return body_part_ik_target[bodypart]

    def _global_loc_to_bone_space(self, armature, bone, global_position):
        # bone_local = self.skeleton.data.bones["hand_ik.L"].head_local
        bone_local = bone.head
        return global_position - armature.location - bone_local

    def _get_world_position(self, ik_target):
        return self.skeleton.matrix_world @ ik_target.head

    def get_ik_target_locations(self):
        set_object_mode()
        self.skeleton.select_set(True)
        # head, torso, hand l/r, leg l/r
        head = self.skeleton.matrix_world @ self.head_ik.head
        torso = self.skeleton.matrix_world @ self.torso_ik.head
        hand_l = self.skeleton.matrix_world @ self.hand_ik_l.head
        hand_r = self.skeleton.matrix_world @ self.hand_ik_r.head
        foot_l = self.skeleton.matrix_world @ self.foot_ik_l.head
        foot_r = self.skeleton.matrix_world @ self.foot_ik_r.head
        shoulder_l = self.skeleton.matrix_world @ self.shoulder_l.tail
        shoulder_r = self.skeleton.matrix_world @ self.shoulder_r.tail
        self.skeleton.select_set(False)
        return [
            Vec3(list(head[:])),
            Vec3(list(torso[:])),
            Vec3(list(hand_l[:])),
            Vec3(list(hand_r[:])),
            Vec3(list(foot_l[:])),
            Vec3(list(foot_r[:])),
            Vec3(list(shoulder_l[:])),
            Vec3(list(shoulder_r[:])),
        ], self.skeleton.matrix_world


# dummy class. This will contain the size and joint limits and strengths for each
# 'mass' in the physics body
class PhysAnimSkeleton:
    def __init__(self, contestant: Contestant):
        self.contestant = contestant

    pass


class PoseEngine:
    def __init__(self, contestants: list = [], sim_frame_rate=10, anim_frame_rate=24):
        self.contestants = contestants
        self.sim_frame_rate = sim_frame_rate
        self.anim_frame_rate = anim_frame_rate

        self._skeleton_map = {}
        for contestant in contestants:
            ik_armature = IKSkeleton(contestant)
            phys_armature = PhysAnimSkeleton(contestant)
            self._skeleton_map[contestant] = [
                ik_armature,
                phys_armature,
            ]
            contestant.set_body_locations(ik_armature.get_ik_target_locations())
        # create new animation layer and go to frame zero
        pass

    def get_contestant_ik_target_locations(self, contestant):
        return self._skeleton_map[contestant][0].get_ik_target_locations()

    def _keyframe(self):
        logger.debug(f"keyframing..")
        pass

    def update(self, contestant, actions, hits):
        logger.debug(f"------------Start Pose-----------")

        ik_skeleton = self._skeleton_map[contestant][0]
        phys_skeleton = self._skeleton_map[contestant][1]

        # go to object mode
        set_object_mode()
        # select appropriate skeleton
        select(f"{ik_skeleton.contestant.name}_skeleton")
        # update ik skeleton to perform current action. procedural animation
        for action in actions:
            logger.debug(f"Action: {action.name}")
            ik_skeleton.perform(action)
        # go back to object mode
        set_object_mode()
        # if there is an active object, deselect it
        if bpy.context.active_object:
            bpy.context.active_object.select_set(False)

        # if there have been no hits then map phys skeleton to ik skeleton and return
        # i.e. do no physics calcs and let the animation play as is

        # if there have been hits apply hits to phys_skeleton then update ik skeleton
        # positions with hit skeleton, interpolating weight between ik and phys down
        # until zero over time
        self._keyframe()
        logger.debug(f"---------------------------------")
        return ik_skeleton, phys_skeleton


# on action:
# - get ik targets for involved body locations mapping
# - if straight path, create path from current location to target location
# - if curved path, create path from current location to target location
# - store paths in action
# - store action in current actions
# - update paths at each time step
# - when path is complete, remove path from current paths
# - when all paths are complete, remove action from current actions

# on update:
# - if action is in current actions, update action
# - if action is not in current actions, update paths
# - if action is not in current actions and paths are complete, remove paths
# - if action is not in current actions and paths are complete, remove action


# TODO:
# - Every function with path modifier in the name needs review
# - Implement path curve creation. Note: path center should start from world center
# - when hand exceeds length of arm, turn shoulders
# - when leg exceeds length of leg, turn hips
# - let time steps be independent of frame rate of animationr
def main():
    os.system("cls")
    # logger.info("Program started.")
    # Jack, Jill = Contestant("Jack"), Contestant("Jill")
    # Jack.id, Jill.id = 1, 2
    # jab_jills_head = ConcreteAction(Attack["JAB_HEAD"], [Jill.head_loc])

    # pose_engine = PoseEngine([Jack, Jill])
    # pose_engine.update(Jack, [jab_jills_head], None)
    # x = Path._generate_straight_path([Vector([0, 0, 0]), Vector([1, 1, 1])])
    # x.select_set(True)

    logger.info("Program ended.")


main()
