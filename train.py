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
# use the line below to load a pre-trained model (i.e. continue training an existing one)
# model = PPO.load("racecar_ppo_model", env=env)

callback = RenderCallback(render_freq=20)
try:
    model.learn(total_timesteps=100000, callback=callback)
except RuntimeError as e:
    if str(e) == "pygame GUI was closed":
        print("Training stopped, model not saved")
    else:
        raise e
else:
    model.save("racecar_ppo_model")
finally:
    env.close()