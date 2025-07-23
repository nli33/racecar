from game import Game
import math
import pygame

# color values
CAR = (255, 0, 0)
ALT_CAR = (0, 0, 255)
TILE = (180, 180, 180)
GOAL = (255, 255, 0)
SPACE = (255, 255, 255) # out of bounds color
GRIDLINE = (50, 50, 50)
SPAWN = (255, 0, 0)

'''
Renderer encloses a Game instance
should only be initialized once
'''

def draw_tile(surface: pygame.Surface, dimensions: tuple):
    pygame.draw.rect(surface, TILE, dimensions)

def draw_goal(surface: pygame.Surface, dimensions: tuple):
    pygame.draw.rect(surface, GOAL, dimensions)

def draw_spawn(surface: pygame.Surface, coords: tuple):
    pygame.draw.circle(surface, SPAWN, coords, 5)

class Renderer:
    def __init__(self, game: Game, centered: bool = False):
        self.game = game
        self.size = (game.track.width, game.track.height)
        self.surface = pygame.display.set_mode(self.size)
        self.stopped = False
        self.centered = centered
        self.center = (game.track.width // 2, 3 * game.track.height // 4)
        pygame.init()
        self.clock = pygame.time.Clock()
    
    def render(self):
        self.surface.fill(SPACE)
        
        if self.centered:
            car_x, car_y = self.game.car.center
            center_x = self.surface.get_width() / 2
            center_y = self.surface.get_height() / 2
            angle = math.radians(self.game.car.angle - 90)
            
            def transform(x, y):
                dx = x - car_x
                dy = y - car_y
                x_trans = dx * math.cos(angle) - dy * math.sin(angle) + center_x
                y_trans = dx * math.sin(angle) + dy * math.cos(angle) + center_y
                return x_trans, y_trans
            
            # tiles
            for tile in self.game.track.tiles:
                x, y, w, h = tile.dimensions
                corners = [
                    (x, y),
                    (x + w, y),
                    (x + w, y + h),
                    (x, y + h)
                ]
                transformed_corners = [transform(cx, cy) for cx, cy in corners]
                pygame.draw.polygon(self.surface, (150, 150, 150), transformed_corners)
            
            # goal (rotated)
            goal_x, goal_y, goal_w, goal_h = self.game.track.goal.dimensions
            goal_corners = [
                (goal_x, goal_y),
                (goal_x + goal_w, goal_y),
                (goal_x + goal_w, goal_y + goal_h),
                (goal_x, goal_y + goal_h)
            ]
            transformed_goal_corners = [transform(cx, cy) for cx, cy in goal_corners]
            pygame.draw.polygon(self.surface, (255, 215, 0), transformed_goal_corners)
            
            # draw car at center of screen
            car_w, car_l = self.game.car.size
            car_rect = (center_x - car_w / 2, center_y - car_l / 2, car_w, car_l)
            pygame.draw.rect(self.surface, CAR, car_rect)
        
            if self.game.alt_car:
                # agent_x, agent_y = self.game.alt_car.center
                # alt_w, alt_l = self.game.alt_car.size
                # agent_rect_center = transform(agent_x, agent_y)
                # agent_rect = (agent_rect_center[0] - alt_w / 2, agent_rect_center[1] - alt_l / 2, alt_w, alt_l)
                # pygame.draw.rect(self.surface, ALT_CAR, agent_rect)
                # # Draw alt car with its own rotation
                agent_x, agent_y = self.game.alt_car.center
                alt_w, alt_l = self.game.alt_car.size
                agent_rect_center = transform(agent_x, agent_y)

                # Compute relative angle: how much the alt car is rotated compared to the main car
                rel_angle = self.game.alt_car.angle - self.game.car.angle

                # Draw rotated rectangle for alt car
                alt_surf = pygame.Surface((alt_w, alt_l), pygame.SRCALPHA)
                pygame.draw.rect(alt_surf, ALT_CAR, (0, 0, alt_w, alt_l))
                rotated_alt_surf = pygame.transform.rotate(alt_surf, rel_angle)
                rotated_alt_rect = rotated_alt_surf.get_rect(center=agent_rect_center)
                self.surface.blit(rotated_alt_surf, rotated_alt_rect)
        else:
            # tiles
            for tile in self.game.track.tiles:
                pygame.draw.rect(self.surface, (150, 150, 150), tile.dimensions)
            
            # goal
            pygame.draw.rect(self.surface, (255, 215, 0), self.game.track.goal.dimensions)
            
            # draw car onto car_surf, then transform car_surf
            sf_w, sf_h = 100, 100
            car_surf = pygame.Surface((sf_w, sf_h), pygame.SRCALPHA)
            car_w, car_l = self.game.car.size
            pygame.draw.rect(car_surf, CAR, (sf_w//2 - car_w//2, sf_h//2 - car_l//2, car_w, car_l))
            rotated_surf = pygame.transform.rotate(car_surf, self.game.car.angle + 90)
            rotated_rect = rotated_surf.get_rect(center=self.game.car.center)
            self.surface.blit(rotated_surf, rotated_rect)
            
            if self.game.alt_car:
                alt_surf = pygame.Surface((sf_w, sf_h), pygame.SRCALPHA)
                alt_w, alt_l = self.game.alt_car.size
                pygame.draw.rect(alt_surf, ALT_CAR, (sf_w//2 - alt_w//2, sf_h//2 - alt_l//2, alt_w, alt_l))
                agent_rotated_surf = pygame.transform.rotate(alt_surf, self.game.alt_car.angle + 90)
                agent_rotated_rect = agent_rotated_surf.get_rect(center=self.game.alt_car.center)
                self.surface.blit(agent_rotated_surf, agent_rotated_rect)
        
        pygame.display.flip()
        self.clock.tick(60)
    
    def handle_events(self):
        action = [False, False, False, False]  # accel, steer_left, steer_right, brake
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return
            
            if event.type == pygame.KEYDOWN:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_r]:
                    self.game.reset()
        
        pressed = pygame.key.get_pressed()
            
        action[0] = pressed[pygame.K_w]
        action[1] = pressed[pygame.K_a]
        action[2] = pressed[pygame.K_d]
        action[3] = pressed[pygame.K_s]
        
        return action
    
    def close(self):
        pygame.quit()