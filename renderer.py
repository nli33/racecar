from game import Game
import pygame

CAR = (255, 0, 0)
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
    def __init__(self, game: Game):
        self.game = game
        self.size = (game.track.width, game.track.height)
        self.surface = pygame.display.set_mode(self.size)
        self.stopped = False
        pygame.init()
    
    def render(self):
        self.surface.fill(SPACE)
        
        for tile in self.game.track.tiles:
            draw_tile(self.surface, tile.dimensions)
        
        draw_goal(self.surface, self.game.track.goal.dimensions)
        
        # draw car onto car_surf, rotate car_surf, then blit onto main surface
        sf_w, sf_h = 100, 100  # car surface dimensions
        car_surf = pygame.Surface((sf_w, sf_h), pygame.SRCALPHA)
        car_w, car_l = self.game.car.size
        pygame.draw.rect(car_surf, CAR, (sf_w//2 - car_w//2, sf_h//2 - car_l//2, car_w, car_l))
        rotated_surf = pygame.transform.rotate(car_surf, self.game.car.angle + 90)
        rotated_rect = rotated_surf.get_rect(center=self.game.car.center)
        self.surface.blit(rotated_surf, rotated_rect)
        
        pygame.display.flip()
    
    def handle_events(self):
        action = [False, False, False, False]  # accel, steer_left, steer_right, brake
        pressed = pygame.key.get_pressed()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.stopped = True
                return
            
        action[0] = pressed[pygame.K_w]
        action[1] = pressed[pygame.K_a]
        action[2] = pressed[pygame.K_d]
        action[3] = pressed[pygame.K_s]
        
        return action
    
    def close(self):
        pygame.quit()