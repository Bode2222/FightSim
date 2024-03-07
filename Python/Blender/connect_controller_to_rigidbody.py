"""
This script connects every rigidbody from controller to character with a generic spring
"""

import os
import bpy


def main():
    os.system("cls")
    # Get all objects with suffix "rigidbody" and sort them by name
    rigidbodies = [obj for obj in bpy.data.objects if "rigidbody" in obj.name.lower()]

    # Get all objects with suffix "controller" and sort them by name
    controllers = [obj for obj in bpy.data.objects if "controller" in obj.name.lower()]

    print(f"len(rigidbodies): {len(rigidbodies)}")
    print(f"len(controllers): {len(controllers)}")
    assert len(rigidbodies) == len(
        controllers
    ), "Number of rigidbodies and controllers must be the same"

    # For each controller, connect it to the corresponding rigidbody with a generic spring
    for controller in controllers:
        # Get the rigidbody corresponding to the controller
        part_name = controller.name.rsplit("_", 1)[0]
        rigidbody = [rb for rb in rigidbodies if part_name in rb.name]
        assert (
            len(rigidbody) == 1
        ), f"Expected 1 rigidbody for {controller.name}, but got {len(rigidbody)}"
        rigidbody = rigidbody[0]

        is_any_object_selected = any(
            obj.select_get() for obj in bpy.context.scene.objects
        )
        if is_any_object_selected:
            bpy.ops.object.select_all(action="DESELECT")

        # Create a generic spring between the controller and the rigidbody.
        # Do this by creating an empty object at the rigidbody location and setting
        # it as a rigidbody constraint
        # rigidbody.select_set(True)
        bpy.context.view_layer.objects.active = rigidbody
        # if it doesn't have a constraint, add one
        if not rigidbody.constraints:
            bpy.ops.rigidbody.constraint_add(type="GENERIC_SPRING")
        constraint = bpy.context.object
        # Constraint name is controller name without the suffix + _constraint
        # constraint.name = controller.name.rsplit("_", 0)[0] + "_constraint"

        # Set the rigidbody and controller for the constraint
        constraint.rigid_body_constraint.object1 = controller
        constraint.rigid_body_constraint.object2 = rigidbody

        # Set the generic spring parameters
        constraint.rigid_body_constraint.use_limit_lin_x = False
        constraint.rigid_body_constraint.use_limit_lin_y = False
        constraint.rigid_body_constraint.use_limit_lin_z = False
        constraint.rigid_body_constraint.use_limit_ang_x = False
        constraint.rigid_body_constraint.use_limit_ang_y = False
        constraint.rigid_body_constraint.use_limit_ang_z = False
        if "shin" in rigidbody.name.lower():
            constraint.rigid_body_constraint.use_spring_x = True
            constraint.rigid_body_constraint.use_spring_y = True
            constraint.rigid_body_constraint.use_spring_z = True
        constraint.rigid_body_constraint.use_spring_ang_x = True
        constraint.rigid_body_constraint.use_spring_ang_y = True
        constraint.rigid_body_constraint.use_spring_ang_z = True
        # set angular spring stiffness
        constraint.rigid_body_constraint.spring_stiffness_ang_x = 100
        constraint.rigid_body_constraint.spring_stiffness_ang_y = 100
        constraint.rigid_body_constraint.spring_stiffness_ang_z = 100
    return


# todo: get this script to work
main()
