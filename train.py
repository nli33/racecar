from config import get_config
import gymnasium as gym
from env import RacecarEnv
from stable_baselines3 import PPO

env = RacecarEnv(get_config())

model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=1,
    seed=42
)

model.learn(total_timesteps=100000)

model.save("racecar_ppo_model")