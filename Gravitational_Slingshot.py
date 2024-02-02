# gravitational slingshot effect

import pygame
import math

class Planet:
    def __init__(self, x, y, mass=100,radius=50):
        self.x = x
        self.y = y
        self.mass = mass
        self.image = pygame.transform.scale(pygame.image.load("Planet.png"), (radius * 2, radius * 2))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.radius = radius
        self.speed = -1
        self.off_screen = False

    def move(self):
        self.rect.centerx += self.speed
        self.x = self.rect.centerx
        self.y = self.rect.centery

        if self.rect.top > game.Height or self.rect.bottom < 0 or self.rect.left > game.Width or self.rect.right < 0:
            self.off_screen = True


    def reset(self,x,y):
        self.x = x
        self.y = y
        self.rect.center = (self.x, self.y)
        self.off_screen = False
    
    def draw(self,screen):
        screen.blit(self.image,self.rect)

class Spacecraft:
    def __init__(self, x, y, vel_x, vel_y, mass=5,size = 20,G = 5):
        self.x = x
        self.y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.mass = mass
        self.G = G
        self.image =  pygame.transform.scale(pygame.image.load("ship.png"), (size, size))
        self.image_orig = self.image.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.off_screen = False
        self.collided = False
        self.speed = math.sqrt(self.vel_x**2 + self.vel_y ** 2)
        self.text = f"speed:{round(self.speed,2)}"
        self.info = Info(self.text, [self.x,self.y-20])

    def move(self, game):
        distance = math.sqrt((self.x - game.planet.x)**2 + (self.y - game.planet.y)**2)
        force = (self.G * self.mass * game.planet.mass) / distance ** 2
        
        acceleration = force / self.mass
        angle = math.atan2(game.planet.y - self.y, game.planet.x - self.x)

        acceleration_x = acceleration * math.cos(angle)
        acceleration_y = acceleration * math.sin(angle)

        self.vel_x += acceleration_x
        self.vel_y += acceleration_y

        fly_angle = math.atan2(self.vel_y, self.vel_x)
        fly_angle = 270 - math.degrees(fly_angle)
        self.speed = math.sqrt(self.vel_x**2 + self.vel_y ** 2)
        self.image = pygame.transform.rotate(self.image_orig, fly_angle)

        self.x += self.vel_x
        self.y += self.vel_y

        self.rect.centerx = self.x
        self.rect.centery = self.y

        self.text = f"speed:{round(self.speed,2)}"
        self.info.update(self.text, [self.x,self.y-20])


        if self.rect.top > game.Height or self.rect.bottom < 0 or self.rect.left > game.Width or self.rect.right < 0:
            self.off_screen = True

        if math.sqrt((self.x - game.planet.x)**2 + (self.y - game.planet.y)**2) <= game.planet.radius:
            self.collided = True

    
    def draw(self,screen):
        screen.blit(self.image,self.rect) 
        self.info.draw(screen)

class Info:

    def __init__(self,text,position,size=28):
        self.font = pygame.font.Font(None, size)
        self.text = self.font.render(text, True, Game.WHITE)
        self.rect = self.text.get_rect()
        self.rect.center = position

    def update(self, text, position):
        self.text = self.font.render(text, True, Game.WHITE)
        self.rect.center = position

    def draw(self, screen):
        screen.blit(self.text , self.rect)
        

class Game:

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)

    def __init__(self, Width=800, Height=600):
        pygame.init()
        self.Width = Width
        self.Height = Height
        self.screen = pygame.display.set_mode((Width, Height))
        pygame.display.set_caption("Gravitational Slingshot Effect")
        self.SHIP_MASS = 5
        self.FPS = 60
        self.BG = pygame.transform.scale(pygame.image.load("BG.png"), (Width, Height))
        self.ships = []
        self.running = True
        self.clock = pygame.time.Clock()
        self.planet = Planet(Width, Height // 2)
        self.click_count = 0
        self.first_pos = None
        self.mouse_pos = None


    def create_ship(self, location, mouse_loc):
        t_x, t_y = location
        m_x, m_y = mouse_loc
        vel_x = (m_x - t_x) / 100
        vel_y = (m_y - t_y) / 100
        ship = Spacecraft(t_x, t_y, vel_x, vel_y)
        self.ships.append(ship)


    def get_input(self):
        self.mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.click_count += 1
                if self.click_count > 2:
                    self.click_count = 1
                if self.click_count == 1:
                    self.first_pos = self.mouse_pos
                if self.click_count == 2:
                    self.create_ship(self.first_pos, self.mouse_pos)
                    

    def draw(self):
        self.screen.blit(self.BG,(0,0))
        self.planet.draw(self.screen)
        if self.click_count == 1:
            pygame.draw.line(self.screen, self.WHITE, self.first_pos,self.mouse_pos)
        
        for ship in self.ships:
            ship.draw(self.screen)

        pygame.display.update()


    def update(self):
        self.planet.move()
        if self.planet.off_screen:
            self.planet.reset(self.Width, self.Height // 2)

        for ship in self.ships:
            ship.move(self)
            if ship.off_screen or ship.collided:
                self.ships.remove(ship)


    def play(self):

        while self.running:
            self.clock.tick(self.FPS)

            self.get_input()
            self.update()
            self.draw()
        
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.play()