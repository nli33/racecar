from config import get_config
from stable_baselines3 import PPO
from callback import RenderCallback
from racecar_env import RacecarEnv

env = RacecarEnv(config=get_config(), render_mode="human")

model = PPO(
    policy="MlpPolicy",
    env=env,
    verbose=1,
    seed=1)

callback = RenderCallback(render_freq=1000)
try:
    model.learn(total_timesteps=100000, callback=callback)
except RuntimeError as e:
    if str(e) == "Pygame GUI was closed by the user":
        print("Training stopped")
    else:
        raise e
finally:
    env.close()

model.save("racecar_ppo_model")