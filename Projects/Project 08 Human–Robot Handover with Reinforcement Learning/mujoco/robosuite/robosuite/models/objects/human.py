from robosuite.models.objects.objects import MujocoXMLObject
from robosuite.utils.mjcf_utils import array_to_string, xml_path_completion


class HumanObject(MujocoXMLObject):
    """
    Clothed human from Human-Robot Gym.

    The skeleton root is a mocap body, so no free joint is added. Collision meshes are the
    original body-part meshes with contact enabled (contype 2, conaffinity 1): they collide
    with the robot, stick, and table, and not with each other.
    """

    def __init__(self, name):
        super().__init__(
            xml_path_completion("human/human.xml"),
            name=name,
            joints=None,
            obj_type="all",
            duplicate_collision_geoms=True,
        )

    def set_quat(self, quat):
        """Set the root quaternion (w, x, y, z)."""
        self._obj.set("quat", array_to_string(quat))

    @property
    def hand_geoms(self):
        """Collision geoms of both hands."""
        return [g for g in self.contact_geoms if "Hand_collision" in g]
