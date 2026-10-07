class Puzzle:
    def __init__(self, size):
        self.size = size
        self.board = [
            list(range(row * size + 1, row * size + size + 1))
            for row in range(size)
        ]
        self.board[-1][-1] = 0


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