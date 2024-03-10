import bpy
import sys
import os

dir = os.path.dirname(bpy.data.filepath)
if not dir in sys.path:
    sys.path.append(dir)

from logger import logger


def select(object_name: str):
    # Check if there is an active object
    if bpy.context.active_object:
        # Set the mode to Object Mode
        bpy.ops.object.mode_set(mode="OBJECT")

        # Deselect all objects
        # bpy.ops.object.select_all(action="DESELECT")

    # Select the object by name
    if object_name in bpy.data.objects:
        bpy.data.objects[object_name].select_set(True)
    else:
        print(f"Object named '{object_name}' not found.")

    # Update the view layer
    bpy.context.view_layer.update()

    # Optional: Set the selected object as the active object
    bpy.context.view_layer.objects.active = bpy.data.objects[object_name]


def duplicate_active():
    active_object = bpy.context.active_object
    if active_object:
        bpy.ops.object.duplicate(linked=False)

        # The duplicated object is now the active object
        duplicated_object = bpy.context.active_object

        # Update the scene
        bpy.context.view_layer.update()
    else:
        print(f"Duplicate active failed")


def delete_active():
    # Assume there is an active object
    active_object = bpy.context.active_object

    if active_object:
        # Select the active object
        bpy.ops.object.select_all(action="DESELECT")
        active_object.select_set(True)

        # Delete the active object
        bpy.ops.object.delete()


def lookup_object_by_name(object_name):
    # Check if the object exists in the current scene
    if object_name in bpy.data.objects:
        return bpy.data.objects[object_name]
    else:
        return None


def set_pose_mode():
    active_object = bpy.context.active_object
    if active_object:
        bpy.ops.object.mode_set(mode="POSE")


def set_object_mode():
    active_object = bpy.context.active_object
    if active_object is not None:
        bpy.ops.object.mode_set(mode="OBJECT")


def get_mode():
    """
    Get the current mode in Blender.

    Returns:
        str: The current mode (e.g., 'OBJECT', 'EDIT_MESH', 'EDIT_CURVE', etc.).
    """
    # Get the context
    context = bpy.context

    # Check the type of the active object
    if context.active_object is not None:
        obj = context.active_object
        if obj.mode == "OBJECT":
            return "OBJECT"
        elif obj.mode == "EDIT":
            # Check the type of the object data
            if isinstance(obj.data, bpy.types.Mesh):
                return "EDIT_MESH"
            elif isinstance(obj.data, bpy.types.Curve):
                return "EDIT_CURVE"
            # Add more checks for other edit modes as needed
        else:
            return obj.mode

    return None


if __name__ == "__main__":
    RIG_TEMPLATE_NAME = "rig_template"
    select(RIG_TEMPLATE_NAME)
