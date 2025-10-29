import random
from player.player import Player

class AIPlayer(Player):
    """Người chơi máy, kế thừa Player"""
    def make_move(self, board):
        # Đơn giản: chọn ô trống ngẫu nhiên
        empty_cells = [(y, x) for y in range(board.size) for x in range(board.size) if board.get(y, x) == 0]
        if empty_cells:
            y, x = random.choice(empty_cells)
            board.set(y, x, self.piece_id)
            return y, x
        return None