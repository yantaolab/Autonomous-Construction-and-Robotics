import numpy as np

import robosuite.utils.transform_utils as T
from robosuite.controllers.composite.composite_controller_factory import load_composite_controller_config
from robosuite.environments.manipulation.manipulation_env import ManipulationEnv
from robosuite.models.arenas import TableArena
from robosuite.models.objects import HammerObject, HumanObject
from robosuite.models.tasks import ManipulationTask
from robosuite.utils.mjcf_utils import find_elements
from robosuite.utils.observables import Observable, sensor
from robosuite.utils.placement_samplers import UniformRandomSampler

# 3 seconds at 20 Hz inside the 2 cm ball, no faster than 5 mm/s.
HOLD_STEPS = 60
# Tier 3 speed. Faster than this does not score the hold and does not end the episode.
CONTACT_SPEED = 0.005
# Tier 2 and tier 3 ball around the palm-sphere center.
TIER_RADIUS = 0.02
# Palm-sphere radius. The handle center is inside when it is at most this far
# from the sphere center.
PALM_SPHERE_RADIUS = 0.05
# Sphere center sits this far from the hand-mesh center, out along the palm normal.
PALM_SPHERE_OFFSET = 0.06

# Held start: the head is already pinched at the home pose. Measured from a real
# top-down pinch. The hammer is always built with rng(0), so the size does not
# depend on env seed or reset count.
HELD_HAMMER_POS = np.array([0.01261, -0.08939, 0.09573])
HELD_HAMMER_QUAT = np.array([0.69627, -0.71712, -0.02065, 0.02252])
HELD_FINGERS = np.array([0.50329, 0.54306, 0.49466, 0.50419, 0.52221, 0.50033])


def _handover_controller():
    """Shrink every action step, and leave every axis free.

    Stock OSC is 5 cm and 0.5 rad per step. The assembly file cut translation
    to 2 cm and 1 cm, then zeroed the sideways axis and the wrist. Those zeros
    cannot steer a hammer, so nothing is locked: 2 cm and 0.02 rad per step.
    """
    config = load_composite_controller_config(robot="XArm7Handover")
    arm = config["body_parts"]["right"]
    arm["output_max"] = list(arm["output_max"])
    arm["output_min"] = list(arm["output_min"])
    # Stock kp 150 only sinks about 1.5 mm per step, so a 300-step episode
    # never reaches the table. 800 tracks the 2 cm position step.
    arm["kp"] = 800
    for i in range(3):
        arm["output_max"][i] = 0.02
        arm["output_min"][i] = -0.02
    for i in range(3, 6):
        arm["output_max"][i] = 0.02
        arm["output_min"][i] = -0.02
    arm["nullspace_kp"] = 40
    return config


def handover_reward(obs, info):
    """Distance-only score from the info dict. obs is unused. Between 0 and 1.

    Read from info:
        handle_pos        handle center, meters.
        ellipsoid_pos     center of the palm sphere, meters.
    """
    handle = np.asarray(info["handle_pos"], dtype=float)
    center = np.asarray(info["ellipsoid_pos"], dtype=float)
    center_dist = float(np.linalg.norm(handle - center))
    # 1 at the sphere center, falling toward 0. 0.15 m is the decay length.
    return float(np.exp(-(center_dist / 0.15) ** 2))


