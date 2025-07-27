import argparse
from config import get_config
from racecar_env import RacecarEnv
from stable_baselines3 import PPO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test a trained racecar agent")
    parser.add_argument('model', nargs='?', default='model', help='model filename to load')
    args = parser.parse_args()
    model_filename = args.model

    env = RacecarEnv(config=get_config(), render_mode="human")
    model = PPO.load(model_filename)

    try:
        obs, _ = env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=False)
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