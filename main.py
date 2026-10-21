import random
import pygame
import time
import heapq
from collections import deque
from itertools import count


# =========================================================
# Search Node
# =========================================================

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


# =========================================================
# Puzzle
# =========================================================

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

        if not (
            0 <= new_row < self.size
            and 0 <= new_col < self.size
        ):
            return False

        self.board[row][col], self.board[new_row][new_col] = (
            self.board[new_row][new_col],
            self.board[row][col]
        )

        return True

    def shuffle(self, moves=100):
        directions = ["up", "down", "left", "right"]

        opposite = {
            "up": "down",
            "down": "up",
            "left": "right",
            "right": "left"
        }

        previous_direction = None

        for _ in range(moves):
            possible_moves = [
                direction
                for direction in self.get_possible_moves()
                if direction != opposite.get(previous_direction)
            ]

            if not possible_moves:
                possible_moves = self.get_possible_moves()

            direction = random.choice(possible_moves)
            self.move(direction)

            previous_direction = direction

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


# =========================================================
# Search Algorithms
# =========================================================

# Maximum number of expanded nodes per search.
MAX_EXPLORED_NODES = 250_000

# Maximum depth explored by DFS.
DFS_DEPTH_LIMIT = 100


# ---------------------------------------------------------
# 1. Breadth-First Search (BFS)
# ---------------------------------------------------------

def bfs(puzzle):
    start_state = puzzle.get_state()
    goal_state = puzzle.goal_state

    queue = deque([Node(start_state)])
    visited = {start_state}
    explored_nodes = 0

    while queue and explored_nodes < MAX_EXPLORED_NODES:
        current_node = queue.popleft()
        explored_nodes += 1

        if current_node.state == goal_state:
            return current_node.get_path(), explored_nodes

        current_puzzle = puzzle.from_state(current_node.state)

        for direction in current_puzzle.get_possible_moves():
            new_puzzle = puzzle.from_state(current_node.state)
            new_puzzle.move(direction)

            new_state = new_puzzle.get_state()

            if new_state not in visited:
                visited.add(new_state)

                child_node = Node(
                    state=new_state,
                    parent=current_node,
                    action=direction,
                    cost=current_node.cost + 1,
                    depth=current_node.depth + 1
                )

                queue.append(child_node)

    return None, explored_nodes


# ---------------------------------------------------------
# 2. Depth-First Search (DFS)
# ---------------------------------------------------------

def dfs(puzzle):
    start_state = puzzle.get_state()
    goal_state = puzzle.goal_state

    stack = [Node(start_state)]
    visited = {start_state}
    explored_nodes = 0

    while stack and explored_nodes < MAX_EXPLORED_NODES:
        current_node = stack.pop()
        explored_nodes += 1

        if current_node.state == goal_state:
            return current_node.get_path(), explored_nodes

        if current_node.depth >= DFS_DEPTH_LIMIT:
            continue

        current_puzzle = puzzle.from_state(current_node.state)

        for direction in reversed(
            current_puzzle.get_possible_moves()
        ):
            new_puzzle = puzzle.from_state(current_node.state)
            new_puzzle.move(direction)

            new_state = new_puzzle.get_state()

            if new_state not in visited:
                visited.add(new_state)

                child_node = Node(
                    state=new_state,
                    parent=current_node,
                    action=direction,
                    cost=current_node.cost + 1,
                    depth=current_node.depth + 1
                )

                stack.append(child_node)

    return None, explored_nodes


# ---------------------------------------------------------
# 3. Manhattan Distance Heuristic
# ---------------------------------------------------------

def manhattan_distance(state, size):
    distance = 0

    for index, tile in enumerate(state):
        if tile == 0:
            continue

        current_row, current_col = divmod(index, size)

        # In the goal state, tile 1 is at index 0,
        # tile 2 at index 1, and so on.
        goal_index = tile - 1
        goal_row, goal_col = divmod(goal_index, size)

        distance += (
            abs(current_row - goal_row)
            + abs(current_col - goal_col)
        )

    return distance


# ---------------------------------------------------------
# 4. A* Search
# ---------------------------------------------------------

