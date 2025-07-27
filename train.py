import argparse
from callback import Callback
from config import get_config
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
from racecar_env import RacecarEnv
from stable_baselines3 import PPO

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Racecar agent training")
    parser.add_argument('model', nargs='?', default='model', help='model filename to save/load')
    parser.add_argument('--legend', action='store_true', help='show legend on training progress plot')
    parser.add_argument('--plot', type=str, default='training.png', help='filename to save training plot image')
    parser.add_argument('--timesteps', type=int, default=100000, help='number of timesteps to train for')
    args = parser.parse_args()
    
    env = RacecarEnv(config=get_config(), render_mode="human")
    
    model_filename = args.model
    if not model_filename.endswith('.zip'):
        model_filename += '.zip'
    if os.path.exists(model_filename):
        model = PPO.load(model_filename, env=env)
    else:
        model = PPO(
            policy="MlpPolicy",
            env=env,
            verbose=1,
            seed=1)

    callback = Callback(render_freq=20)
    try:
        model.learn(total_timesteps=args.timesteps, callback=callback)
    except RuntimeError as e:
        print("Model not saved:", e)
    else:
        # plot training metrics
        rewards = callback.episode_rewards
        steps = callback.episode_steps
        outcomes = callback.episode_outcomes
        colors = {'success': 'green', 'crash': 'red', 'timeout': 'orange'}
        episode_colors = [colors.get(o, 'gray') for o in outcomes]
        print(outcomes)
        plt.figure(figsize=(10, 5))
        scatter = plt.scatter(range(len(steps)), steps, c=episode_colors)
        plt.xlabel('Episode')
        plt.ylabel('Steps')
        plt.title('Training results')

        if args.legend:
            legend_patches = [
                mpatches.Patch(color='green', label='success'),
                mpatches.Patch(color='red', label='crash'),
                mpatches.Patch(color='orange', label='timeout'),
                mpatches.Patch(color='gray', label='other'),
            ]
            plt.legend(handles=legend_patches, title='Outcome')

        plt.savefig(args.plot)
        
        model.save(model_filename)
    finally:
        env.close()