from config import get_config
from game import Game
from renderer import Renderer

center_car = True

if __name__ == "__main__":
    game = Game(get_config())
    renderer = Renderer(game, centered=center_car)
    states = []
    
    while True:
        action = renderer.handle_events()
        if renderer.stopped:
            break
        game.step(action)
        renderer.render()