def astar(puzzle):
    start_state = puzzle.get_state()
    goal_state = puzzle.goal_state

    counter = count()

    priority_queue = [
        (
            manhattan_distance(start_state, puzzle.size),
            next(counter),
            Node(start_state)
        )
    ]

    best_cost = {start_state: 0}
    explored_nodes = 0

    while (
        priority_queue
        and explored_nodes < MAX_EXPLORED_NODES
    ):
        _, _, current_node = heapq.heappop(priority_queue)

        # Ignore outdated entries in the priority queue.
        if current_node.cost != best_cost.get(current_node.state):
            continue

        explored_nodes += 1

        if current_node.state == goal_state:
            return current_node.get_path(), explored_nodes

        current_puzzle = puzzle.from_state(current_node.state)

        for direction in current_puzzle.get_possible_moves():
            new_puzzle = puzzle.from_state(current_node.state)
            new_puzzle.move(direction)

            new_state = new_puzzle.get_state()
            new_cost = current_node.cost + 1

            if new_cost < best_cost.get(new_state, float("inf")):
                best_cost[new_state] = new_cost

                child_node = Node(
                    state=new_state,
                    parent=current_node,
                    action=direction,
                    cost=new_cost,
                    depth=current_node.depth + 1
                )

                heuristic = manhattan_distance(
                    new_state,
                    puzzle.size
                )

                priority = new_cost + heuristic

                heapq.heappush(
                    priority_queue,
                    (
                        priority,
                        next(counter),
                        child_node
                    )
                )

    return None, explored_nodes


# =========================================================
# Input
# =========================================================

while True:
    try:
        size = int(input("Enter puzzle size (3-10): "))

        if 3 <= size <= 10:
            break

        print("Please enter a number from 3 to 10.")

    except ValueError:
        print("Invalid input. Please enter an integer.")


# =========================================================
# Pygame Setup
# =========================================================

pygame.init()

WIDTH = 1000
HEIGHT = 800

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Puzzle Solver")


# =========================================================
# Colors
# =========================================================

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
WARNING = (255, 90, 100)


# =========================================================
# Initialize Game
# =========================================================

puzzle = Puzzle(size)
puzzle.shuffle()

goal_puzzle = Puzzle(size)

running = True
game_won = False
game_over = False

move_count = 0
max_moves = 20


# =========================================================
# Fonts
# =========================================================

title_font = pygame.font.Font(None, 42)
label_font = pygame.font.Font(None, 30)
number_font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 24)


# =========================================================
# Algorithm Selection
# =========================================================

algorithms = ["BFS", "DFS", "A*"]
selected_algorithm_index = 0

algorithm_button = pygame.Rect(390, 555, 220, 40)
solve_button = pygame.Rect(390, 605, 220, 45)
restart_button = pygame.Rect(420, 660, 160, 40)

solve_requested = False

solution = []
solution_index = 0
last_move_time = 0
is_solving = False

explored_nodes = 0
elapsed_time = 0.0
last_solution_length = None

search_message = ""


# =========================================================
# Draw Puzzle
# =========================================================

