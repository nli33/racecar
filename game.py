from config import get_config
import math
import numpy as np
import pygame


class Track:
    def __init__(self, config: dict):
        self.width = config.get("width")
        self.height = config.get("height")
        self.diagonal = math.hypot(self.width, self.height)
        self.tiles = [Tile(*t) for t in config.get("tiles", [])]
        self.goal = Tile(*config.get("goal"))

    # check if point is on any tile, or goal
    def on_platform(self, x, y):
        for tile in self.tiles + [self.goal]:
            if tile.contains_point(x, y):
                return True
        return False


class Tile:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
    
    @property
    def dimensions(self):
        return (self.x, self.y, self.w, self.h)

    def contains_point(self, px, py):
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h


# TODO: give less control over steering

# rectangular for now
class Car:
    def __init__(self, spawn, length=20, width=10):
        self.spawn = spawn
        self.length = length
        self.width = width
        self.max_v = 3
        self.accel = 0.05 # accelerator/gas (additive)
        self.decel = 0.01 # friction (additive)
        self.brake_factor = 0.95 # multiple
        self.reset(spawn)

    def reset(self, spawn=None):
        if spawn:
            self.x, self.y = spawn
        else:
            self.x = 0
            self.y = 0
        self.v = 0.0
        self.angle = 90.0    # 0 facing right, ccw
        self.crashed = False
        self.reached_goal = False

    def apply_action(self, action):
        accel, steer_left, steer_right, brake = action
        
        # update speed
        if accel:
            self.v += self.accel
        if brake:
            self.v *= self.brake_factor
        self.v -= self.decel
        self.v = max(0.0, min(self.v, self.max_v))
        
        # update angle
        steer = 0.0
        if steer_left and not steer_right:
            steer = 2
        elif steer_right and not steer_left:
            steer = -2
        self.angle += steer

    # move the car (call once per frame)
    def update(self):
        dx = math.cos(math.radians(-self.angle)) * self.v
        dy = math.sin(math.radians(-self.angle)) * self.v
        self.x += dx
        self.y += dy
    
    @property
    def size(self):
        return self.width, self.length
    
    def rect(self):
        #return pygame.Rect(self.x - self.width//2, self.y - self.length//2, self.width, self.length)
        return pygame.Rect(self.x - self.length//2, self.y - self.width//2, self.width, self.length)

    @property
    def center(self):
        # For collision: use center point
        return self.x, self.y


class Game:
    def __init__(self, config: dict):
        self.track = Track(config)
        self.spawn = config.get("spawn")
        self.car = Car(self.spawn)
        self.step_count = 0
        self.raycast_angles = config.get("raycast_angles")
        if self.raycast_angles is None or len(self.raycast_angles) == 0:
            raise ValueError("No raycast angles given")

    def reset(self):
        self.car.reset(self.spawn)
        self.step_count = 0

    def step(self, action):
        if self.is_done():
            return
        self.car.apply_action(action)
        self.car.update()
        self.step_count += 1
        
        # check car status
        cx, cy = self.car.center
        if not self.track.on_platform(cx, cy):
            self.car.crashed = True
        elif self.track.goal.contains_point(cx, cy):
            self.car.reached_goal = True

    def get_raycasts(self, max_length=None, step_size=1.0):
        cx, cy = self.car.center
        
        if max_length is None:
            max_length = self.track.diagonal
        
        # relative ray angles
        distances = np.zeros(len(self.raycast_angles))
        
        for i, rel in enumerate(self.raycast_angles):
            # yeah idk but this works so
            world_ang = math.radians(-(self.car.angle + rel))
            
            # distances[i] will be 0 if first step is off tiles
            dist = 0.0
            x, y = cx, cy
            
            # step out until we exit the platform or hit max_length
            while dist < max_length and self.track.on_platform(x, y):
                x += math.cos(world_ang) * step_size
                y += math.sin(world_ang) * step_size
                dist += step_size
            
            # last in-bound distance
            distances[i] = dist
        
        return distances

    def is_done(self):
        return self.car.crashed or self.car.reached_goal # or self.step_count >= self.max_steps
