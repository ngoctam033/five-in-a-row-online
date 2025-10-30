# L - Liskov Substitution: Các class con có thể thay thế class cha mà không phá vỡ logic
import logging
logging.basicConfig(level=logging.INFO)
class Player:
    """Đại diện cho người chơi"""
    def __init__(self, piece_id):
        logging.info(f"Player initialized with piece_id {piece_id}")
        self.piece_id = piece_id

    def make_move(self, board, y, x):
        if board.get(y, x) == 0:
            # logging.info(f"Player {self.piece_id} made a move at ({y}, {x}).")
            board.set(y, x, self.piece_id)
            return True
        logging.info(f"Player {self.piece_id} failed to make a move at ({y}, {x}): Cell is already occupied.")  
        return False
    
class OnlinePlayer(Player):
    """Đại diện cho người chơi online, nhận nước đi từ network"""
    def make_move(self, board, y, x):
        # Có thể thêm logic nhận nước đi từ client/network ở đây
        logging.info(f"OnlinePlayer {self.piece_id} thực hiện nước đi tại ({y}, {x}) qua mạng.")
        return super().make_move(board, y, x)