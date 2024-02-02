# Solar system simulation

import pygame
import math

class Planet:

	def __init__(self, x, y, x_vel, y_vel, color, is_sun, mass, radius):
		self.x = x
		self.y = y
		self.mass = mass
		self.radius = radius
		self.x_vel = x_vel
		self.y_vel = y_vel
		self.orbit = []
		self.is_sun = is_sun
		self.color = color
		self.check()
	
	def check(self):
		if self.is_sun:
			self.image = pygame.transform.scale(pygame.image.load("Planet.png"), (self.radius * 2, self.radius * 2))
			self.rect = self.image.get_rect()
			
	@staticmethod
	def attraction(object1, object2):
		distance_x = object2.x - object1.x
		distance_y = object2.y - object1.y
		distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

		force = Game.G * object1.mass * object2.mass / distance**2
		theta = math.atan2(distance_y, distance_x)
		force_x = math.cos(theta) * force
		force_y = math.sin(theta) * force
		return force_x, force_y

	def move(self, planets):
		total_force_x = total_force_y = 0
		for planet in planets:
			if self == planet:
				continue

			force_x, force_y = Planet.attraction(self,planet)
			total_force_x += force_x
			total_force_y += force_y

		acceleration_x = total_force_x / self.mass 
		acceleration_y = total_force_y / self.mass 
		self.x_vel += acceleration_x * Game.TIMESTEP
		self.y_vel += acceleration_y * Game.TIMESTEP

		self.x += self.x_vel * Game.TIMESTEP
		self.y += self.y_vel * Game.TIMESTEP
		self.orbit.append((self.x, self.y))

	
	def draw(self,game):
		x = self.x * Game.SCALE + game.Width / 2
		y = self.y * Game.SCALE + game.Height / 2

		if self.is_sun:
			self.rect.center = (x, y)
			game.screen.blit(self.image,self.rect)
		else:
			pygame.draw.circle(game.screen, self.color, (x, y), self.radius)

		if len(self.orbit) > 2:
			updated_points = []
			for point in self.orbit:
				x, y = point
				x = x * Game.SCALE + game.Width / 2
				y = y * Game.SCALE + game.Height / 2
				updated_points.append((x, y))

			pygame.draw.lines(game.screen, self.color, False, updated_points, 2)

		

class Spacecraft:

	ORBIT_DIST = 7000*1000
	INIT_SPEED = 42*1000

	def __init__(self, x, y, direction_x, direction_y, mass=100000,size = 20):
		self.x = x + direction_x * self.ORBIT_DIST
		self.y = y + direction_y * self.ORBIT_DIST
		self.x_vel = direction_x * self.INIT_SPEED
		self.y_vel = direction_y * self.INIT_SPEED 
		self.mass = mass
		self.image =  pygame.transform.scale(pygame.image.load("ship.png"), (size, size))
		self.image_orig = self.image.copy()
		self.rect = self.image.get_rect()
		self.off_screen = False
		self.collided = False
		self.speed = self.INIT_SPEED
		self.text = f"speed:{round(self.speed/1000,2)}"
		self.info = Info(self.text)

	def move(self, game):
		total_force_x = total_force_y = 0
		for planet in game.planets:
			force_x, force_y = Planet.attraction(self,planet)
			total_force_x += force_x
			total_force_y += force_y

		acceleration_x = total_force_x / self.mass 
		acceleration_y = total_force_y / self.mass 
		self.x_vel += acceleration_x * Game.TIMESTEP
		self.y_vel += acceleration_y * Game.TIMESTEP

		self.x += self.x_vel * Game.TIMESTEP
		self.y += self.y_vel * Game.TIMESTEP

		fly_angle = math.atan2(self.x_vel, self.y_vel)
		fly_angle = 180+math.degrees(fly_angle)
		self.speed = math.sqrt(self.x_vel**2 + self.y_vel ** 2)
		self.image = pygame.transform.rotate(self.image_orig, fly_angle)

		self.text = f"speed:{round(self.speed/1000,2)}"
		
	
	def draw(self,game):
		x = self.x * Game.SCALE + game.Width / 2
		y = self.y * Game.SCALE + game.Height / 2

		self.rect.center = (x, y)
		game.screen.blit(self.image,self.rect) 
		self.info.update(self.text, (x,y-20))
		self.info.draw(game.screen)

class Info:

	def __init__(self,text,size=28):
		self.font = pygame.font.Font(None, size)
		self.text = self.font.render(text, True, Game.WHITE)
		self.rect = self.text.get_rect()

	def update(self, text, position):
		self.text = self.font.render(text, True, Game.WHITE)
		self.rect.center = position

	def draw(self, screen):
		screen.blit(self.text , self.rect)
		

class Game:
	AU = 149.6e6 * 1000
	G = 6.67428e-11
	SCALE = 250 / AU  # 1AU = 100 pixels
	TIMESTEP = 3600*12 # 0.5 day

	WHITE = (255, 255, 255)
	YELLOW = (255, 255, 0)
	BLUE = (100, 149, 237)
	RED = (188, 39, 50)
	DARK_GREY = (80, 78, 81)

	def __init__(self, Width=1000, Height=1000):
		pygame.init()
		self.Width = Width
		self.Height = Height
		self.screen = pygame.display.set_mode((Width, Height))
		pygame.display.set_caption("solar system")
		self.FPS = 60
		self.BG = pygame.transform.scale(pygame.image.load("BG.png"), (Width, Height))
		self.ships = []
		self.running = True
		self.clock = pygame.time.Clock()
		self.click_count = 0
		self.first_pos = None
		self.mouse_pos = None
		self.setup_planets()

	def setup_planets(self):
		sun = Planet(x=0, y=0, x_vel=0, y_vel=0, color = Game.YELLOW, 
			   is_sun = True, radius = 30, mass = 1.98892 * 10**30)
		earth = Planet(x=-1 * Game.AU,y = 0, x_vel=0, y_vel=29.783 * 1000, color = Game.BLUE, 
				 is_sun = False, radius = 16, mass = 5.9742 * 10**24)
		mars = Planet(x=-1.524 * Game.AU,y = 0, x_vel=0, y_vel=24.077 * 1000, color = Game.RED,
				 is_sun = False, radius = 12, mass = 6.39 * 10**23)
		mercury = Planet(x=0.387 * Game.AU,y = 0, x_vel=0, y_vel=-47.4 * 1000, color = Game.DARK_GREY,
				 is_sun = False, radius = 8, mass = 3.30 * 10**23)
		venus = Planet(x=0.723 * Game.AU,y = 0, x_vel=0, y_vel=-35.02 * 1000, color = Game.WHITE,
				 is_sun = False, radius = 14, mass = 4.8685 * 10**24)

		self.planets = [sun, earth, mars, mercury, venus]


	def create_ship(self, location, mouse_loc):
		direction = (pygame.math.Vector2(mouse_loc)- pygame.math.Vector2(location)).normalize()
		direction_x, direction_y = direction
		pos_x = self.planets[1].x
		pos_y = self.planets[1].y

		ship = Spacecraft(pos_x, pos_y,direction_x,direction_y)
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
		for planet in self.planets:
			planet.draw(self)
		if self.click_count == 1:
			pygame.draw.line(self.screen, self.WHITE, self.first_pos,self.mouse_pos)
		
		for ship in self.ships:
			ship.draw(self)

		pygame.display.update()


	def update(self):
		for planet in self.planets:
			planet.move(self.planets)

		for ship in self.ships:
			ship.move(self)


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