import pygame
from tkinter import *
from tkinter import messagebox
from queue import PriorityQueue

PIXELS = 600  # height and width of window
BLOCKS = 50  # number of cells both horizontally and vertically
WIN = pygame.display.set_mode((PIXELS, PIXELS))
pygame.display.set_caption("A* Path Finding Algorithm")
Tk().wm_withdraw()

# defining colors for grid
YELLOW = (255, 255, 0)  # closed
ORANGE = (255, 165, 0)  # open
BLUE = (0, 0, 255)  # construct path
WHITE = (255, 255, 255)  # unscanned spot
BLACK = (0, 0, 0)  # barrier
GREEN = (0, 255, 0)  # start
GREY = (128, 128, 128)  # gap
RED = (255, 0, 0)  # end

# a cell in a grid is called a spot for path finding
class Spot:
    def __init__(self, row, col, pixels):
        self.row = row  # index of row
        self.col = col  # index of column
        self.x = row * pixels  # x pixel coordinate at which spot starts
        self.y = col * pixels  # y pixel coordinate at which spot starts
        self.color = WHITE
        self.neighbors = []
        self.pixels = pixels  # size of the spot

    def make_start(self):
        self.color = GREEN

    def is_start(self):
        return self.color == GREEN

    def make_end(self):
        self.color = RED

    def is_end(self):
        return self.color == RED
    
    def make_closed(self):
        self.color = YELLOW

    def is_closed(self):
        return self.color == YELLOW

    def make_open(self):
        self.color = ORANGE

    def is_open(self):
        return self.color == ORANGE

    def is_barrier(self):
        return self.color == BLACK

    def make_barrier(self):
        self.color = BLACK

    def make_path(self):
        self.color = BLUE

    def reset(self):
        self.color = WHITE

    def get_pos(self):
        return self.row, self.col

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.pixels, self.pixels))

    def update_neighbors(self, grid):
        self.neighbors = []

        if self.row > 0 and not grid[self.row-1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row-1][self.col])

        if self.col < BLOCKS-1 and not grid[self.row][self.col+1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col+1])

        if self.row < BLOCKS-1 and not grid[self.row+1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row+1][self.col])

        if self.col > 0 and not grid[self.row][self.col-1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col-1])


# heuristic function to calculate h score
# I've used Manhattan distance
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


# construct path if found
def construct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


# implementation of A* shortest path algorithm
def shortest_path(draw, grid, start, end):
    count = 0  # count is need to make priority queue work
    visited = PriorityQueue()
    visited.put((0, count, start))
    came_from = {}
    g_score = {spot: float('inf') for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float('inf') for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos()) + g_score[start]

    visited_hash = {start}

    while not visited.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = visited.get()[2]
        visited_hash.remove(current)

        if current == end:
            construct_path(came_from, end, draw)
            end.make_end()
            start.make_start()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current]+1
            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in visited_hash:
                    count += 1
                    visited.put((f_score[neighbor], count, neighbor))
                    visited_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


# defining the grid 
def make_grid():
    grid = []
    gap = PIXELS // BLOCKS
    for i in range(BLOCKS):
        grid.append([])
        for j in range(BLOCKS):
            spot = Spot(i, j, gap)
            grid[i].append(spot)
    return grid


# drawing the lines on the grid
def draw_grid_lines(win):
    gap = PIXELS//BLOCKS
    for i in range(BLOCKS):
        pygame.draw.line(win, GREY, (0, i*gap), (PIXELS, i*gap))
        for j in range(BLOCKS):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, PIXELS))


# drawing the entire grid 
def draw(win, grid):
    win.fill(WHITE)
    for row in grid:
        for spot in row:
            spot.draw(win)
    draw_grid_lines(win)
    pygame.display.update()


# get the pixel coordinate of the mouse click
def get_clicked_pos(pos):
    gap = PIXELS // BLOCKS
    y, x = pos
    row = y // gap
    col = x // gap
    return row, col


# main function to run the program 
def main(win):
    grid = make_grid()

    start = False
    end = False

    run = True
    started = False

    while run:
        draw(win, grid)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            # left click event
            if pygame.mouse.get_pressed(3)[0] and not started:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()
                elif not end and spot != start:
                    end = spot
                    end.make_end()
                elif spot != end and spot != start:
                    spot.make_barrier()

            #right click event
            elif pygame.mouse.get_pressed(3)[2] and not started:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            # start the algorithm
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end and not started:
                    started = True
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)
                    found_flag = shortest_path(lambda: draw(win, grid), grid, start, end)
                    if found_flag:
                        draw(win, grid)
                        messagebox.showinfo('Success', 'Path found !!')
                    else:
                        draw(win, grid)
                        messagebox.showinfo('Failure', 'Path not found !!')

                # reset the grid
                if event.key == pygame.K_r:
                    start = None
                    end = None
                    started = False
                    grid = make_grid()
    pygame.quit()


# run the program
if __name__ == '__main__':
    main(WIN)
