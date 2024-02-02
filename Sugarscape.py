# Sugarscape model

import pygame
import random
import numpy as np
from util import plot_hist

class Cell:

	def __init__(self,pos,init_sugar):
		self.x,self.y = pos
		self.capacity = init_sugar
		self.sugar = init_sugar
		self.occupied = False

	def grow(self):
		if self.sugar < self.capacity:
			self.sugar += 1

class Agent:
	Color = (188, 39, 50)
	def __init__(self,x,y,tile_size):
		self.x = x
		self.y = y
		self.tile_size = tile_size
		self.reset()

	def reset(self):
		self.sugar = random.randrange(5,25)
		self.metabolism = random.randrange(1,4)
		self.vision = random.randrange(1,6)
		self.neighbors = {}
		self.target = None
		self.died = False
		self.life = random.randrange(60,100)

	#  agent surveys k cells in each of the 4 compass directions, where k isthe range of the agent’s vision
	def survey(self,grid):
		self.neighbors.clear()
		dx_list = [-i for i in range(1,self.vision+1)]+[i for i in range(1,self.vision+1)]
		
		for dx in dx_list:
			if self.x + dx < 0 or self.x + dx >=grid.grid_width:
				continue
			self.neighbors[(self.x + dx, self.y)] = {'sugar': grid.cells[self.x + dx, self.y].sugar, 
													'occupied': grid.cells[self.x + dx, self.y].occupied,
													'distance': abs(dx)} 

		for dy in dx_list:
			if self.y + dy < 0 or self.y + dy >=grid.grid_height:
				continue
			self.neighbors[(self.x, self.y + dy)] = {'sugar': grid.cells[self.x, self.y + dy].sugar,
													'occupied': grid.cells[self.x, self.y + dy].occupied,
													'distance': abs(dy)}



	
	#  chooses the unoccupied cell with the most sugar. In case of a tie,it chooses the closer cell; among cells at the same distance, it chooses randomly.
	def choose(self,grid):
		self.survey(grid)
		candidates = {k:v for (k,v) in self.neighbors.items() if not v['occupied']}
		if len(candidates) > 0:
			max_sugar = max([v['sugar'] for v in candidates.values()])

			candidates = {k:v for (k,v) in  candidates.items() if v['sugar'] == max_sugar}
			min_dist = min([v['distance'] for v in candidates.values()])

			candidates = [k for (k,v) in  candidates.items() if v['distance'] == min_dist]
			self.target = random.choice(candidates)
		else:
			self.target = (self.x,self.y)

	# moves to the selected cell and harvests the sugar, adding the harvest to its accumulated wealth and leaving the cell empty
	def move(self,grid):
		grid.cells[(self.x, self.y)].occupied = False
		self.x, self.y = self.target
		self.sugar += grid.cells[self.target].sugar
		grid.cells[self.target].sugar = 0
		grid.cells[self.target].occupied = True

	def consume(self,grid):
		self.sugar -= self.metabolism
		self.life -= 1
		if self.sugar <= 0 or self.life <= 0:
			self.died = True
			grid.cells[(self.x, self.y)].occupied = False

	def update(self, grid):
		self.choose(grid)
		self.move(grid)
		self.consume(grid)

	def draw(self,screen):
		radius = self.tile_size//2
		pygame.draw.circle(screen, self.Color, center = (self.x*self.tile_size+radius, self.y*self.tile_size+radius),radius= radius)



