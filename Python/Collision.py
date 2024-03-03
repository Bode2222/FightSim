from common import Vec3
import numpy as np


class BoundingVolume:
    def __init__(self, loc: Vec3):
        self.location = loc
        pass

    def collision(self, object):
        pass


class BoundingSphere(BoundingVolume):
    def __init__(self, loc: Vec3, radius: float):
        super().__init__(loc)
        self.radius = radius

    def collision(self, object):
        if isinstance(object, BoundingBox):
            return _box_sphere_collision(object, self)
        elif isinstance(object, BoundingSphere):
            return _sphere_sphere_collision(object, self)
        else:
            print("Invalid collsion object")
        return False


class BoundingBox(BoundingVolume):
    def __init__(self, loc: Vec3, rot: Vec3, half_extents: Vec3):
        super().__init__(loc)
        self.rotation = rot
        self.half_extents = half_extents

    def rotation_matrix(self):
        # Calculate the rotation matrix based on the Euler angles
        cos_x, sin_x = np.cos(self.rotation.x), np.sin(self.rotation.x)
        cos_y, sin_y = np.cos(self.rotation.y), np.sin(self.rotation.y)
        cos_z, sin_z = np.cos(self.rotation.z), np.sin(self.rotation.z)

        rotation_x = np.array([[1, 0, 0], [0, cos_x, -sin_x], [0, sin_x, cos_x]])
        rotation_y = np.array([[cos_y, 0, sin_y], [0, 1, 0], [-sin_y, 0, cos_y]])
        rotation_z = np.array([[cos_z, -sin_z, 0], [sin_z, cos_z, 0], [0, 0, 1]])

        return np.dot(rotation_z, np.dot(rotation_y, rotation_x))

    def collision(self, object: BoundingVolume):
        if isinstance(object, BoundingBox):
            return _box_box_collision(self, object)
        elif isinstance(object, BoundingSphere):
            return _box_sphere_collision(box=self, sphere=object)
        else:
            print("Invalid collsion object")
        return False


def _sphere_sphere_collision(self, s1: BoundingSphere, s2: BoundingSphere):
    max_radius = max(s1.radius, s2.radius)
    dist_btw_spheres = (s1.location - s2.location).magnitude()
    return dist_btw_spheres <= max_radius


def _box_box_collision(box1: BoundingBox, box2: BoundingBox):
    box1_center, box2_center = box1.location, box2.location
    box1_half_extents, box2_half_extents = box1.half_extents, box2.half_extents
    box1_angles, box2_angles = box1.rotation, box2.rotation
    # Calculate the rotation matrices for each box
    rotation_matrix1 = np.dot(
        np.dot(
            np.array(
                [
                    [np.cos(box1_angles[2]), -np.sin(box1_angles[2]), 0],
                    [np.sin(box1_angles[2]), np.cos(box1_angles[2]), 0],
                    [0, 0, 1],
                ]
            ),
            np.array(
                [
                    [np.cos(box1_angles[1]), 0, np.sin(box1_angles[1])],
                    [0, 1, 0],
                    [-np.sin(box1_angles[1]), 0, np.cos(box1_angles[1])],
                ]
            ),
        ),
        np.array(
            [
                [1, 0, 0],
                [0, np.cos(box1_angles[0]), -np.sin(box1_angles[0])],
                [0, np.sin(box1_angles[0]), np.cos(box1_angles[0])],
            ]
        ),
    )

    rotation_matrix2 = np.dot(
        np.dot(
            np.array(
                [
                    [np.cos(box2_angles[2]), -np.sin(box2_angles[2]), 0],
                    [np.sin(box2_angles[2]), np.cos(box2_angles[2]), 0],
                    [0, 0, 1],
                ]
            ),
            np.array(
                [
                    [np.cos(box2_angles[1]), 0, np.sin(box2_angles[1])],
                    [0, 1, 0],
                    [-np.sin(box2_angles[1]), 0, np.cos(box2_angles[1])],
                ]
            ),
        ),
        np.array(
            [
                [1, 0, 0],
                [0, np.cos(box2_angles[0]), -np.sin(box2_angles[0])],
                [0, np.sin(box2_angles[0]), np.cos(box2_angles[0])],
            ]
        ),
    )

    # Transform box2 into the coordinate system of box1
    box2_center_rotated = np.dot(rotation_matrix1.T, (box2_center - box1_center).data)
    box2_half_extents_rotated = np.dot(rotation_matrix1.T, box2_half_extents.data)

    # Calculate the minimum and maximum coordinates of the boxes along each axis
    box1_min = box1_center - box1_half_extents
    box1_max = box1_center + box1_half_extents

    box2_min_rotated = box2_center_rotated - box2_half_extents_rotated
    box2_max_rotated = box2_center_rotated + box2_half_extents_rotated

    # Check for collision along each axis
    for axis in range(3):
        if (
            box1_max[axis] < box2_min_rotated[axis]
            or box1_min[axis] > box2_max_rotated[axis]
        ):
            return False

    return True


def _box_sphere_collision(box: BoundingBox, sphere: BoundingSphere):
    # Rotate the sphere's position into the box's local space
    sphere_local_position = np.dot(
        np.linalg.inv(box.rotation_matrix()), (sphere.location - box.location).data
    )

    # Clamp the sphere's position to the box's half extents
    closest_point_local = Vec3(
        [
            np.clip(sphere_local_position[0], -box.half_extents.x, box.half_extents.x),
            np.clip(sphere_local_position[1], -box.half_extents.y, box.half_extents.y),
            np.clip(sphere_local_position[2], -box.half_extents.z, box.half_extents.z),
        ]
    )

    # Rotate the closest point back to the world space
    closest_point_world = (
        np.dot(box.rotation_matrix(), closest_point_local.data) + box.location.data
    )

    # Calculate the distance between the sphere's center and the closest point on the box
    distance = (sphere.location - Vec3(closest_point_world)).magnitude()

    # Check if the distance is less than or equal to the sum of the sphere's radius and half of the box's dimensions
    return distance <= (
        sphere.radius + max(box.half_extents.x, box.half_extents.y, box.half_extents.z)
    )


def rotation_matrix(self):
    # Calculate the rotation matrix based on the Euler angles
    cos_x, sin_x = np.cos(self.rotation.x), np.sin(self.rotation.x)
    cos_y, sin_y = np.cos(self.rotation.y), np.sin(self.rotation.y)
    cos_z, sin_z = np.cos(self.rotation.z), np.sin(self.rotation.z)

    rotation_x = np.array([[1, 0, 0], [0, cos_x, -sin_x], [0, sin_x, cos_x]])
    rotation_y = np.array([[cos_y, 0, sin_y], [0, 1, 0], [-sin_y, 0, cos_y]])
    rotation_z = np.array([[cos_z, -sin_z, 0], [sin_z, cos_z, 0], [0, 0, 1]])

    return np.dot(rotation_z, np.dot(rotation_y, rotation_x))


if __name__ == "__main__":
    # Example usage
    box1 = BoundingBox(
        Vec3([2.0, 2.0, 2.0]),
        Vec3([np.pi / 4.0, np.pi / 6.0, np.pi / 3.0]),
        Vec3([1.0, 2.0, 3.0]),
    )
    box2 = BoundingBox(
        Vec3([4.0, 4.0, 4.0]),
        Vec3([np.pi / 6.0, np.pi / 4.0, np.pi / 3.0]),
        Vec3([1.0, 2.0, 3.0]),
    )
    sphere = BoundingSphere(Vec3([1.59, 0.46, 0.28]), 1)

    print("Collision:", box1.collision(box2), sphere.collision(box1))
