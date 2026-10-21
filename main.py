import random
import pygame
import time
import threading
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
    def __init__(self, size, goal_state=None):
        self.size = size

        if goal_state is None:
            board = [
                list(range(row * size + 1, row * size + size + 1))
                for row in range(size)
            ]
            board[-1][-1] = 0
            self.goal_state = tuple(tile for row in board for tile in row)
        else:
            self.goal_state = tuple(goal_state)
            board = [
                list(self.goal_state[row * size:(row + 1) * size])
                for row in range(size)
            ]

        self.board = board

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
        puzzle = Puzzle(self.size, goal_state=self.goal_state)

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

def manhattan_distance(state, size, goal_state=None):
    distance = 0
    if goal_state is None:
        goal_state = tuple(list(range(1, size * size)) + [0])
    goal_positions = {tile: divmod(index, size) for index, tile in enumerate(goal_state)}

    for index, tile in enumerate(state):
        if tile == 0:
            continue

        current_row, current_col = divmod(index, size)

        goal_row, goal_col = goal_positions[tile]

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
            manhattan_distance(start_state, puzzle.size, puzzle.goal_state),
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
                    puzzle.size,
                    puzzle.goal_state
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


# Puzzle size is selected in the setup screen (3-10).
size = 3

# =========================================================
# Pygame Setup and Theme
# =========================================================
pygame.init()
WIDTH, HEIGHT = 1000, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Puzzle Solver")

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

TITLE_FONT = pygame.font.Font(None, 42)
LABEL_FONT = pygame.font.Font(None, 30)
SMALL_FONT = pygame.font.Font(None, 24)

# Screens: first define the goal, then play the generated puzzle.
phase = "setup"
goal_entries = [None] * (size * size)
selected_cell = None
edit_buffer = ""
message = "Click a cell, type a number, then press Enter if needed. Use 0 for the empty tile."

puzzle = None
goal_puzzle = None
running = True
game_won = False
game_over = False
move_count = 0
max_moves = max(30, size * size * 3)

algorithms = ["BFS", "DFS", "A*"]
selected_algorithm_index = 0

size_minus_button = pygame.Rect(785, 28, 34, 32)
size_plus_button = pygame.Rect(925, 28, 34, 32)
next_button = pygame.Rect(400, 690, 200, 48)
algorithm_button = pygame.Rect(350, 600, 190, 42)
solve_button = pygame.Rect(555, 600, 190, 42)
restart_button = pygame.Rect(350, 650, 190, 38)
back_button = pygame.Rect(555, 650, 190, 38)

solve_requested = False
is_searching = False
search_generation = 0
solver_result = None
solution = []
solution_index = 0
last_move_time = 0
is_solving = False
explored_nodes = 0
elapsed_time = 0.0
last_solution_length = None
search_message = ""
clock = pygame.time.Clock()


def reset_setup(new_size=None):
    """Return to goal-entry phase and clear the goal grid."""
    global size, phase, goal_entries, selected_cell, edit_buffer, message
    global puzzle, goal_puzzle, move_count, max_moves, game_won, game_over
    global solve_requested, is_searching, search_generation, solver_result
    global solution, solution_index, is_solving, explored_nodes, elapsed_time
    global last_solution_length, search_message

    if new_size is not None:
        size = new_size
    search_generation += 1
    solver_result = None
    is_searching = False
    solve_requested = False
    phase = "setup"
    goal_entries = [None] * (size * size)
    selected_cell = None
    edit_buffer = ""
    message = "Fill every cell with numbers 0 to " + str(size * size - 1) + "."
    puzzle = None
    goal_puzzle = None
    move_count = 0
    max_moves = max(30, size * size * 3)
    game_won = False
    game_over = False
    solution = []
    solution_index = 0
    is_solving = False
    explored_nodes = 0
    elapsed_time = 0.0
    last_solution_length = None
    search_message = ""


def commit_edit_buffer():
    global edit_buffer, goal_entries, message
    if selected_cell is None or not edit_buffer:
        return True
    try:
        value = int(edit_buffer)
    except ValueError:
        edit_buffer = ""
        return False
    if not 0 <= value < size * size:
        message = f"Enter a value from 0 to {size * size - 1}."
        edit_buffer = ""
        return False
    goal_entries[selected_cell] = value
    edit_buffer = ""
    return True