def draw_puzzle(
    puzzle_obj,
    x,
    y,
    board_size,
    title,
    accent_color
):
    title_text = label_font.render(
        title,
        True,
        accent_color
    )

    title_rect = title_text.get_rect(
        center=(x + board_size // 2, y - 25)
    )

    screen.blit(title_text, title_rect)

    tile_size = board_size // puzzle_obj.size

    for row in range(puzzle_obj.size):
        for col in range(puzzle_obj.size):
            tile = puzzle_obj.board[row][col]

            rect = pygame.Rect(
                x + col * tile_size + 3,
                y + row * tile_size + 3,
                tile_size - 6,
                tile_size - 6
            )

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

                # Reduce font size for large boards.
                if puzzle_obj.size >= 7:
                    tile_font = pygame.font.Font(
                        None,
                        max(18, 42 - puzzle_obj.size)
                    )
                else:
                    tile_font = number_font

                text = tile_font.render(
                    str(tile),
                    True,
                    TEXT
                )

                text_rect = text.get_rect(
                    center=rect.center
                )

                screen.blit(text, text_rect)


# =========================================================
# Mouse Movement
# =========================================================

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


# =========================================================
# Restart Game
# =========================================================

def restart_game():
    global puzzle, move_count, game_won, game_over
    global solve_requested, solution, solution_index
    global last_move_time, is_solving
    global explored_nodes, elapsed_time
    global last_solution_length, search_message

    puzzle = Puzzle(size)
    puzzle.shuffle()

    move_count = 0
    game_won = False
    game_over = False

    solve_requested = False

    solution = []
    solution_index = 0
    last_move_time = 0

    is_solving = False

    explored_nodes = 0
    elapsed_time = 0.0

    last_solution_length = None
    search_message = ""


# =========================================================
# Main Loop
# =========================================================

clock = pygame.time.Clock()

while running:

    # -----------------------------------------------------
    # Events
    # -----------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r:
                restart_game()

            elif (
                not game_won
                and not game_over
                and not is_solving
            ):

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

            if event.button == 1:

                # Restart button
                if restart_button.collidepoint(event.pos):
                    restart_game()

                # Algorithm selector
                elif algorithm_button.collidepoint(event.pos):

                    if not is_solving:
                        selected_algorithm_index = (
                            selected_algorithm_index + 1
                        ) % len(algorithms)

                        search_message = ""

                # Auto-solve button
                elif (
                    solve_button.collidepoint(event.pos)
                    and not game_won
                    and not game_over
                    and not is_solving
                ):
                    solve_requested = True

                # Manual mouse movement
                elif (
                    not game_won
                    and not game_over
                    and not is_solving
                ):
                    moved = handle_mouse_click(event.pos)

                    if moved:
                        move_count += 1

    # -----------------------------------------------------
    # Check Win / Lose
    # -----------------------------------------------------

    if puzzle.is_solved():
        game_won = True
        game_over = False
        is_solving = False

    if (
        move_count >= max_moves
        and not game_won
        and not is_solving
    ):
        game_over = True

    # -----------------------------------------------------
    # Run Selected Algorithm
    # -----------------------------------------------------

    if solve_requested:

        algorithm_name = algorithms[selected_algorithm_index]

        algorithm_functions = {
            "BFS": bfs,
            "DFS": dfs,
            "A*": astar
        }

        selected_algorithm = algorithm_functions[algorithm_name]

        start_time = time.perf_counter()

        solution, explored_nodes = selected_algorithm(puzzle)

        elapsed_time = time.perf_counter() - start_time

        solution = solution or []

        solution_index = 0
        last_move_time = pygame.time.get_ticks()

        last_solution_length = (
            len(solution) if solution else None
        )

        is_solving = bool(solution)
        solve_requested = False

        if puzzle.is_solved():

            game_won = True
            search_message = "Puzzle is already solved."

        elif not solution:

            search_message = (
                f"{algorithm_name}: no solution found "
                "within search limits."
            )

        else:

            search_message = (
                f"{algorithm_name} found a path of "
                f"{len(solution)} moves."
            )

    # -----------------------------------------------------
    # Automatic Solution Animation
    # -----------------------------------------------------

    if is_solving and solution_index < len(solution):

        current_time = pygame.time.get_ticks()

        if current_time - last_move_time >= 300:

            puzzle.move(solution[solution_index])

            solution_index += 1
            last_move_time = current_time

            # Count automatic moves as well.
            move_count += 1

            if solution_index >= len(solution):
                is_solving = False

    # -----------------------------------------------------
    # Background
    # -----------------------------------------------------

    screen.fill(BACKGROUND)

    # -----------------------------------------------------
    # Main Title
    # -----------------------------------------------------

    title = title_font.render(
        "Dynamic Puzzle Solver",
        True,
        TEXT
    )

    title_rect = title.get_rect(
        center=(WIDTH // 2, 35)
    )

    screen.blit(title, title_rect)

    # -----------------------------------------------------
    # Move Counter
    # -----------------------------------------------------

    moves_text = label_font.render(
        f"Moves: {move_count} / {max_moves}",
        True,
        TEXT
    )

    moves_rect = moves_text.get_rect(
        center=(WIDTH // 2, 68)
    )

    screen.blit(moves_text, moves_rect)

    # -----------------------------------------------------
    # Puzzle Cards
    # -----------------------------------------------------

    card_width = 440
    card_height = 470

    left_card = pygame.Rect(
        30, 80, card_width, card_height
    )

    right_card = pygame.Rect(
        530, 80, card_width, card_height
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

    # -----------------------------------------------------
    # Current Puzzle
    # -----------------------------------------------------

    board_size = 380

    draw_puzzle(
        puzzle,
        60,
        160,
        board_size,
        "CURRENT PUZZLE",
        ACCENT
    )

    # -----------------------------------------------------
    # Goal Puzzle
    # -----------------------------------------------------

    draw_puzzle(
        goal_puzzle,
        560,
        160,
        board_size,
        "GOAL PUZZLE",
        GOAL_ACCENT
    )

    # -----------------------------------------------------
    # Algorithm Selection Button
    # -----------------------------------------------------

    pygame.draw.rect(
        screen,
        CARD_BORDER,
        algorithm_button,
        border_radius=9
    )

    pygame.draw.rect(
        screen,
        ACCENT,
        algorithm_button,
        width=2,
        border_radius=9
    )

    algorithm_text = label_font.render(
        f"Algorithm: {algorithms[selected_algorithm_index]}",
        True,
        TEXT
    )

    algorithm_text_rect = algorithm_text.get_rect(
        center=algorithm_button.center
    )

    screen.blit(
        algorithm_text,
        algorithm_text_rect
    )

    # -----------------------------------------------------
    # Auto Solve Button
    # -----------------------------------------------------

    pygame.draw.rect(
        screen,
        ACCENT,
        solve_button,
        border_radius=10
    )

    solve_text = label_font.render(
        "SOLVING..." if is_solving else "AUTO SOLVE",
        True,
        BACKGROUND
    )

    solve_text_rect = solve_text.get_rect(
        center=solve_button.center
    )

    screen.blit(
        solve_text,
        solve_text_rect
    )

    # -----------------------------------------------------
    # Restart Button
    # -----------------------------------------------------

    pygame.draw.rect(
        screen,
        GOAL_ACCENT,
        restart_button,
        border_radius=10
    )

    restart_text = label_font.render(
        "RESTART",
        True,
        BACKGROUND
    )

    restart_text_rect = restart_text.get_rect(
        center=restart_button.center
    )

    screen.blit(
        restart_text,
        restart_text_rect
    )

    # -----------------------------------------------------
    # Algorithm Statistics
    # -----------------------------------------------------

    stats_text = small_font.render(
        f"Algorithm: {algorithms[selected_algorithm_index]} | "
        f"Nodes: {explored_nodes} | "
        f"Time: {elapsed_time:.4f}s",
        True,
        SECONDARY_TEXT
    )

    stats_rect = stats_text.get_rect(
        center=(WIDTH // 2, 715)
    )

    screen.blit(
        stats_text,
        stats_rect
    )

    # -----------------------------------------------------
    # Solution Length
    # -----------------------------------------------------

    if last_solution_length is not None:

        path_text = small_font.render(
            f"Solution length: {last_solution_length} moves",
            True,
            SECONDARY_TEXT
        )

        path_rect = path_text.get_rect(
            center=(WIDTH // 2, 738)
        )

        screen.blit(
            path_text,
            path_rect
        )

    # -----------------------------------------------------
    # Search Message
    # -----------------------------------------------------

    if search_message:

        message_text = small_font.render(
            search_message,
            True,
            SECONDARY_TEXT
        )

        message_rect = message_text.get_rect(
            center=(WIDTH // 2, 758)
        )

        screen.blit(
            message_text,
            message_rect
        )

    # -----------------------------------------------------
    # Win / Game Over Message
    # -----------------------------------------------------

    if game_won:

        result_text = title_font.render(
            "YOU WIN!",
            True,
            GOAL_ACCENT
        )

        result_rect = result_text.get_rect(
            center=(WIDTH // 2, 785)
        )

        screen.blit(
            result_text,
            result_rect
        )

    elif game_over:

        result_text = title_font.render(
            "GAME OVER!",
            True,
            WARNING
        )

        result_rect = result_text.get_rect(
            center=(WIDTH // 2, 785)
        )

        screen.blit(
            result_text,
            result_rect
        )

    # -----------------------------------------------------
    # Update Display
    # -----------------------------------------------------

    pygame.display.flip()
    clock.tick(60)


pygame.quit()