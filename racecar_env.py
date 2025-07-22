from game import Game
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from renderer import Renderer

'''
observation space: range of valid observations passed to agent
action space: range of valid actions agent can take

RacecarEnv encloses a Game instance, it's basically a thin wrapper around Game
'''

class RacecarEnv(gym.Env):
    metadata = {"render_modes": ["human"], "render_fps": 30}
    
    def __init__(self, config: dict, render_mode=None):
        super().__init__()
        self.render_mode = render_mode
        self.game = Game(config)
        self.renderer = None
        self.raycast_angles = config.get("raycast_angles")
        num_raycast_angles = len(self.raycast_angles)
        self.action_space = spaces.MultiBinary(4)  # accel, left, right, brake
        # self.action_space = spaces.MultiDiscrete([3, 3])  # (none, left, right), (none, brake, accel)
        self.observation_space = spaces.Box(
            low=np.array([0.0]*num_raycast_angles + [0.0]),  # 0 for rays, 0 for speed
            high=np.array([self.game.track.diagonal]*num_raycast_angles + [self.game.car.max_v]),  # 10 for rays, 3 for speed
            dtype=np.float32
        )
    
    
    # initialize or reset environment to starting state
    # returns:
    # - observation: observation space
    # - info: diagnostic metadata
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.game.reset()
        # reset internal state
        obs = self._get_observation()
        info = {}
        return obs, info


    # apply an action, then advance environment by one timestep/frame
    # returns:
    # - obs: next state observation
    # - reward: numeric feedback
    # - terminated: episode ended naturally (goal reached / death) - bool
    # - truncated: terminated due to timeout or external limit
    # - info: optional debug info
    def step(self, action):
        # apply action, update state
        self.game.step(action)
        # print(self.game.step_count)
        obs = self._get_observation()
        reward = self._compute_reward()
        terminated = self._is_done()
        truncated = False # self.step_count >= self.max_steps
        info = {}
        if terminated:
            print("w", self.game.step_count)
        return obs, reward, terminated, truncated, info


    def render(self):
        if self.renderer is None:
            self.renderer = Renderer(self.game)
            
        if self.render_mode == 'human':
            self.renderer.handle_events()
            if self.renderer.stopped:
                raise RuntimeError("pygame GUI was closed")
            self.renderer.render()
        # elif self.render_mode == 'rgb_array':


    def close(self):
        if self.renderer is not None:
            self.renderer.close()
            self.renderer = None
    
    
    def _compute_reward(self):
        if self.game.car.crashed:
            return -150
        if self.game.car.reached_goal:
            return 150
        speed_ratio = self.game.car.v / self.game.car.max_v
        # more heavily reward speeds close to max
        speed_reward = 4 * speed_ratio**2
        return speed_reward
    
    
    def _get_observation(self):
        rays = self.game.get_raycasts()
        rays = np.array(rays, dtype=np.float32)
        speed = np.float32(self.game.car.v)
        return np.append(rays, speed)
    
    
    def _is_done(self):
        return self.game.is_done()