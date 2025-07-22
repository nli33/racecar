from config import get_config
from racecar_env import RacecarEnv
from stable_baselines3 import PPO

env = RacecarEnv(config=get_config(), render_mode="human")
model = PPO.load("racecar_ppo_model")

try:
    obs, _ = env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        done = terminated or truncated
        if env.render_mode == "human":
            env.render()
except RuntimeError as e:
    if str(e) == "pygame GUI was closed":
        print("pygame GUI was closed")
    else:
        raise e
finally:
    env.close()