from config import get_config, write_config
from enum import Enum
from renderer import SPACE, GRIDLINE, draw_tile, draw_goal, draw_spawn
import pygame

class Mode(Enum):
    TILE = 0
    GOAL = 1
    DELETE = 2
    SPAWN = 3

pygame.init()

config = get_config()
tiles = config.get("tiles", [])
goal = config.get("goal")
spawn = config.get("spawn")
canvas_w = config.get("width", 700)
canvas_h = config.get("height", 600)
mode = Mode.TILE
tile_size = 100
keybinds = {
    pygame.K_d: "delete",
    pygame.K_t: "tile",
    pygame.K_g: "goal",
    pygame.K_s: "save",
    pygame.K_b: "spawn",
}

MIN_TILE_SIZE = 25
MAX_TILE_SIZE = 200
LINE_WIDTH = 2

screen = pygame.display.set_mode((canvas_w, canvas_h))

def round_down_to_multiple(n, x):
    return n - (n % x)

try:
    running = True
    while running:
        events = pygame.event.get()
        mx, my = pygame.mouse.get_pos()
        rx = round_down_to_multiple(mx, MIN_TILE_SIZE)
        ry = round_down_to_multiple(my, MIN_TILE_SIZE)
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if 0 <= mx < canvas_w and 0 <= mx < canvas_h:
                    if mode == Mode.TILE:
                        tiles.append((rx, ry, tile_size, tile_size))
                    elif mode == Mode.DELETE:
                        for tile in tiles[:]:
                            x, y, w, h = tile
                            if x <= mx < x+w and y <= my < y+h:
                                tiles.remove(tile)
                    elif mode == Mode.GOAL:
                        goal = (rx, ry, tile_size, tile_size)
                    elif mode == Mode.SPAWN:
                        spawn = (rx, ry)
                else:
                    pass
            
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                for key, action in keybinds.items():
                    if not keys[key]:
                        continue
                    if action == "delete":
                        mode = Mode.DELETE
                    elif action == "tile":
                        mode = Mode.TILE
                    elif action == "goal":
                        mode = Mode.GOAL
                    elif action == "spawn":
                        mode = Mode.SPAWN
                    elif action == "save":
                        config["tiles"] = tiles
                        config["goal"] = goal
                        config["spawn"] = spawn
                        write_config(config)
                        print("Saved")
                
                if keys[pygame.K_DOWN]:
                    tile_size = max(MIN_TILE_SIZE, tile_size-25)
                elif keys[pygame.K_UP]:
                    tile_size = min(MAX_TILE_SIZE, tile_size+25)
        
        # pygame.draw.rect(screen, SPACE, (0, 0, canvas_w, canvas_h))
        screen.fill(SPACE)
        
        # draw tiles/goals
        for tile in tiles:
            draw_tile(screen, tuple(tile))
        if goal is not None:
            draw_goal(screen, goal)
        if spawn is not None:
            draw_spawn(screen, spawn)
        
        # draw gridlines
        for x in range(0, canvas_w, 100):
            pygame.draw.rect(screen, GRIDLINE, (x, 0, LINE_WIDTH, canvas_h))
        for y in range(0, canvas_h, 100):
            pygame.draw.rect(screen, GRIDLINE, (0, y, canvas_w, LINE_WIDTH))
        
        # draw hover preview
        if mode == Mode.GOAL:
            draw_goal(screen, (rx, ry, tile_size, tile_size))
        elif mode == Mode.TILE:
            draw_tile(screen, (rx, ry, tile_size, tile_size))
        elif mode == Mode.SPAWN:
            draw_spawn(screen, (rx, ry))
        
        pygame.display.flip()
        
finally:
    pygame.quit()