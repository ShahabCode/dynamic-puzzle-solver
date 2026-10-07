import random

import pygame


class Node:
    def __init__(self, state, parent=None, action=None, cost=0, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = depth

    def get_path(self):
        path = []
        current = self
        while current is not None:
            if current.action is not None:
                path.append(current.action)
            current = current.parent
        path.reverse()
        return path


class Puzzle:
    def __init__(self, size):
        self.size = size
        self.board = [
            list(range(row * size + 1, row * size + size + 1))
            for row in range(size)
        ]
        self.board[-1][-1] = 0

        self.goal_state = tuple(
            tile
            for row in self.board
            for tile in row
        )


    def find_empty(self):
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:
                    return row, col


    def move(self, direction):
        row, col = self.find_empty()

        if direction == "up":
            new_row, new_col = row - 1, col
        elif direction == "down":
            new_row, new_col = row + 1, col
        elif direction == "left":
            new_row, new_col = row, col - 1
        elif direction == "right":
            new_row, new_col = row, col + 1
        else:
            return False

        if not (0 <= new_row < self.size and 0 <= new_col < self.size):
            return False

        self.board[row][col], self.board[new_row][new_col] = \
            self.board[new_row][new_col], self.board[row][col]
        return True


    def shuffle(self, moves=100):
        directions = ["up", "down", "left", "right"]

        for _ in range(moves):
            direction = random.choice(directions)
            self.move(direction)


    def get_state(self):
        return tuple(
            tile
            for row in self.board
            for tile in row
        )


    def get_possible_moves(self):
        row, col = self.find_empty()
        moves = []

        if row > 0:
            moves.append("up")

        if row < self.size - 1:
            moves.append("down")

        if col > 0:
            moves.append("left")

        if col < self.size - 1:
            moves.append("right")

        return moves


    def from_state(self, state):
        puzzle = Puzzle(self.size)

        puzzle.board = [
            list(state[row * self.size:(row + 1) * self.size])
            for row in range(self.size)
        ]
        return puzzle


    def get_neighbors(self):
        neighbors = []

        for direction in self.get_possible_moves():
            new_puzzle = self.from_state(self.get_state())
            new_puzzle.move(direction)
            neighbors.append(new_puzzle.get_state())
        return neighbors


pygame.init()

screen = pygame.display.set_mode((600, 600))
pygame.display.set_caption("Dynamic Puzzle")

puzzle = Puzzle(5)

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                puzzle.move("up")
            elif event.key == pygame.K_DOWN:
                puzzle.move("down")
            elif event.key == pygame.K_LEFT:
                puzzle.move("left")
            elif event.key == pygame.K_RIGHT:
                puzzle.move("right")

    screen.fill((30, 30, 30))

    tile_size = tile_size = 600 // puzzle.size

    for row in range(puzzle.size):
        for col in range(puzzle.size):
            tile = puzzle.board[row][col]

            if tile != 0:
                rect = pygame.Rect(
                    col * tile_size,
                    row * tile_size,
                    tile_size,
                    tile_size
                )

                pygame.draw.rect(screen, (70, 130, 180), rect)

                font = pygame.font.Font(None, 60)
                text = font.render(str(tile), True, (255, 255, 255))

                text_rect = text.get_rect(center=rect.center)

                screen.blit(text, text_rect)

    pygame.display.flip()

pygame.quit()

puzzle = Puzzle(5)