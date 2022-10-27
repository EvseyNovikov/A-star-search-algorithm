import pygame
import math
from queue import PriorityQueue

app_widow_width = 800
app_window = pygame.display.set_mode((app_widow_width, app_widow_width))
pygame.display.set_caption("A* Path Finding Algorithm")

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))



    def update_neighbors(self, grid): # находим и сохраняем в массив всех соседей всех вершин графа (клеток)
        self.neighbors = []

        if self.row < (self.total_rows - 1) and not grid[self.row + 1][self.col].is_barrier():  # Нижняя клетка
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # Верхняя клетка
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < (self.total_rows - 1) and not grid[self.row][self.col + 1].is_barrier():  # Правая клетка
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # Левая клетка
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(p1, p2):  #ф-ия для нахождения кратчайщего пути между начальной и конечной вершиной
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current):
    while current in came_from: #проходимся по словарю от конечного элемента до первого (исключая его).

        #пример: {B: A C: B, D: C, E: D, F: E}
        # метод берёт последний элемент F, после чего текущим становится E, далее вызывается метод E.make_path().
        #Цикл while повторяет данную операцию до тех пор, пока не дойдёт до ключа B, где в current запишется объект A, к-го в данном словаре нет.
        #Цикл прекращает свою работу

        current = came_from[current]
        current.make_path()


def algorithm(draw, grid, start, end):
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[1]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end)
            end.make_end()
            return True

        for neighbor in current.neighbors:

            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:

                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score

                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())

                if neighbor not in open_set_hash:
                    open_set.put((f_score[neighbor], neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(total_row, width): # заполнение массива клеток (вершин)
    grid = []
    spot_size = width // total_row

    for i in range(total_row):
        grid.append([])
        for j in range(total_row):
            spot = Spot(i, j, spot_size, total_row)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width): #метод для рисования сетки (не клеток)
    spot_size = width // rows

    for i in range(rows): # рисование горизонтальных линий
        pygame.draw.line(win, GREY, (0, i * spot_size), (width, i * spot_size))

        for j in range(rows): # рисование вертикальных линий
            pygame.draw.line(win, GREY, (j * spot_size, 0), (j * spot_size, width))


def draw(win, grid, rows, width): # отрисовка клеток на экране
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_pos(pos, rows, width): # метод для определения вершины (клетки), на который нажал пользователь
    spot_size = width // rows
    y, x = pos

    row = y // spot_size
    col = x // spot_size

    return row, col


def main(win, width):
    rows = 50
    grid = make_grid(rows, width)

    start = None
    end = None

    run = True
    while run:
        draw(win, grid, rows, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # отслеживание левого клика мыши
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]

                if not start:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # отслеживание правого клика мыши
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, rows, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end: # при нажатии на пробел начинается расчёт пути (вызов algorithm)
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid) # находим и сохраняем всех соседей всех вершин графа (клеток)

                    algorithm(lambda: draw(win, grid, rows, width), grid, start, end)

                if event.key == pygame.K_c: # очистка grid-а
                    start = None
                    end = None
                    grid = make_grid(rows, width)

    pygame.quit()


main(app_window, app_widow_width)
