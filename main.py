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


    def is_solved(self):
        return self.get_state() == self.goal_state


size = int(input("Enter puzzle size (3-10): "))
pygame.init()

# -----------------------------
# Window
# -----------------------------

WIDTH = 1000
HEIGHT = 650

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Puzzle Solver")

# -----------------------------
# Colors
# -----------------------------

BACKGROUND = (15, 18, 25)
CARD = (25, 29, 39)
CARD_BORDER = (55, 62, 78)

TILE = (42, 49, 65)
TILE_BORDER = (75, 85, 105)

TEXT = (235, 238, 245)
SECONDARY_TEXT = (150, 158, 175)

ACCENT = (80, 180, 255)
GOAL_ACCENT = (90, 220, 160)

EMPTY = (18, 21, 29)

# -----------------------------
# Puzzle
# -----------------------------

puzzle = Puzzle(size)
puzzle.shuffle()

# Puzzle هدف
goal_puzzle = Puzzle(size)

running = True
game_won = False

# -----------------------------
# Fonts
# -----------------------------

title_font = pygame.font.Font(None, 42)
label_font = pygame.font.Font(None, 30)
number_font = pygame.font.Font(None, 50)

# -----------------------------
# Draw Puzzle Function
# -----------------------------

def draw_puzzle(puzzle, x, y, board_size, title, accent_color):
    # عنوان
    title_text = label_font.render(
        title,
        True,
        accent_color
    )

    title_rect = title_text.get_rect(
        center=(x + board_size // 2, y - 25)
    )

    screen.blit(title_text, title_rect)

    # اندازه هر خانه
    tile_size = board_size // puzzle.size

    for row in range(puzzle.size):
        for col in range(puzzle.size):

            tile = puzzle.board[row][col]

            rect = pygame.Rect(
                x + col * tile_size + 3,
                y + row * tile_size + 3,
                tile_size - 6,
                tile_size - 6
            )

            # خانه خالی
            if tile == 0:
                pygame.draw.rect(
                    screen,
                    EMPTY,
                    rect,
                    border_radius=10
                )

                pygame.draw.rect(
                    screen,
                    TILE_BORDER,
                    rect,
                    width=2,
                    border_radius=10
                )

            # خانه معمولی
            else:
                pygame.draw.rect(
                    screen,
                    TILE,
                    rect,
                    border_radius=10
                )

                pygame.draw.rect(
                    screen,
                    accent_color,
                    rect,
                    width=2,
                    border_radius=10
                )

                text = number_font.render(
                    str(tile),
                    True,
                    TEXT
                )

                text_rect = text.get_rect(
                    center=rect.center
                )

                screen.blit(text, text_rect)


# -----------------------------
# Main Loop
# -----------------------------

move_count = 0
max_moves = 20
game_over = False

def handle_mouse_click(pos):
    board_size = 380
    tile_size = board_size // size

    board_x = 60
    board_y = 160

    mouse_x, mouse_y = pos

    col = (mouse_x - board_x) // tile_size
    row = (mouse_y - board_y) // tile_size

    if not (0 <= row < size and 0 <= col < size):
        return False

    empty_row, empty_col = puzzle.find_empty()

    if abs(row - empty_row) + abs(col - empty_col) == 1:
        if row < empty_row:
            return puzzle.move("up")
        elif row > empty_row:
            return puzzle.move("down")
        elif col < empty_col:
            return puzzle.move("left")
        elif col > empty_col:
            return puzzle.move("right")

    return False

solve_button = pygame.Rect(400, 570, 200, 45)
solve_requested = False

while running:

    # -------------------------
    # Events
    # -------------------------

    for event in pygame.event.get():

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                puzzle = Puzzle(size)
                puzzle.shuffle()

                move_count = 0
                game_won = False
                game_over = False

            elif not game_won and not game_over:

                if event.key == pygame.K_UP:
                    moved = puzzle.move("up")

                elif event.key == pygame.K_DOWN:
                    moved = puzzle.move("down")

                elif event.key == pygame.K_LEFT:
                    moved = puzzle.move("left")

                elif event.key == pygame.K_RIGHT:
                    moved = puzzle.move("right")

                else:
                    moved = False

                if moved:
                    move_count += 1


        elif event.type == pygame.MOUSEBUTTONDOWN:

            if not game_won and not game_over:

                if solve_button.collidepoint(event.pos):

                    solve_requested = True


                else:

                    moved = handle_mouse_click(event.pos)

                    if moved:
                        move_count += 1
    # -------------------------
    # Check Win
    # -------------------------

    if puzzle.is_solved():
        game_won = True

    if move_count >= max_moves and not game_won:
        game_over = True

    # -------------------------
    # Background
    # -------------------------

    screen.fill(BACKGROUND)

    # -------------------------
    # Main Title
    # -------------------------

    title = title_font.render(
        "Dynamic Puzzle Solver",
        True,
        TEXT
    )

    title_rect = title.get_rect(
        center=(WIDTH // 2, 45)
    )

    screen.blit(title, title_rect)

    # -------------------------
    # Cards
    # -------------------------

    moves_text = label_font.render(
        f"Moves: {move_count}",
        True,
        TEXT
    )

    moves_rect = moves_text.get_rect(
        center=(WIDTH // 2, 75)
    )

    screen.blit(moves_text, moves_rect)

    card_width = 440
    card_height = 510

    left_card = pygame.Rect(
        30,
        80,
        card_width,
        card_height
    )

    right_card = pygame.Rect(
        530,
        80,
        card_width,
        card_height
    )

    pygame.draw.rect(
        screen,
        CARD,
        left_card,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        CARD_BORDER,
        left_card,
        width=2,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        CARD,
        right_card,
        border_radius=18
    )

    pygame.draw.rect(
        screen,
        CARD_BORDER,
        right_card,
        width=2,
        border_radius=18
    )

    # -------------------------
    # Draw Current Puzzle
    # -------------------------

    board_size = 380

    draw_puzzle(
        puzzle,
        60,
        160,
        board_size,
        "CURRENT PUZZLE",
        ACCENT
    )

    # -------------------------
    # Draw Goal Puzzle
    # -------------------------

    draw_puzzle(
        goal_puzzle,
        560,
        160,
        board_size,
        "GOAL PUZZLE",
        GOAL_ACCENT
    )

    # -------------------------
    # Win Message
    # -------------------------

    if game_won:
        result_text = title_font.render(
            "YOU WIN!",
            True,
            GOAL_ACCENT
        )

    elif game_over:
        result_text = title_font.render(
            "GAME OVER!",
            True,
            (255, 90, 100)
        )

    else:
        result_text = None

    if result_text:
        result_rect = result_text.get_rect(
            center=(WIDTH // 2, 620)
        )
        screen.blit(result_text, result_rect)

    pygame.draw.rect(
        screen,
        ACCENT,
        solve_button,
        border_radius=10
    )

    solve_text = label_font.render(
        "AUTO SOLVE",
        True,
        BACKGROUND
    )

    solve_text_rect = solve_text.get_rect(
        center=solve_button.center
    )

    screen.blit(solve_text, solve_text_rect)

    # -------------------------
    # Update Display
    # -------------------------

    pygame.display.flip()


pygame.quit()
