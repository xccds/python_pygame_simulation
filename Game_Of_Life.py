# cowways game of life

import pygame
import random

class Grid:
	def __init__(self, grid_width, grid_height,tile_size):
		self.grid_width = grid_width
		self.grid_height = grid_height
		self.tile_size = tile_size
		self.cells = set()

	def position2cell(self, position):
		x, y = position
		return (x // self.tile_size, y // self.tile_size)
	
	def cell2position(self, cell):
		x, y = cell
		return (x * self.tile_size, y * self.tile_size)

	def clear(self):
		self.cells.clear()

	def reset(self,num=random.randrange(4, 10)):
		self.cells = set([(random.randrange(0, self.grid_height), random.randrange(0, self.grid_width)) 
							for _ in range(num*self.grid_width)])

	def add_or_remove(self,position):
		cell = self.position2cell(position)
		if cell in self.cells:
			self.cells.remove(cell)
		else:
			self.cells.add(cell)


	def get_neighbors(self,pos):
		x, y = pos
		neighbors = []
		for dx in [-1, 0, 1]:
			if x + dx < 0 or x + dx >= self.grid_width:
				continue
			for dy in [-1, 0, 1]:
				if y + dy < 0 or y + dy >= self.grid_height:
					continue
				if dx == 0 and dy == 0:
					continue

				neighbors.append((x + dx, y + dy))
		
		return neighbors

	def update(self):
		all_neighbors = set()
		new_cells = set()

		for cell in self.cells:
			neighbors = self.get_neighbors(cell)
			all_neighbors.update(neighbors)

			neighbors = [neighbor for neighbor in neighbors if neighbor in self.cells]

			if len(neighbors) in [2, 3]:
				new_cells.add(cell)
		
		for cell in all_neighbors:
			neighbors = self.get_neighbors(cell)
			neighbors = [neighbor for neighbor in neighbors if neighbor in self.cells]

			if len(neighbors) == 3:
				new_cells.add(cell)
		
		self.cells = new_cells

	def draw(self,screen):
		for cell in self.cells:
			top_left = self.cell2position(cell)
			pygame.draw.rect(screen, Game.BLUE, (*top_left, self.tile_size, self.tile_size))


class Game:

	WHITE = (255, 255, 255)
	YELLOW = (255, 255, 0)
	BLUE = (100, 149, 237)
	RED = (188, 39, 50)
	BLACK = (0, 0, 0)
	DARK_GREY = (80, 78, 81)

	def __init__(self, Width=800, Height=800,Tile_size = 20):
		pygame.init()
		self.Width = Width
		self.Height = Height
		self.Tile_size = Tile_size
		self.screen = pygame.display.set_mode((Width, Height))
		self.clock = pygame.time.Clock()
		self.grid = Grid(Width//Tile_size, Height//Tile_size, Tile_size)
		self.update_freq = 500
		self.time_passed = 0
		self.running = True
		self.pause = True
		self.FPS = 60

	def draw(self):
		self.screen.fill(Game.DARK_GREY)
		self.grid.draw(self.screen)
		for row in range(self.grid.grid_height):
			pygame.draw.line(self.screen, self.BLACK, (0, row * self.Tile_size), (self.Width, row * self.Tile_size))
		for col in range(self.grid.grid_width):
			pygame.draw.line(self.screen, self.BLACK, (col * self.Tile_size, 0), (col * self.Tile_size, self.Height))
		
		pygame.display.update()

	def update(self):
		if not self.pause:
			self.time_passed += self.clock.tick(self.FPS)
			if self.time_passed > self.update_freq:
				self.time_passed = 0
				self.grid.update()

	def get_input(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				self.grid.add_or_remove(pos)
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.pause = not self.pause
				
				if event.key == pygame.K_c:
					self.grid.clear()
					self.pause = True
				
				if event.key == pygame.K_r:
					self.grid.reset()

	def play(self):

		while self.running:

			self.get_input()
			self.update()
			self.draw()
			
		pygame.quit()

if __name__ == "__main__":
	game = Game(800,800,20)
	game.play()