from callback import Callback
from config import get_config
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from racecar_env import RacecarEnv
from stable_baselines3 import PPO

env = RacecarEnv(config=get_config(), render_mode="human")

load_pretrained = True

if load_pretrained:
    model = PPO.load("racecar_ppo_model", env=env)
else:
    model = PPO(
        policy="MlpPolicy",
        env=env,
        verbose=1,
        seed=1)

callback = Callback(render_freq=20)
try:
    model.learn(total_timesteps=100000, callback=callback)
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

    # legend_patches = [
    #     mpatches.Patch(color='green', label='success'),
    #     mpatches.Patch(color='red', label='crash'),
    #     mpatches.Patch(color='orange', label='timeout'),
    #     mpatches.Patch(color='gray', label='other'),
    # ]
    # plt.legend(handles=legend_patches, title='Outcome')

    plt.savefig("training.png")
    
    model.save("racecar_ppo_model")
finally:
    env.close()