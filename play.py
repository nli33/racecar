from config import get_config
from game import Game
import numpy as np
from renderer import Renderer
from stable_baselines3 import PPO

center_car = True
show_alt_car = True

if __name__ == "__main__":
    game = Game(get_config(), has_alt_car=show_alt_car)
    renderer = Renderer(game, centered=center_car)
    states = []
    model = PPO.load("racecar_ppo_model")
    
    while True:
        action = renderer.handle_events()
        if renderer.stopped:
            break
        if show_alt_car and game.first_step is not None:
            obs = np.append(game.get_raycasts(alt_car=True), np.float32(game.car.v))
            alt_action, _ = model.predict(obs, deterministic=True)
            game.step(action, alt_action)
        else:
            game.step(action, np.array([0, 0, 0, 0]))
        renderer.render()