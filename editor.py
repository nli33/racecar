from config import get_config, write_config
from enum import Enum
from renderer import SPACE, GRIDLINE, draw_tile, draw_goal, draw_spawn, draw_waypoint, draw_waypoint_endpoint
import pygame

class Mode(Enum):
    TILE = 0
    GOAL = 1
    DELETE = 2
    SPAWN = 3
    WAYPOINT = 4

pygame.init()

config = get_config()
tiles = config.get("tiles", [])
goal = config.get("goal")
spawn = config.get("spawn")
waypoints = config.get("waypoints", []) # represented as tuples in the editor
waypoint_endpoint = None
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
    pygame.K_w: "waypoint",
    pygame.K_ESCAPE: "clear_waypoint",
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
                if mode == Mode.TILE:
                    tiles.append((rx, ry, tile_size, tile_size))
                elif mode == Mode.DELETE:
                    for tile in tiles[:]:
                        x, y, w, h = tile
                        if x <= mx < x+w and y <= my < y+h:
                            tiles.remove(tile)
                    for waypoint in waypoints[:]:
                        start, end = waypoint
                        if abs(start[0] - mx) < 10 and abs(start[1] - my) < 10:
                            waypoints.remove(waypoint)
                        elif abs(end[0] - mx) < 10 and abs(end[1] - my) < 10:
                            waypoints.remove(waypoint)
                elif mode == Mode.GOAL:
                    goal = (rx, ry, tile_size, tile_size)
                elif mode == Mode.SPAWN:
                    spawn = (rx, ry)
                elif mode == Mode.WAYPOINT:
                    if waypoint_endpoint is None:
                        waypoint_endpoint = (rx, ry)
                    else:
                        waypoints.append((waypoint_endpoint, (rx, ry)))
                        waypoint_endpoint = None
            
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
                        config["waypoints"] = waypoints
                        write_config(config)
                        print("Saved")
                    elif action == "waypoint":
                        mode = Mode.WAYPOINT
                    elif action == "clear_waypoint":
                        waypoint_endpoint = None
                
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
        
        # draw waypoints
        for start, end in waypoints:
            draw_waypoint(screen, start, end)
        
        # draw endpoint, if any
        if waypoint_endpoint is not None:
            draw_waypoint_endpoint(screen, waypoint_endpoint)
        
        # draw hover preview
        if mode == Mode.GOAL:
            draw_goal(screen, (rx, ry, tile_size, tile_size))
        elif mode == Mode.TILE:
            draw_tile(screen, (rx, ry, tile_size, tile_size))
        elif mode == Mode.SPAWN:
            draw_spawn(screen, (rx, ry))
        elif mode == Mode.WAYPOINT:
            draw_waypoint_endpoint(screen, (rx, ry))
        
        pygame.display.flip()
        
finally:
    pygame.quit()