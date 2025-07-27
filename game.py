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


class Waypoint:
    """
    A waypoint defined by a line segment between two endpoints.
    They should guide the car towards the goal.
    Note: the code using the Game class is responsible for calling the Game.check_waypoints() method,
        it is not called by default. (ex: within RacecarEnv or play.py)
    """
    
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    
    @classmethod
    def from_endpoints(cls, start: tuple, end: tuple):
        return cls(start[0], start[1], end[0], end[1])

    @property
    def start(self):
        return self.x1, self.y1

    @property
    def end(self):
        return self.x2, self.y2
    
    def intersects_car(self, car: Car):
        cx, cy = car.center
        w, l = car.size
        angle_rad = math.radians(-car.angle)
        
        hw, hl = w/2, l/2
        # Compute corners relative to center, then rotate and translate
        corners = []
        for dx, dy in [(-hw, -hl), (hw, -hl), (hw, hl), (-hw, hl)]:
            # Rotate
            rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
            ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
            # Translate
            corners.append((cx + rx, cy + ry))

        # Car edges as line segments
        car_edges = [
            (corners[i], corners[(i + 1) % 4]) for i in range(4)
        ]

        # Waypoint as line segment
        seg1 = ((self.x1, self.y1), (self.x2, self.y2))

        # Check intersection with each car edge
        for edge in car_edges:
            if Waypoint.segments_intersect(seg1[0], seg1[1], edge[0], edge[1]):
                return True
        return False

    # returns true if line segments p1-p2 and q1-q2 intersect
    @staticmethod
    def segments_intersect(p1, p2, q1, q2):
        def ccw(a, b, c):
            return (c[1]-a[1]) * (b[0]-a[0]) > (b[1]-a[1]) * (c[0]-a[0])
        return (ccw(p1, q1, q2) != ccw(p2, q1, q2)) and (ccw(p1, p2, q1) != ccw(p1, p2, q2))


class Game:
    def __init__(self, config: dict, has_alt_car=False):
        self.track = Track(config)
        self.spawn = config.get("spawn")
        self.car = Car(self.spawn)
        if has_alt_car:
            self.alt_car = Car(self.spawn)
            self.alt_car_active = True
        else:
            self.alt_car = None
        self.first_step = None
        self.step_count = 0
        self.raycast_angles = config.get("raycast_angles")
        if self.raycast_angles is None or len(self.raycast_angles) == 0:
            raise ValueError("No raycast angles given")
        # true if active
        self.waypoints = {Waypoint.from_endpoints(*t): True for t in config.get("waypoints", [])}


    def reset(self):
        self.car.reset(self.spawn)
        self.alt_car.reset(self.spawn) if self.alt_car else None
        self.first_step = None
        self.step_count = 0
        self.alt_car_active = True
        for waypoint in self.waypoints:
            self.waypoints[waypoint] = True


    def step(self, action, alt_car_action=None):
        # record first action time
        if self.first_step is None and any(action):
            self.first_step = self.step_count
        
        # print total time elapsed
        if self.is_done():
            print(self.step_count - self.first_step)
            return
        
        self.car.apply_action(action)
        self.car.update()
        if self.alt_car and alt_car_action.any() and self.alt_car_active:
            self.alt_car.apply_action(alt_car_action)
            self.alt_car.update()
        self.step_count += 1
        
        # check car status
        cx, cy = self.car.center
        if not self.track.on_platform(cx, cy):
            self.car.crashed = True
        elif self.track.goal.contains_point(cx, cy):
            self.car.reached_goal = True
        
        # check alt car status
        if self.alt_car and self.alt_car_active:
            acx, acy = self.alt_car.center
            if not self.track.on_platform(acx, acy) or self.track.goal.contains_point(acx, acy):
                self.alt_car_active = False


    def get_raycasts(self, max_length=None, step_size=1.0, alt_car=False):
        if alt_car:
            car = self.alt_car
        else:
            car = self.car
        cx, cy = car.center
        
        if max_length is None:
            max_length = self.track.diagonal
        
        # relative ray angles
        distances = np.zeros(len(self.raycast_angles))
        
        for i, rel in enumerate(self.raycast_angles):
            # yeah idk but this works so
            world_ang = math.radians(-(car.angle + rel))
            
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


    def check_waypoints(self):
        count = 0
        for waypoint, active in self.waypoints.items():
            if not active: 
                continue
            if waypoint.intersects_car(self.car):
                self.waypoints[waypoint] = False
                count += 1
        return count