def begin_game():
    global phase, puzzle, goal_puzzle, message, move_count, max_moves
    global game_won, game_over, selected_algorithm_index
    global solution, solution_index, is_solving, explored_nodes, elapsed_time
    global last_solution_length, search_message

    if not commit_edit_buffer():
        return
    expected = set(range(size * size))
    entered = [value for value in goal_entries if value is not None]
    if len(entered) != size * size:
        message = "Fill every cell first. Each number must appear exactly once."
        return
    if len(set(entered)) != size * size or set(entered) != expected:
        message = f"Use each number from 0 to {size * size - 1} exactly once."
        return

    goal_state = tuple(entered)
    goal_puzzle = Puzzle(size, goal_state=goal_state)
    puzzle = Puzzle(size, goal_state=goal_state)
    # A sequence of legal moves from the user-defined goal guarantees solvability.
    puzzle.shuffle(moves=max(30, size * size * 2))
    phase = "game"
    move_count = 0
    max_moves = max(30, size * size * (5 if algorithms[selected_algorithm_index] == "DFS" else 3))
    game_won = False
    game_over = False
    solution = []
    solution_index = 0
    is_solving = False
    explored_nodes = 0
    elapsed_time = 0.0
    last_solution_length = None
    search_message = "Puzzle generated from your goal. It is solvable."
    message = ""


def restart_game():
    global puzzle, move_count, max_moves, game_won, game_over
    global solve_requested, solution, solution_index, is_solving
    global explored_nodes, elapsed_time, last_solution_length, search_message
    global is_searching, search_generation, solver_result

    if goal_puzzle is None:
        return
    search_generation += 1
    solver_result = None
    is_searching = False
    puzzle = Puzzle(size, goal_state=goal_puzzle.goal_state)
    puzzle.shuffle(moves=max(30, size * size * 2))
    move_count = 0
    max_moves = max(30, size * size * (5 if algorithms[selected_algorithm_index] == "DFS" else 3))
    game_won = False
    game_over = False
    solve_requested = False
    solution = []
    solution_index = 0
    is_solving = False
    explored_nodes = 0
    elapsed_time = 0.0
    last_solution_length = None
    search_message = "Puzzle restarted from your custom goal."


def draw_size_controls():
    pygame.draw.rect(screen, CARD_BORDER, size_minus_button, border_radius=7)
    pygame.draw.rect(screen, ACCENT, size_minus_button, width=2, border_radius=7)
    screen.blit(LABEL_FONT.render("-", True, TEXT), LABEL_FONT.render("-", True, TEXT).get_rect(center=size_minus_button.center))
    size_label = SMALL_FONT.render(f"Size: {size} x {size}", True, TEXT)
    screen.blit(size_label, size_label.get_rect(center=(872, 44)))
    pygame.draw.rect(screen, CARD_BORDER, size_plus_button, border_radius=7)
    pygame.draw.rect(screen, ACCENT, size_plus_button, width=2, border_radius=7)
    plus_text = LABEL_FONT.render("+", True, TEXT)
    screen.blit(plus_text, plus_text.get_rect(center=size_plus_button.center))


