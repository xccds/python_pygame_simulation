# Schelling's Models of Segregation

import pygame
import random

class Grid:
	def __init__(self, grid_width, grid_height,tile_size):
		self.grid_width = grid_width
		self.grid_height = grid_height
		self.tile_size = tile_size
		self.cell_type = ["empty", "blue","red"]
		self.choice_weight = [0.1,0.45,0.45]
		self.happy_value = 4
		self.reset_cells()
		
	def reset_cells(self):
		self.cells = {}
		for x in range(self.grid_width):
			for y in range(self.grid_height):
				self.cells[(x,y)] = random.choices(self.cell_type, weights=self.choice_weight)[0]

	def position2cell(self, position):
		x, y = position
		return (x // self.tile_size, y // self.tile_size)
	
	def cell2position(self, cell):
		x, y = cell
		return (x * self.tile_size, y * self.tile_size)


	def get_neighbors(self,pos):
		same_num = 0
		x, y = pos
		happy = False
		
		neighbors = {}
		for dx in [-1, 0, 1]:
			if x + dx < 0 or x + dx >= self.grid_width:
				continue
			for dy in [-1, 0, 1]:
				if y + dy < 0 or y + dy >= self.grid_height:
					continue
				if dx == 0 and dy == 0:
					continue

				neighbors[(x + dx, y + dy)] = self.cells[(x + dx, y + dy)]
				if neighbors[(x + dx, y + dy)] == self.cells[pos]:
					same_num += 1
		if same_num >= self.happy_value:
			happy = True

		return neighbors, happy

	def update(self):
	
		for cell in self.cells:
			if self.cells[cell] != "empty":
				neighbors, happy = self.get_neighbors(cell)
				if not happy:
					empty_cells =  [k for k,v in self.cells.items() if v == 'empty' ]
					random_empty_cell = random.choice(empty_cells)
					self.cells[random_empty_cell] = self.cells[cell]
					self.cells[cell] = 'empty'


	def draw(self,screen):
		for cell,color in self.cells.items():
			top_left = self.cell2position(cell)
			if color == "blue":
				pygame.draw.rect(screen, Game.BLUE, (*top_left, self.tile_size, self.tile_size))
			elif color == "red":
				pygame.draw.rect(screen, Game.RED, (*top_left, self.tile_size, self.tile_size))



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
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.pause = not self.pause
				
				if event.key == pygame.K_r:
					self.grid.reset_cells()

	def play(self):

		while self.running:

			self.get_input()
			self.update()
			self.draw()
			
		pygame.quit()

if __name__ == "__main__":
	game = Game(800,800,10)
	game.play()