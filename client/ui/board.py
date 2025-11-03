# S - Single Responsibility: Tách riêng từng trách nhiệm
import logging

logging.basicConfig(level=logging.INFO)

class BoardRenderer:
    """Chịu trách nhiệm vẽ bàn cờ lên canvas"""
    def __init__(self, canvas, board, pixel=40):
        self.canvas = canvas
        self.board = board
        self.pixel = pixel
        logging.info(f"BoardRenderer initialized with pixel size {self.pixel}")

    def draw_board(self):
        self.canvas.delete("all")
        # logging.info("Drawing board...")
        for i in range(self.board.size):
            for j in range(self.board.size):
                x, y = i * self.pixel, j * self.pixel
                self.canvas.create_rectangle(x, y, x + self.pixel, y + self.pixel, outline="black", width=1)
                piece = self.board.get(j, i)
                if piece == 1:
                    # logging.info(f"Draw circle at ({j}, {i})")
                    self.draw_circle(x + self.pixel // 2, y + self.pixel // 2, 18, "blue")
                elif piece == 2:
                    # logging.info(f"Draw cross at ({j}, {i})")
                    self.draw_cross(x + self.pixel // 2, y + self.pixel // 2, 18, "red")

    def draw_circle(self, x, y, size, color):
        # logging.info(f"Drawing circle at pixel ({x}, {y}), size {size}, color {color}")
        self.canvas.create_oval(x - size, y - size, x + size, y + size, outline="black", fill=color, width=3)

    def draw_cross(self, x, y, size, color):
        logging.info(f"Drawing cross at pixel ({x}, {y}), size {size}, color {color}")
        self.canvas.create_line(x - size, y - size, x + size, y + size, fill=color, width=5)
        self.canvas.create_line(x + size, y - size, x - size, y + size, fill=color, width=5)
class Board(BoardRenderer):
    """Quản lý trạng thái bàn cờ và logic liên quan"""
    def __init__(self, size=25):
        self.size = size
        logging.info(f"Board initialized with size {self.size}")
        self.reset()

    def reset(self):
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        logging.info("Board reset.")

    def is_empty(self):
        empty = all(cell == 0 for row in self.grid for cell in row)
        logging.info(f"Board is_empty: {empty}")
        return empty

    def is_in(self, y, x):
        in_board = 0 <= y < self.size and 0 <= x < self.size
        # logging.info(f"Check is_in({y}, {x}): {in_board}")
        return in_board

    def get(self, y, x):
        if self.is_in(y, x):
            value = self.grid[y][x]
            # logging.info(f"Get cell ({y}, {x}): {value}")
            return value
        else:
            logging.info(f"Get cell ({y}, {x}): out of bounds")
            return None

    def set(self, y, x, value):
        if self.is_in(y, x):
            self.grid[y][x] = value
            # logging.info(f"Set cell ({y}, {x}) to {value}")
        else:
            logging.info(f"Set cell ({y}, {x}) failed: out of bounds")

    def reset_cell(self, y, x):
        if self.is_in(y, x):
            self.grid[y][x] = 0
            logging.info(f"Reset cell ({y}, {x}) to 0")
        else:
            logging.info(f"Reset cell ({y}, {x}) failed: out of bounds")
