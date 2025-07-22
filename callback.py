from stable_baselines3.common.callbacks import BaseCallback

'''
callback: 
- mechanism to execute custom code at points in training process
- monitor/log/modify training behaviour
'''


class RenderCallback(BaseCallback):
    def __init__(self, render_freq=1000, verbose=0):
        super().__init__(verbose)
        
        # render every X steps
        self.render_freq = render_freq
        self.episode_rewards = []
        self.episode_steps = []
        self.current_reward = 0
        self.current_steps = 0

    def _on_step(self):
        self.current_reward += self.locals["rewards"]
        self.current_steps += 1
        
        if self.n_calls % self.render_freq == 0 and self.locals["env"].render_mode == "human":
            try:
                self.locals["env"].render()
            except RuntimeError as e:
                if str(e) == "pygame GUI was closed":
                    print("Training stopped: pygame GUI was closed")
                    return False  # Stop training
                raise e
        
        # log episode metrics
        if self.locals["dones"]:
            self.episode_rewards.append(self.current_reward)
            self.episode_steps.append(self.current_steps)
            print(f"Episode {len(self.episode_rewards)}: Reward = {self.current_reward}, Steps = {self.current_steps}")
            self.current_reward = 0
            self.current_steps = 0
        return True