from collections import OrderedDict
import numpy as np

import robosuite.utils.transform_utils as T
from robosuite.environments.manipulation.two_arm_env import TwoArmEnv
from robosuite.models.arenas import TableArena
from robosuite.models.tasks import ManipulationTask
from robosuite.utils.observables import Observable, sensor

# These must exist in robosuite.models.objects.__init__ (or import from your module path)
from robosuite.models.objects import FreeTimberObject, BaseTimberObject


class TwoArmAssembly(TwoArmEnv):
    """
    Two-arm assembly task:
      - One free timber
      - Two fixed base timbers (each has ONE notch site named "notch")
        We instantiate TWO BaseTimberObject instances and place them on the table.

    Args:
        robots (str or list of str): Specification for specific robot(s)
            Note: Must be 2 robots!

        env_configuration (str): Specifies how to position the robots.
            :`'parallel'`: Robots next to each other.
            :`'opposed'`: Robots across from each other.

        controller_configs (str or list of dict): parameters for the controller.

        gripper_types (str or list of str): type of gripper.

        initialization_noise (dict or list of dict): joint position noise.

        prehensile (bool): If true, the timber starts on the table. 

        table_full_size (3-tuple): x, y, and z dimensions of the table.

        use_camera_obs (bool): if True, include rendered image(s) in observations.

        use_object_obs (bool): if True, include object information in observations.

        reward_shaping (bool): if True, use dense rewards.

        has_renderer (bool): If true, render the simulation state in a viewer.

        horizon (int): Every episode lasts for exactly @horizon timesteps.
    """

    def __init__(
        self,
        robots,
        env_configuration="default",
        controller_configs=None,
        gripper_types="default",
        initialization_noise="default",
        prehensile=False,
        table_full_size=(0.8, 0.8, 0.05),
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
        horizon=1000,
        ignore_done=False,
        hard_reset=True,
        camera_names="agentview",
        camera_heights=256,
        camera_widths=256,
        camera_depths=False,
        camera_segmentations=None,
        renderer="mjviewer",
        renderer_config=None,
        seed=None,
        frozen_arm0=False,
    ):
        # --- Task settings ---
        self.prehensile = prehensile
        self.frozen_arm0 = frozen_arm0
        self.use_object_obs = use_object_obs
        self.use_camera_obs = use_camera_obs
        # --- Settings for table top ---
        self.table_full_size = table_full_size
        self.table_friction = table_friction
        self.table_offset = np.array((0.0, 0.0, 0.8))

        # --- Settings for robot pose ---
        self.arm0_home_qpos = np.array([0.0, 0.4, 0.0, 1.0, 0.0, 0.5, 0.0])
        self.arm1_home_qpos = np.array([0.0, 0.4, 0.0, 1.0, 0.0, 0.5, 0.0])
        self.notch_distance_threshold = 0.002  # meters

        # --- Reward configuration ---
        self.reward_scale = reward_scale
        self.reward_shaping = reward_shaping

        # --- Base timber layout (Target Layout) ---
        self.base0_world_pos = self.table_offset + np.array([0.0, -0.2255, 0.035])
        self.base1_world_pos = self.table_offset + np.array([0.0, 0.2255, 0.035])
        self.base0_world_quat = np.array([0.0, -0.707, 0.0, 0.707])  # MuJoCo quat = (w, x, y, z)
        self.base1_world_quat = np.array([0.707, 0.0, 0.707, 0.0])  # MuJoCo quat = (w, x, y, z)


        # --- Object placement initializer ---
        self.placement_initializer = placement_initializer

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

    # -----------------
    # Reward / Step
    # -----------------

    def reward(self, action=None):
        """
        Reward function for the task.
        
        Sparse: 1.0 for success.
        Dense: Guided rewards for grasping, proximity, and alignment.
        """
        # 1. Success Check (Used for both Sparse and Dense)
        success = self._check_success()
        
        # --- SPARSE REWARD LOGIC ---
        if not self.reward_shaping:
            return 1.0 if success else 0.0

        # --- DENSE REWARD LOGIC ---
        # 2. Grab task info
        d0, d1, arm0_grasp, arm1_grasp = self._get_task_info()
        
        # 3. Grasping Reward (Keep the timber in hand)
        # We reward the robot for having both hands on the stick
        grasp_reward = 0.0
        if arm0_grasp: grasp_reward += 0.5
        if arm1_grasp: grasp_reward += 0.5
        
        # 4. Notch Alignment Reward (Reduced distance)
        # We use a tanh-based reach reward so it scales between 0 and 1
        # d0 and d1 are the distances from free notches to base notches
        avg_dist = (d0 + d1) / 2.0
        alignment_reward = 2.0 * (1.0 - np.tanh(10.0 * avg_dist))
        
        # 5. Success Bonus
        success_bonus = 5.0 if success else 0.0
        
        # 6. Penalty for dropping (Termination/Survival penalty)
        # If no one is holding the stick, the reward drops significantly
        drop_penalty = 0.0
        if not arm0_grasp and not arm1_grasp:
            drop_penalty = -2.0

        # Total Shaped Reward
        reward = grasp_reward + alignment_reward + success_bonus + drop_penalty

        # Scale if necessary
        if self.reward_scale is not None:
            reward *= self.reward_scale
            
        return reward

    def step(self, action):
        """
        Same as the parent step, but handles gravity warmup.
        """
        # --- GRAVITY WARMUP LOGIC ---
        if self.sim.data.time < 1:
            self.sim.model.opt.gravity[:] = [0.0, 0.0, 0.0]
        else:
            self.sim.model.opt.gravity[:] = [0.0, 0.0, -9.81]
            #self.sim.model.opt.gravity[:] = [0.0, 0.0, 0]

        # Let robosuite handle physics + reward + normal termination
        obs, rew, done, info = super().step(action)

        # Grab task info
        d0, d1, arm0_grasp_timber, arm1_grasp_timber = self._get_task_info()
        success = self._check_success()

        # Update info dict
        info["success"] = 1.0 if success else 0.0
        done = True if success else done

        # Requested assembly info
        info["free_notch0_to_base0_notch_dist"] = float(d0)
        info["free_notch1_to_base1_notch_dist"] = float(d1)
        info["arm0_grasp_timber"] = 1.0 if arm0_grasp_timber else 0.0
        info["arm1_grasp_timber"] = 1.0 if arm1_grasp_timber else 0.0
        info["mutual_grasp"] = 1.0 if (arm0_grasp_timber and arm1_grasp_timber) else 0.0

        return obs, rew, done, info

    # -----------------
    # Model loading
    # -----------------

    def _load_model(self):
        """
        Loads an xml model, puts it in self.model
        """
        super()._load_model()

        # --- Robot base placement ---
        if self.env_configuration == "single-robot":
            xpos = self.robots[0].robot_model.base_xpos_offset["table"](self.table_full_size[0])
            self.robots[0].robot_model.set_base_xpos(xpos)
        else:
            if self.env_configuration == "opposed":
                for robot, rotation, offset in zip(self.robots, (np.pi / 2, -np.pi / 2), (-0.1, 0.1)):
                    xpos = robot.robot_model.base_xpos_offset["table"](self.table_full_size[0])
                    rot = np.array((0.0, 0.0, rotation))
                    xpos = T.euler2mat(rot) @ np.array(xpos)
                    xpos += np.array((0.0, offset, 0.0))
                    robot.robot_model.set_base_xpos(xpos)
                    robot.robot_model.set_base_ori(rot)
            else:  # parallel
                for robot, offset in zip(self.robots, (-0.25, 0.25)):
                    xpos = robot.robot_model.base_xpos_offset["table"](self.table_full_size[0])
                    xpos = np.array(xpos) + np.array((0.0, offset, 0.0))
                    robot.robot_model.set_base_xpos(xpos)

        # --- Load model for arena ---
        mujoco_arena = TableArena(
            table_full_size=self.table_full_size,
            table_friction=self.table_friction,
            table_offset=self.table_offset,
        )
        mujoco_arena.set_origin([0.0, 0.0, 0.0])
        mujoco_arena.set_camera(
            camera_name="agentview",
            pos=[0.8894354364730311, -3.481824231498976e-08, 1.7383813133506494],
            quat=[0.6530981063842773, 0.2710406184196472, 0.27104079723358154, 0.6530979871749878],
        )

        # --- Initialize objects of interest ---
        self.base_timber0 = BaseTimberObject(name="base_timber0")
        self.base_timber1 = BaseTimberObject(name="base_timber1")
        self.free_timber = FreeTimberObject(name="free_timber")

        # Sampler disabled for absolute fixed placement
        self.placement_initializer = None

        # --- Task includes arena, robot, and objects ---
        self.model = ManipulationTask(
            mujoco_arena=mujoco_arena,
            mujoco_robots=[robot.robot_model for robot in self.robots],
            mujoco_objects=[self.base_timber0, self.base_timber1, self.free_timber],
        )

    def _setup_observables(self):
        """
        Sets up observables to be used for this environment. 
        """
        observables = super()._setup_observables()

        # 1. Timber Position and Rotation
        @sensor(modality="object")
        def free_timber_pos(obs_cache):
            return np.array(self._free_timber_pos)

        @sensor(modality="object")
        def free_timber_quat(obs_cache):
            return T.convert_quat(self.sim.data.body_xquat[self.free_body_id], to="xyzw")

        # 2. Relative: Grippers to free timber
        @sensor(modality="object")
        def gripper0_to_timber(obs_cache):
            arm_name = self.robots[0].arms[0]
            eef_id = self.robots[0].eef_site_id[arm_name]
            return self._free_timber_pos - self.sim.data.site_xpos[eef_id]

        @sensor(modality="object")
        def gripper1_to_timber(obs_cache):
            arm_name = self.robots[1].arms[0]
            eef_id = self.robots[1].eef_site_id[arm_name]
            return self._free_timber_pos - self.sim.data.site_xpos[eef_id]

        # 3. Relative: Free Notch to Base Notch
        @sensor(modality="object")
        def notch0_to_base0(obs_cache):
            return self._free_notch_0_xpos - self._base_notch_0_xpos

        @sensor(modality="object")
        def notch1_to_base1(obs_cache):
            return self._free_notch_1_xpos - self._base_notch_1_xpos

        sensors = [
            free_timber_pos, free_timber_quat, 
            gripper0_to_timber, gripper1_to_timber, 
            notch0_to_base0, notch1_to_base1
        ]
        
        for s in sensors:
            observables[s.__name__] = Observable(
                name=s.__name__,
                sensor=s,
                sampling_rate=self.control_freq,
            )

        return observables

    # -----------------
    # References
    # -----------------

    def _setup_references(self):
        """
        Sets up references to important MuJoCo components.
        """
        super()._setup_references()

        self.base0_body_id = self.sim.model.body_name2id(self.base_timber0.root_body)
        self.base1_body_id = self.sim.model.body_name2id(self.base_timber1.root_body)

        self.base_0_notch_id = self.sim.model.site_name2id(self.base_timber0.important_sites["notch"])
        self.base_1_notch_id = self.sim.model.site_name2id(self.base_timber1.important_sites["notch"])
        self.free_notch_0_id = self.sim.model.site_name2id(self.free_timber.important_sites["notch_0"])
        self.free_notch_1_id = self.sim.model.site_name2id(self.free_timber.important_sites["notch_1"])

        self.free_body_id = self.sim.model.body_name2id(self.free_timber.root_body)

    # -----------------
    # Reset
    # -----------------

    def _reset_internal(self):
        """
        Handles the reset of internal simulation state.
        Now spawns timber at a fixed table position even when starting 'in-hand'.
        Mimics TwoArmHandover: force-close BOTH grippers during stabilization so grasps register.
        """
        super()._reset_internal()

        # 1. Zero out gravity for the setup phase
        self.sim.model.opt.gravity[:] = [0, 0, 0]

        # 2. SET BASE TIMBERS
        self.sim.model.body_pos[self.base0_body_id] = self.base0_world_pos
        self.sim.model.body_quat[self.base0_body_id] = self.base0_world_quat
        self.sim.model.body_pos[self.base1_body_id] = self.base1_world_pos
        self.sim.model.body_quat[self.base1_body_id] = self.base1_world_quat

        # 3. Set Robots to Home Poses
        def set_arm_qpos(robot, q):
            idxs = robot._ref_joint_pos_indexes[: len(q)]
            self.sim.data.qpos[idxs] = q

        if len(self.robots) >= 2:
            set_arm_qpos(self.robots[0], self.arm0_home_qpos)
            set_arm_qpos(self.robots[1], self.arm1_home_qpos)
        
        self.arm0_joint_idxs = self.robots[0]._ref_joint_pos_indexes
        self.arm1_joint_idxs = self.robots[1]._ref_joint_pos_indexes
        
        self.sim.forward() 

        # 4. Placement Logic (MODIFIED)
        if self.prehensile:
            # Table placement for prehensile mode
            stick_offset = np.array([0.0, 0.0, 0.1]) 
            target_pos = self.table_offset + stick_offset
            target_quat = T.mat2quat(T.euler2mat(np.radians([90, 0, 0])))
        else:
            # Table placement for non-prehensile mode (as requested)
            stick_offset = np.array([0.0, 0.0, 0.2]) 
            target_pos = self.table_offset + stick_offset
            target_quat = T.mat2quat(T.euler2mat(np.radians([90, 0, 0])))

        # 5. The Stabilization Loop (100 Steps)
        for _ in range(100):
            if self.free_timber.joints:
                self.sim.data.set_joint_qpos(
                    self.free_timber.joints[0], 
                    np.concatenate([target_pos, target_quat])
                )
            
            for robot in self.robots:
                arm_name = robot.arms[0]
                torques = robot.part_controllers[arm_name].torque_compensation
                self.sim.data.ctrl[robot._ref_arm_joint_actuator_indexes] = torques

            # ---- FORCE CLOSE BOTH GRIPPERS (Mimic TwoArmHandover) ----
            for robot in self.robots:
                arm_name = robot.arms[0]
                gripper = robot.gripper[arm_name]

                gripper_ac = [1] * gripper.dof
                gripper_ac = gripper.format_action(gripper_ac)

                gripper_ctrl_name = f"{arm_name}_gripper"
                if gripper_ctrl_name in robot.part_controllers:
                    robot.part_controllers[gripper_ctrl_name].set_goal(gripper_ac)
                else:
                    # Fallback in case controller naming differs
                    if "gripper" in robot.part_controllers:
                        robot.part_controllers["gripper"].set_goal(gripper_ac)
            # ---------------------------------------------------------

            self.sim.step()

        self.sim.forward()

    # -----------------
    # Task info / Success
    # -----------------

    def _get_task_info(self):
        """
        Grabs current locations of notches and grasps.
        """
        free0_to_base0 = float(np.linalg.norm(self._free_notch_0_xpos - self._base_notch_0_xpos))
        free1_to_base1 = float(np.linalg.norm(self._free_notch_1_xpos - self._base_notch_1_xpos))

        # Check grasps
        g0, g1 = self.robots[0].gripper, self.robots[1].gripper
        timber_geom = self.free_timber.timber_geom

        arm0_name = self.robots[0].arms[0]
        arm1_name = self.robots[1].arms[0]

        arm0_grasp_timber = bool(self._check_grasp(gripper=g0[arm0_name], object_geoms=timber_geom))
        arm1_grasp_timber = bool(self._check_grasp(gripper=g1[arm1_name], object_geoms=timber_geom))

        return free0_to_base0, free1_to_base1, arm0_grasp_timber, arm1_grasp_timber

    def _check_success(self):
        """
        Check if notches are aligned and robots are grasping.
        """
        free0_to_base0, free1_to_base1, arm0_grasp_timber, arm1_grasp_timber = self._get_task_info()
        is_aligned = (free0_to_base0 < self.notch_distance_threshold) and (free1_to_base1 < self.notch_distance_threshold)
        #return bool(arm0_grasp_timber and arm1_grasp_timber and is_aligned)
        return bool(is_aligned)

    # -----------------
    # Position properties
    # -----------------

    @property
    def _free_timber_pos(self):
        return np.array(self.sim.data.body_xpos[self.free_body_id])

    @property
    def _free_notch_0_xpos(self):
        return np.array(self.sim.data.site_xpos[self.free_notch_0_id])

    @property
    def _free_notch_1_xpos(self):
        return np.array(self.sim.data.site_xpos[self.free_notch_1_id])

    @property
    def _base_notch_0_xpos(self):
        return np.array(self.sim.data.site_xpos[self.base_0_notch_id])

    @property
    def _base_notch_1_xpos(self):
        return np.array(self.sim.data.site_xpos[self.base_1_notch_id])
