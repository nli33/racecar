from config import get_config
from game import Game
from renderer import Renderer

if __name__ == "__main__":
    game = Game(get_config())
    renderer = Renderer(game)
    while True:
        action = renderer.handle_events()
        if renderer.stopped:
            break
        game.step(action)
        print(game.get_raycasts())
        renderer.render()