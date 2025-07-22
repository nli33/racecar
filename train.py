from config import get_config
from stable_baselines3 import PPO
from callback import RenderCallback
from racecar_env import RacecarEnv

env = RacecarEnv(get_config())

model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=1,
    seed=42
)

model.learn(total_timesteps=100000)

model.save("racecar_ppo_model")