class HumanRobotHandover(ManipulationEnv):
    """
    Handover task with one giver arm and a human receiver.

    Same table, hammer, and gravity warmup as the original handover. The arm that
    used to stand on the +y side of the table is replaced by the Human-Robot Gym
    human. The giver is unchanged.

    Success: the handle center stays within 2 cm of the palm-sphere center for
    3 seconds, no faster than 5 mm/s, without touching the person. Faster motion
    does not score that step and does not end the episode. Touching the person,
    including the hand, ends the episode. The gripper does not have to open.
    """

    def __init__(
        self,
        robots,
        env_configuration="default",
        controller_configs=None,
        gripper_types="default",
        initialization_noise=None,
        table_full_size=(0.8, 1.2, 0.05),
        table_friction=(1.0, 5e-3, 1e-4),
        use_camera_obs=True,
        use_object_obs=True,
        reward_scale=1.0,
        reward_shaping=False,
        placement_initializer=None,
        has_renderer=False,
        has_offscreen_renderer=True,
        render_camera="frontview",
        render_collision_mesh=False,
        render_visual_mesh=True,
        render_gpu_device_id=-1,
        control_freq=20,
        lite_physics=True,
        horizon=300,
        ignore_done=False,
        hard_reset=False,
        camera_names="agentview",
        camera_heights=256,
        camera_widths=256,
        camera_depths=False,
        camera_segmentations=None,
        renderer="mjviewer",
        renderer_config=None,
        seed=0,
        start_holding=True,
    ):
        self.table_full_size = table_full_size
        self.table_true_size = list(table_full_size)
        self.table_true_size[1] *= 0.25
        self.table_friction = table_friction
        self.table_offset = [0, self.table_full_size[1] * (-3 / 8), 0.8]

        self.reward_scale = reward_scale
        self.reward_shaping = reward_shaping
        self._grasp_hold_steps = 0
        # Training starts with the head already pinched.
        self.start_holding = start_holding
        self._hold_steps = 0
        self._task_state_step = -1
        self._task_state = {}

        self.use_object_obs = use_object_obs
        self.placement_initializer = placement_initializer
        if controller_configs is None:
            controller_configs = _handover_controller()

        # Local +Y is up. Rx(+90) stands the person up facing world -Y (the robot);
        # a small yaw turns the chest toward the handover point.
        self._human_root_quat = np.array([0.69727, 0.69727, 0.11756, 0.11756])
        # Toe joints sit near local y = -1.15, which becomes world z after the rotation.
        # Tuned so the lowest foot vertex sits on the floor instead of inside it.
        self._human_foot_drop = 1.162
        # Right palm faces up. R_Elbow_z is opened so the palm sits about 10 cm lower
        # than the stock pose. The person stands 5 cm farther from the robot, so the
        # palm is near (0.01, -0.03, 1.26). Left arm hangs at the side.
        self._human_pose = {
            "R_Shoulder_x": -0.2255,
            "R_Shoulder_y": 1.6255,
            "R_Shoulder_z": -0.0704,
            "R_Elbow_y": -0.1120,
            "R_Elbow_z": 0.2704,
            "R_Elbow_x": 2.4108,
            "R_Wrist_x": 0.9497,
            "R_Wrist_y": 0.3131,
            "R_Wrist_z": 0.2826,
            "L_Shoulder_z": -1.5010,
            "L_Shoulder_x": -0.0522,
            "L_Elbow_y": 0.1557,
        }

        super().__init__(
            robots=robots,
            env_configuration=env_configuration,
            controller_configs=controller_configs,
            base_types="default",
            gripper_types=gripper_types,
            initialization_noise=initialization_noise,
            use_camera_obs=use_camera_obs,
            has_renderer=has_renderer,
            has_offscreen_renderer=has_offscreen_renderer,
            render_camera=render_camera,
            render_collision_mesh=render_collision_mesh,
            render_visual_mesh=render_visual_mesh,
            render_gpu_device_id=render_gpu_device_id,
            control_freq=control_freq,
            lite_physics=lite_physics,
            horizon=horizon,
            ignore_done=ignore_done,
            hard_reset=hard_reset,
            camera_names=camera_names,
            camera_heights=camera_heights,
            camera_widths=camera_widths,
            camera_depths=camera_depths,
            camera_segmentations=camera_segmentations,
            renderer=renderer,
            renderer_config=renderer_config,
            seed=seed,
        )

    def reward(self, action=None):
        """Built-in score. super().step() calls this after the physics update.

        Without shaping this is 1 on success and 0 otherwise, as in the
        original assembly task. Shaping is the distance score only.
        """
        self._sync_task_state()
        if not self.reward_shaping:
            return 1.0 if self._task_state["success"] > 0.5 else 0.0
        return float(self.reward_scale) * handover_reward(None, self._task_state)

    def step(self, action):
        if self.sim.data.time < 0.5:
            self.sim.model.opt.gravity[:] = [0, 0, 0]
        else:
            self.sim.model.opt.gravity[:] = [0, 0, -9.81]

        observations, reward, done, info = super().step(action)
        # reward() already updated the task state for this step.
        self._sync_task_state()
        info.update(self._task_state)
        if info["success"] > 0.5 or info["failure"] > 0.5:
            done = True
        return observations, reward, done, info

    def _sync_task_state(self):
        """Read the simulator once per step and store the fields published in info."""
        if self._task_state_step == self.timestep:
            return
        handle = np.array(self.sim.data.geom_xpos[self.hammer_handle_geom_id], dtype=float)
        speed = float(np.linalg.norm(self._hammer_linear_vel()))
        # A two-pad touch lasts one or two steps and then slips. Eight steps is a
        # seated pinch. Lock it, otherwise the head slips out of the fingers.
        head_grasp = self._check_grasp(
            gripper=self.robots[0].gripper, object_geoms=self._hammer_head_geoms()
        )
        if head_grasp:
            self._grasp_hold_steps += 1
        else:
            self._grasp_hold_steps = 0
        # A centered pinch is stable by the fourth step. The scripted check still
        # waits eight, because a glancing touch used to weld and then slip.
        if self._grasp_hold_steps == 8 and self.sim.model.neq:
            eid = self.sim.model.equality("handover_grasp").id
            if float(self.sim.data.eq_active[eid]) < 0.5:
                self.lock_grasp()
        hand_names = ["human_R_Hand_collision"]
        hammer_on_hand = bool(self.check_contact(self.hammer.all_geoms, hand_names))
        robot_on_hand = bool(self._robot_geoms) and bool(self.check_contact(self._robot_geoms, hand_names))
        hand_contact = hammer_on_hand or robot_on_hand
        body_contact = self._body_contact()
        ellipsoid_pos = np.array(self.sim.data.geom_xpos[self.palm_sensor_id], dtype=float)
        center_dist = float(np.linalg.norm(handle - ellipsoid_pos))
        # Touching the body or the hand fails immediately and cannot also succeed.
        # Faster than 5 mm/s only keeps this step out of the 3 second count.
        touched_person = body_contact or hand_contact
        still = center_dist <= TIER_RADIUS and speed <= CONTACT_SPEED and not touched_person
        self._hold_steps = self._hold_steps + 1 if still else 0
        success = bool(self._hold_steps >= HOLD_STEPS)
        self._task_state = {
            "success": 1.0 if success else 0.0,
            "failure": 1.0 if touched_person else 0.0,
            "body_contact": 1.0 if body_contact else 0.0,
            "hand_contact": 1.0 if hand_contact else 0.0,
            "handle_pos": handle,
            "ellipsoid_pos": ellipsoid_pos,
            "hammer_speed": speed,
            "hold_steps": float(self._hold_steps),
        }
        self._task_state_step = self.timestep

    def _pre_action(self, action, policy_step=False):
        action = np.array(action, dtype=float, copy=True)
        if action.shape[0]:
            if self.start_holding:
                # The fingers stay at the hold command.
                action[-1] = 0.0
            # +1 keeps integrating the finger command up to fully shut, which cams
            # the head out of the pads. 0.8 is the ctrl (~229) that pinches and holds.
            gripper = self.robots[0].gripper["right"]
            held = float(np.asarray(gripper.current_action).ravel()[0])
            if action[-1] > 0.0 and held >= 0.8:
                action[-1] = 0.0
        super()._pre_action(action, policy_step)
        self._hold_human_pose()

    def _load_model(self):
        super()._load_model()

        # Giver keeps the opposed slot that arm0 used in TwoArmHandover.
        robot = self.robots[0]
        base = np.array(robot.robot_model.base_xpos_offset["table"](self.table_full_size[0]), dtype=float)
        giver_rot = np.array((0.0, 0.0, np.pi / 2))
        giver_pos = T.euler2mat(giver_rot) @ base + np.array((0.0, -0.25, 0.0))
        robot.robot_model.set_base_xpos(giver_pos)
        robot.robot_model.set_base_ori(giver_rot)

        # Across the table from the robot, 5 cm farther back than the old spot.
        self._human_root_pos = np.array([0.0199, 0.60, self._human_foot_drop])

        mujoco_arena = TableArena(
            table_full_size=self.table_true_size,
            table_friction=self.table_friction,
            table_offset=self.table_offset,
        )
        mujoco_arena.set_origin([0, 0, 0])
        # Wider than the two-arm handover cameras so the standing person is in frame.
        view_pos = [1.8723793, -1.4154966, 1.8034441]
        view_quat = [0.73321843, 0.53271425, 0.24840894, 0.34190539]
        mujoco_arena.set_camera(camera_name="agentview", pos=view_pos, quat=view_quat)
        mujoco_arena.set_camera(camera_name="frontview", pos=view_pos, quat=view_quat)
        # Side view from +x, and a close frame on the palm sphere.
        mujoco_arena.set_camera(
            camera_name="extra_side_plusx",
            pos=[1.369407, 0.016, 1.441076],
            quat=[0.549525, 0.444997, 0.444997, 0.549525],
        )
        mujoco_arena.set_camera(
            camera_name="extra_palm_close",
            pos=[0.325441, -0.458823, 1.40235],
            quat=[0.7455, 0.572049, 0.208223, 0.271354],
        )

        # Fixed geometry so the held-start pinch stays valid after every reset.
        self.hammer = HammerObject(name="hammer", rng=np.random.default_rng(0))
        self.human = HumanObject(name="human")
        self.human.set_pos(self._human_root_pos)
        self.human.set_quat(self._human_root_quat)

        if self.placement_initializer is not None:
            self.placement_initializer.reset()
            self.placement_initializer.add_objects(self.hammer)
        else:
            # Spin about the vertical so the hammer stays flat on the table.
            rotation_axis = "z"
            self.placement_initializer = UniformRandomSampler(
                name="ObjectSampler",
                mujoco_objects=self.hammer,
                x_range=[-0.1, 0.1],
                y_range=[-0.05, 0.05],
                rotation=None,
                rotation_axis=rotation_axis,
                ensure_object_boundary_in_range=False,
                ensure_valid_placement=True,
                reference_pos=self.table_offset,
                rng=self.rng,
            )

        self.model = ManipulationTask(
            mujoco_arena=mujoco_arena,
            mujoco_robots=[robot.robot_model for robot in self.robots],
            mujoco_objects=[self.hammer, self.human],
        )
        # Off until lock_grasp(). A closed gripper still lets the hammer pivot a few
        # degrees, which walks the handle off the palm. The weld keeps the grasp pose.
        from xml.etree.ElementTree import Element

        self.model.equality.append(
            Element(
                "weld",
                {
                    "name": "handover_grasp",
                    "body1": "gripper0_right_eef",
                    "body2": self.hammer.root_body,
                    "active": "false",
                },
            )
        )
        self._add_palm_sphere()

    def _add_palm_sphere(self):
        """Palm sphere. The center is filled in after the hand pose exists.

        The center is 6 cm out from the hand-mesh center along the palm normal,
        and the radius is 5 cm. Only the hammer collides with it.
        """
        from xml.etree.ElementTree import Element

        hand = find_elements(
            self.human.root, tags="body", attribs={"name": "human_R_Hand"}, return_first=True
        )
        if hand is None:
            raise RuntimeError("human_R_Hand was not found")
        hand.append(
            Element(
                "geom",
                {
                    "name": "human_R_Palm_collision",
                    "type": "sphere",
                    "pos": "0 0 0",
                    "size": "0.05",
                    "contype": "0",
                    "conaffinity": "4",
                    "density": "0",
                    "group": "1",
                    "rgba": "0.15 0.75 1 0.35",
                },
            )
        )

    def _setup_references(self):
        super()._setup_references()
        self.hammer_body_id = self.sim.model.body_name2id(self.hammer.root_body)
        self.hammer_handle_geom_id = self.sim.model.geom_name2id(self.hammer.handle_geoms[0])
        self.hammer_head_geom_id = self.sim.model.geom_name2id(self.hammer.head_geoms[0])

        self.human_body_id = self.sim.model.body_name2id(self.human.root_body)
        self._human_mocap_id = int(self.sim.model.body_mocapid[self.human_body_id])
        self._human_joints = list(self.human.joints)
        wrist_names = [
            g for g in self.human.contact_geoms if "R_Wrist_collision" in g and not g.endswith("_visual")
        ]
        if not wrist_names:
            raise RuntimeError("right wrist collision geom human_R_Wrist_collision was not found")
        self.palm_geom_id = self.sim.model.geom_name2id(wrist_names[0])
        self.hand_geom_id = self.sim.model.geom_name2id("human_R_Hand_collision")
        self.palm_sensor_name = "human_R_Palm_collision"
        self.palm_sensor_id = self.sim.model.geom_name2id(self.palm_sensor_name)
        # Bit 2 (value 4) is only on the hammer, so the palm sphere can see the
        # hammer and not the hand mesh or the robot.
        for name in self.hammer.contact_geoms:
            gid = self.sim.model.geom_name2id(name)
            self.sim.model.geom_contype[gid] = int(self.sim.model.geom_contype[gid]) | 4
        self._cache_contact_geoms()
        # The hand mesh contact is the skin itself. A margin here reaches into the
        # palm sphere, so the handle cannot sit at the center without counting as a touch.
        self.sim.model.geom_margin[self.hand_geom_id] = 0.0
        self.sim.model.geom_gap[self.hand_geom_id] = 0.0
        self.sim.model.geom_solref[self.hand_geom_id] = [0.05, 1.0]
        self.sim.model.geom_solimp[self.hand_geom_id] = [0.4, 0.8, 0.01, 0.5, 2.0]

        # The gripper ships a 10 m debug cylinder that cuts through the person.
        for i in range(self.sim.model.nsite):
            name = self.sim.model.site_id2name(i) or ""
            if "grip_site_cylinder" in name:
                self.sim.model.site_rgba[i][3] = 0.0

    def _cache_contact_geoms(self):
        """Body geoms are every human collision except the right hand mesh.

        The right hand mesh is reported separately as hand_contact. Both end the episode.
        """
        hand_name = self.sim.model.geom_id2name(self.hand_geom_id)
        self._body_geoms = [
            g for g in self.human.contact_geoms if g != hand_name and not str(g).endswith("_visual")
        ]
        self._robot_geoms = []
        robot_geoms = self._robot_geoms
        for i in range(self.sim.model.ngeom):
            name = self.sim.model.geom_id2name(i) or ""
            if name.endswith("_visual"):
                continue
            if not (name.startswith("robot") or name.startswith("gripper")):
                continue
            if int(self.sim.model.geom_contype[i]) == 0 and int(self.sim.model.geom_conaffinity[i]) == 0:
                continue
            robot_geoms.append(name)
        # Floor and table are left out, so feet on the ground are not a failure.
        self._unsafe_geoms = list(self.hammer.all_geoms) + robot_geoms

    def _setup_observables(self):
        observables = super()._setup_observables()
        if self.use_object_obs:
            modality = "object"

            @sensor(modality=modality)
            def hammer_quat(obs_cache):
                return np.array(self._hammer_quat)

            @sensor(modality=modality)
            def handle_pos(obs_cache):
                return np.array(self.sim.data.geom_xpos[self.hammer_handle_geom_id])

            @sensor(modality=modality)
            def head_pos(obs_cache):
                return np.array(self.sim.data.geom_xpos[self.hammer_head_geom_id])

            @sensor(modality=modality)
            def palm_pos(obs_cache):
                return np.array(self.sim.data.geom_xpos[self.palm_geom_id])

            @sensor(modality=modality)
            def hammer_vel(obs_cache):
                return self._hammer_linear_vel()

            sensors = [hammer_quat, handle_pos, head_pos, palm_pos, hammer_vel]
            for s in sensors:
                observables[s.__name__] = Observable(
                    name=s.__name__,
                    sensor=s,
                    sampling_rate=self.control_freq,
                )
        return observables

    def _limit_arm_joints(self):
        """Stop every joint near the bent-elbow pose.

        The xArm file leaves joints 1, 3, 5, and 7 free to spin a full turn.
        The assembly controller only zeroed unused action channels, so those
        four joints were never given a travel limit.
        """
        qidx = np.array(self.robots[0]._ref_joint_pos_indexes)
        self.sim.model.jnt_limited[qidx] = 1
        self.sim.model.jnt_range[qidx] = np.array(
            [
                [-0.45, 0.55],
                [-0.05, 1.05],
                [-0.70, 0.45],
                [0.35, 1.70],
                [-0.50, 0.80],
                [-0.05, 1.55],
                [-1.15, 0.45],
            ]
        )

    def _reset_internal(self):
        super()._reset_internal()
        self._grasp_hold_steps = 0
        self._hold_steps = 0
        self._task_state_step = -1
        self._task_state = {}
        self._limit_arm_joints()
        ctrl = self.robots[0].part_controllers["right"]
        ctrl.initial_joint = np.array(self.robots[0].init_qpos, dtype=float)
        if self.sim.model.neq:
            eid = self.sim.model.equality("handover_grasp").id
            self.sim.model.eq_active0[eid] = 0
            self.sim.data.eq_active[eid] = 0
        self.sim.model.opt.gravity[:] = [0, 0, 0]
        # Keep the person clear while the gripper closes on the hammer.
        reach_pos = self._human_root_pos.copy()
        self._human_root_pos = np.array([2.5, 2.5, self._human_foot_drop])
        self._hold_human_pose()
        self.sim.forward()

        if not self.deterministic_reset:
            object_placements = self.placement_initializer.sample()
            for obj_pos, obj_quat, obj in object_placements.values():
                # Head lies flat (its wide side down) and the handle runs along the table length.
                flat = T.mat2quat(np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]))
                yaw = self.rng.uniform(-0.3, 0.3) + (np.pi if self.rng.uniform() < 0.5 else 0.0)
                quat = T.quat_multiply(T.axisangle2quat(np.array([0.0, 0.0, yaw])), flat)
                pos = np.array([obj_pos[0], obj_pos[1], self.table_offset[2] + self.hammer.head_halfsize + 0.002])
                self.sim.data.set_joint_qpos(
                    obj.joints[0], np.concatenate([pos, T.convert_quat(quat, to="wxyz")])
                )

        self._human_root_pos = reach_pos
        self._hold_human_pose()
        self.sim.forward()

        if self.start_holding:
            self._start_with_head_held()
        self._place_palm_markers()

    def _start_with_head_held(self):
        """Arm at the home pose, fingers closed on the head, hammer welded to the gripper.

        Hammer size is fixed at build time, so this does not depend on seed.
        """
        robot = self.robots[0]
        self.sim.data.qpos[robot._ref_gripper_joint_pos_indexes["right"]] = HELD_FINGERS
        self.sim.forward()
        b1 = self.sim.model.body_name2id("gripper0_right_eef")
        p1 = np.array(self.sim.data.body_xpos[b1], dtype=float)
        r1 = np.array(self.sim.data.body_xmat[b1], dtype=float).reshape(3, 3)
        rel = T.quat2mat(T.convert_quat(HELD_HAMMER_QUAT, to="xyzw"))
        quat = T.convert_quat(T.mat2quat(r1 @ rel), to="wxyz")
        self.sim.data.set_joint_qpos(self.hammer.joints[0], np.concatenate([p1 + r1 @ HELD_HAMMER_POS, quat]))
        self.sim.data.qvel[:] = 0.0
        self.sim.forward()
        self.lock_grasp()
        # 0.8 is the same hold command the gripper cap uses.
        robot.gripper["right"].current_action = np.array([0.8])
        self._grasp_hold_steps = 1
        # Gravity is on from the first step. The hammer is already held.
        self.sim.data.time = 0.5

    def lock_grasp(self):
        """Weld the hammer to the gripper at the pose it has right now."""
        eid = self.sim.model.equality("handover_grasp").id
        b1 = self.sim.model.body_name2id("gripper0_right_eef")
        b2 = self.hammer_body_id
        p1 = np.array(self.sim.data.body_xpos[b1], dtype=float)
        r1 = np.array(self.sim.data.body_xmat[b1], dtype=float).reshape(3, 3)
        p2 = np.array(self.sim.data.body_xpos[b2], dtype=float)
        r2 = np.array(self.sim.data.body_xmat[b2], dtype=float).reshape(3, 3)
        self.sim.model.eq_data[eid, 0:3] = 0.0
        self.sim.model.eq_data[eid, 3:6] = r1.T @ (p2 - p1)
        self.sim.model.eq_data[eid, 6:10] = T.convert_quat(T.mat2quat(r1.T @ r2), to="wxyz")
        self.sim.model.eq_data[eid, 10] = 1.0
        self.sim.model.eq_solref[eid] = [0.002, 1.0]
        self.sim.model.eq_solimp[eid] = [0.99, 0.999, 0.0001, 0.5, 2.0]
        self.sim.model.eq_active0[eid] = 1
        self.sim.data.eq_active[eid] = 1

    def _place_palm_markers(self):
        """Put the palm sphere 6 cm out along the palm normal."""
        center, normal = self._palm_frame()
        sphere = center + PALM_SPHERE_OFFSET * normal
        self._set_geom_world_pos(self.palm_sensor_id, sphere)
        self.sim.model._model.geom_size[self.palm_sensor_id] = [PALM_SPHERE_RADIUS, 0.0, 0.0]
        self.sim.forward()

    def _set_geom_world_pos(self, geom_id, world):
        body = int(self.sim.model.geom_bodyid[geom_id])
        origin = np.array(self.sim.data.body_xpos[body], dtype=float)
        rot = np.array(self.sim.data.body_xmat[body], dtype=float).reshape(3, 3)
        # A zero local pos is compiled as "same frame as the body", which ignores geom_pos.
        self.sim.model._model.geom_sameframe[geom_id] = 0
        self.sim.model._model.geom_quat[geom_id] = np.array([1.0, 0.0, 0.0, 0.0])
        self.sim.model._model.geom_pos[geom_id] = rot.T @ (np.asarray(world, dtype=float) - origin)

    def _palm_frame(self):
        """Palm center and the direction out of the palm.

        The hand mesh is thinnest along its local x axis. The palm faces up, so
        the normal is that axis with its upward direction.
        """
        center = np.array(self.sim.data.geom_xpos[self.hand_geom_id], dtype=float)
        axis = np.array(self.sim.data.geom_xmat[self.hand_geom_id], dtype=float).reshape(3, 3)[:, 0]
        if axis[2] < 0.0:
            axis = -axis
        return center, axis / np.linalg.norm(axis)

    def _hold_human_pose(self):
        """Keep the person standing, right palm up at the handover point."""
        if self._human_mocap_id >= 0:
            self.sim.data.mocap_pos[self._human_mocap_id] = self._human_root_pos
            self.sim.data.mocap_quat[self._human_mocap_id] = self._human_root_quat
        prefix = self.human.naming_prefix
        for name in self._human_joints:
            short = name[len(prefix):] if name.startswith(prefix) else name
            self.sim.data.set_joint_qpos(name, self._human_pose.get(short, 0.0))
            addr = self.sim.model.get_joint_qvel_addr(name)
            if isinstance(addr, tuple):
                self.sim.data.qvel[addr[0] : addr[1]] = 0.0
            else:
                self.sim.data.qvel[addr] = 0.0

    def _hammer_head_geoms(self):
        """Head, face, neck, and claw. The handle is the only other part."""
        return self.hammer.head_geoms + self.hammer.face_geoms + self.hammer.claw_geoms

    def _hammer_linear_vel(self):
        addr = self.sim.model.get_joint_qvel_addr(self.hammer.joints[0])
        start = int(addr[0]) if isinstance(addr, tuple) else int(addr)
        return np.array(self.sim.data.qvel[start : start + 3], dtype=float)

    def _body_contact(self):
        """Hammer or robot touching the person anywhere except the right hand mesh."""
        if not self._body_geoms or not self._unsafe_geoms:
            return False
        return bool(self.check_contact(self._body_geoms, self._unsafe_geoms))

    def _check_success(self):
        """True after the handle has stayed in the 2 cm ball at or below 5 mm/s for 3 seconds."""
        return bool(self._hold_steps >= HOLD_STEPS)

    @property
    def _hammer_quat(self):
        return T.convert_quat(self.sim.data.body_xquat[self.hammer_body_id], to="xyzw")