def draw_board(board, x, y, board_size, title, accent, editable=False):
    title_surface = LABEL_FONT.render(title, True, accent)
    screen.blit(title_surface, title_surface.get_rect(center=(x + board_size // 2, y - 28)))
    tile_size = board_size // size
    for index in range(size * size):
        row, col = divmod(index, size)
        rect = pygame.Rect(x + col * tile_size + 3, y + row * tile_size + 3,
                           tile_size - 6, tile_size - 6)
        value = board[index] if editable else board[index]
        is_selected = editable and index == selected_cell
        fill = CARD_BORDER if is_selected else (EMPTY if value is None or value == 0 else TILE)
        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, GOAL_ACCENT if editable else accent, rect,
                         width=3 if is_selected else 2, border_radius=8)
        shown = edit_buffer if editable and is_selected and edit_buffer else value
        # In the setup screen, None means unfilled; 0 is displayed explicitly as the empty tile.
        if shown is not None and (editable or shown != 0):
            font_size = max(16, min(42, tile_size // 2))
            tile_font = pygame.font.Font(None, font_size)
            text = tile_font.render(str(shown), True, TEXT)
            screen.blit(text, text.get_rect(center=rect.center))


def draw_button(rect, label, color=ACCENT, text_color=BACKGROUND, border_color=None):
    pygame.draw.rect(screen, color, rect, border_radius=9)
    if border_color:
        pygame.draw.rect(screen, border_color, rect, width=2, border_radius=9)
    text = SMALL_FONT.render(label, True, text_color)
    screen.blit(text, text.get_rect(center=rect.center))


def handle_game_move(direction):
    global move_count
    if phase != "game" or game_won or game_over or is_solving or is_searching:
        return
    if puzzle.move(direction):
        move_count += 1


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN and phase == "setup":
            if event.key == pygame.K_ESCAPE:
                selected_cell = None
                edit_buffer = ""
            elif event.key == pygame.K_BACKSPACE:
                edit_buffer = edit_buffer[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                commit_edit_buffer()
            elif event.unicode.isdigit() and selected_cell is not None:
                max_digits = len(str(size * size - 1))
                if len(edit_buffer) < max_digits:
                    edit_buffer += event.unicode
                    if len(edit_buffer) >= max_digits:
                        commit_edit_buffer()

        elif event.type == pygame.KEYDOWN and phase == "game":
            if event.key == pygame.K_r:
                restart_game()
            elif event.key == pygame.K_ESCAPE:
                reset_setup()
            elif not game_won and not game_over and not is_solving and not is_searching:
                direction_by_key = {
                    pygame.K_UP: "up", pygame.K_DOWN: "down",
                    pygame.K_LEFT: "left", pygame.K_RIGHT: "right"
                }
                if event.key in direction_by_key:
                    handle_game_move(direction_by_key[event.key])

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if size_minus_button.collidepoint(event.pos):
                if size > 3:
                    reset_setup(size - 1)
            elif size_plus_button.collidepoint(event.pos):
                if size < 10:
                    reset_setup(size + 1)
            elif phase == "setup":
                board_x, board_y, board_size = 270, 130, 460
                tile_size = board_size // size
                col = (event.pos[0] - board_x) // tile_size
                row = (event.pos[1] - board_y) // tile_size
                if 0 <= row < size and 0 <= col < size:
                    commit_edit_buffer()
                    selected_cell = row * size + col
                    edit_buffer = ""
                elif next_button.collidepoint(event.pos):
                    begin_game()
            else:
                if solve_button.collidepoint(event.pos) and not game_won and not game_over and not is_solving and not is_searching:
                    solve_requested = True
                elif algorithm_button.collidepoint(event.pos) and not is_solving and not is_searching:
                    selected_algorithm_index = (selected_algorithm_index + 1) % len(algorithms)
                    max_moves = max(30, size * size * (5 if algorithms[selected_algorithm_index] == "DFS" else 3))
                    search_message = f"Selected algorithm: {algorithms[selected_algorithm_index]}"
                elif restart_button.collidepoint(event.pos):
                    restart_game()
                elif back_button.collidepoint(event.pos):
                    reset_setup()
                elif not game_won and not game_over and not is_solving and not is_searching:
                    board_x, board_y, board_size = 60, 155, 380
                    tile_size = board_size // size
                    col = (event.pos[0] - board_x) // tile_size
                    row = (event.pos[1] - board_y) // tile_size
                    if 0 <= row < size and 0 <= col < size:
                        er, ec = puzzle.find_empty()
                        if abs(row - er) + abs(col - ec) == 1:
                            direction = "up" if row < er else "down" if row > er else "left" if col < ec else "right"
                            handle_game_move(direction)

    # Start the requested algorithm exactly as selected; never silently switch BFS/DFS to A*.
    if phase == "game" and solve_requested and not is_searching:
        algorithm_name = algorithms[selected_algorithm_index]
        algorithm_functions = {"BFS": bfs, "DFS": dfs, "A*": astar}
        selected_algorithm = algorithm_functions[algorithm_name]
        puzzle_snapshot = puzzle.from_state(puzzle.get_state())
        generation = search_generation
        is_searching = True
        solve_requested = False
        search_message = f"Searching with {algorithm_name}..."

        def run_search(snapshot, function, generation_id, name):
            started = time.perf_counter()
            found_path, explored = function(snapshot)
            duration = time.perf_counter() - started
            global solver_result
            solver_result = (generation_id, name, found_path, explored, duration)

        threading.Thread(target=run_search,
                         args=(puzzle_snapshot, selected_algorithm, generation, algorithm_name),
                         daemon=True).start()

    if phase == "game" and solver_result is not None:
        result_generation, algorithm_name, found_path, found_explored, found_elapsed = solver_result
        if result_generation == search_generation:
            explored_nodes = found_explored
            elapsed_time = found_elapsed
            solution = found_path or []
            solution_index = 0
            last_move_time = pygame.time.get_ticks()
            last_solution_length = len(solution) if found_path is not None else None
            is_searching = False
            solver_result = None
            if puzzle.is_solved():
                game_won = True
                is_solving = False
                search_message = "Puzzle is already solved."
            elif found_path is None:
                is_solving = False
                search_message = f"{algorithm_name}: no solution found within search limits."
            else:
                is_solving = True
                search_message = f"{algorithm_name} found a path of {len(solution)} moves."
        else:
            solver_result = None

    if phase == "game" and is_solving and solution_index < len(solution):
        now = pygame.time.get_ticks()
        if now - last_move_time >= 220:
            puzzle.move(solution[solution_index])
            solution_index += 1
            last_move_time = now
            move_count += 1
            if solution_index >= len(solution):
                is_solving = False

    if phase == "game" and puzzle is not None:
        if puzzle.is_solved():
            game_won = True
            game_over = False
            is_solving = False
        elif move_count >= max_moves and not is_solving and not is_searching:
            game_over = True

    # ------------------------------ Draw ------------------------------
    screen.fill(BACKGROUND)
    title = TITLE_FONT.render("Dynamic Puzzle Solver", True, TEXT)
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 35)))
    draw_size_controls()

    if phase == "setup":
        subtitle = LABEL_FONT.render("STEP 1: DEFINE YOUR GOAL PUZZLE", True, GOAL_ACCENT)
        screen.blit(subtitle, subtitle.get_rect(center=(WIDTH // 2, 78)))
        draw_board(goal_entries, 270, 130, 460, "CLICK A CELL AND TYPE A NUMBER", GOAL_ACCENT, editable=True)
        help_lines = [
            f"Enter every number from 0 to {size * size - 1} exactly once.",
            "0 represents the empty square. Click a cell, type its value.",
            "For two-digit values, type both digits; press Enter to commit early."
        ]
        for i, line in enumerate(help_lines):
            text = SMALL_FONT.render(line, True, SECONDARY_TEXT)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, 600 + i * 22)))
        draw_button(next_button, "NEXT: CREATE PUZZLE", GOAL_ACCENT, BACKGROUND)
        if message:
            color = WARNING if ("Fill" in message or "Use each" in message or "Enter a value" in message) else SECONDARY_TEXT
            text = SMALL_FONT.render(message, True, color)
            screen.blit(text, text.get_rect(center=(WIDTH // 2, 770)))
    else:
        draw_board(puzzle.get_state(), 60, 155, 380, "CURRENT / SCRAMBLED PUZZLE", ACCENT)
        draw_board(goal_puzzle.get_state(), 560, 155, 380, "YOUR GOAL PUZZLE", GOAL_ACCENT)
        moves_text = LABEL_FONT.render(f"Moves: {move_count} / {max_moves}", True, TEXT)
        screen.blit(moves_text, moves_text.get_rect(center=(WIDTH // 2, 112)))
        draw_button(algorithm_button, f"Algorithm: {algorithms[selected_algorithm_index]}", CARD, TEXT, ACCENT)
        solve_label = "SEARCHING..." if is_searching else "SOLVING..." if is_solving else "AUTO SOLVE"
        draw_button(solve_button, solve_label, CARD_BORDER if is_searching or is_solving else ACCENT,
                    SECONDARY_TEXT if is_searching or is_solving else BACKGROUND)
        draw_button(restart_button, "RESTART", GOAL_ACCENT, BACKGROUND)
        draw_button(back_button, "EDIT GOAL", CARD, TEXT, GOAL_ACCENT)
        stats = SMALL_FONT.render(
            f"Algorithm: {algorithms[selected_algorithm_index]} | Nodes: {explored_nodes} | Time: {elapsed_time:.4f}s",
            True, SECONDARY_TEXT)
        screen.blit(stats, stats.get_rect(center=(WIDTH // 2, 710)))
        if last_solution_length is not None:
            path_text = SMALL_FONT.render(f"Solution length: {last_solution_length} moves", True, SECONDARY_TEXT)
            screen.blit(path_text, path_text.get_rect(center=(WIDTH // 2, 735)))
        if search_message:
            msg_text = SMALL_FONT.render(search_message, True, SECONDARY_TEXT)
            screen.blit(msg_text, msg_text.get_rect(center=(WIDTH // 2, 760)))
        if game_won:
            result = TITLE_FONT.render("YOU WIN!", True, GOAL_ACCENT)
            screen.blit(result, result.get_rect(center=(WIDTH // 2, 785)))
        elif game_over:
            result = TITLE_FONT.render("MOVE LIMIT REACHED - RESTART OR EDIT GOAL", True, WARNING)
            screen.blit(result, result.get_rect(center=(WIDTH // 2, 785)))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
