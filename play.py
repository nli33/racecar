from config import get_config
from game import Game
import numpy as np
from renderer import Renderer
from stable_baselines3 import PPO
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Racecar play mode")
    parser.add_argument('--center', action='store_true', help='center view on player car')
    parser.add_argument('--agent', metavar='MODEL', type=str, help='show RL agent given filename of model')
    args = parser.parse_args()

    center_car = args.center
    show_alt_car = args.agent is not None

    game = Game(get_config(), has_alt_car=show_alt_car)
    renderer = Renderer(game, centered=center_car)
    states = []
    if show_alt_car:
        model = PPO.load(args.agent)
    else:
        model = None

    while True:
        action = renderer.handle_events()
        if renderer.stopped:
            break
        if show_alt_car and game.first_step is not None:
            obs = np.append(game.get_raycasts(alt_car=True), np.float32(game.car.v))
            alt_action, _ = model.predict(obs, deterministic=False)
            game.step(action, alt_action)
        else:
            game.step(action, np.array([0, 0, 0, 0]))
        game.check_waypoints()
        renderer.render()