class Grid:
	Color = [(255,255,214),(254,227,153),(254,203,123),(253,176,104)]
	def __init__(self, grid_width, grid_height,tile_size):
		self.grid_width = grid_width
		self.grid_height = grid_height
		self.tile_size = tile_size
		self.cells = {}
		self.reset_cells()

	def reset_cells(self):
		center1 = [self.grid_width//4, self.grid_height//4]
		center2 = [self.grid_width * 3//4, self.grid_height *3//4]
		self.cells = {}
		for x in range(self.grid_width):
			for y in range(self.grid_height):
				if (self.distance((x,y), center1) < 5 or 
					self.distance((x,y), center2) < 5):
					self.cells[(x,y)] = Cell((x,y),3)
				elif (self.distance((x,y), center1) < 10 or 
					self.distance((x,y), center2) < 10):
					self.cells[(x,y)] = Cell((x,y),2)
				elif (self.distance((x,y), center1) < 15 or 
					self.distance((x,y), center2) < 15):
					self.cells[(x,y)] = Cell((x,y),1)
				else:
					self.cells[(x,y)] = Cell((x,y),0)

	@staticmethod
	def distance(pos1, pos2):
		x1, y1 = pos1
		x2, y2 = pos2
		return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


	def position2cell(self, position):
		x, y = position
		return (x // self.tile_size, y // self.tile_size)
	
	def cell2position(self, cell):
		x, y = cell
		return (x * self.tile_size, y * self.tile_size)

	def draw(self, screen):
		for cell in self.cells:
			x, y = self.cell2position(cell)
			pygame.draw.rect(screen, self.Color[self.cells[cell].sugar], (x, y, self.tile_size, self.tile_size))

class Game:
	DARK_GREY = (80, 78, 81)
	def __init__(self, Width=800, Height=800,Tile_size = 10) :
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
		self.step = 0
		self.reset_agents()

	def reset_agents(self,num=300):
		self.agents = []
		self.pos = set([(random.randrange(0, self.Width//self.Tile_size), random.randrange(0, self.Height//self.Tile_size)) 
							for _ in range(num)])
		for x,y in self.pos:
			self.agents.append(Agent(x,y,self.Tile_size))
			self.grid.cells[(x,y)].occupied = True

	def update(self):
		if not self.pause:
			self.time_passed += self.clock.tick(self.FPS)
			if self.time_passed > self.update_freq:
				self.time_passed = 0
				self.step += 1

				random.shuffle(self.agents)
				for agent in self.agents:
					agent.update(self.grid)
					if agent.died:
						agent.x, agent.y = random.choice([cell for cell in self.grid.cells 
									   			if self.grid.cells[cell].occupied==False])
						agent.reset()
						#self.agents.remove(agent)
				
				for cell in self.grid.cells:
					self.grid.cells[cell].grow()
				sugar_arr = np.array([agent.sugar for agent in self.agents])
				max_value = sugar_arr.max()
				min_value = sugar_arr.min()
				per_25 = np.percentile(sugar_arr, 25)
				per_50 = np.percentile(sugar_arr, 50)
				per_75 = np.percentile(sugar_arr, 75)
				plot_hist(sugar_arr)
				print(f"Step:{self.step} Pop_size:{len(sugar_arr)}\nmin:{min_value}  p25:{per_25}  p50:{per_50}  p75:{per_75}  max:{max_value}")


	def draw(self):
		self.screen.fill(Game.DARK_GREY)
		self.grid.draw(self.screen)
		for agent in self.agents:
			agent.draw(self.screen)
		# for col in range(self.grid.grid_width):
		# 	pygame.draw.line(self.screen, Game.DARK_GREY, (col * self.Tile_size, 0), (col * self.Tile_size, self.Height))
		# for row in range(self.grid.grid_height):
		# 	pygame.draw.line(self.screen, Game.DARK_GREY, (0,row * self.Tile_size), (self.Width,row * self.Tile_size))
		
		pygame.display.update()

	def get_input(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
			
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.pause = not self.pause
				
				if event.key == pygame.K_c:
					self.pause = True
				
				if event.key == pygame.K_r:
					self.step = 0
					self.grid.reset_cells()
					self.reset_agents()

	def play(self):

		while self.running:

			self.get_input()
			self.update()
			self.draw()
			
		pygame.quit()

if __name__ == "__main__":
	game = Game(800,800,10)
	game.play()