from game_manager import GameManager

class Room:
    def __init__(self, player1, player2, room_id=None):
        self.game_manager = GameManager()
        self.player1 = player1
        self.player2 = player2
        self.room_id = room_id
        self.current_turn = 1  # 1: người chơi 1, 2: người chơi 2

    def __repr__(self):
        return f"Room(player1={self.player1}, player2={self.player2})"
    
    def next_player(self):
        """
        Trả về tên user có lượt đi tiếp theo dựa trên trạng thái game_manager.
        """
        # Giả sử game_manager có thuộc tính current_turn: 1 hoặc 2
        if self.current_turn == 1:
            return self.player1.name if hasattr(self.player1, 'name') else self.player1
        elif self.current_turn == 2:
            return self.player2.name if hasattr(self.player2, 'name') else self.player2
    
    def current_player(self):
        """
        Trả về tên user đang có lượt đi dựa trên trạng thái game_manager.
        """
        if hasattr(self.game_manager, 'current_turn'):
            if self.game_manager.current_turn == 1:
                return self.player1.name if hasattr(self.player1, 'name') else self.player1
            elif self.game_manager.current_turn == 2:
                return self.player2.name if hasattr(self.player2, 'name') else self.player2
        # Nếu không xác định được, mặc định trả về player1
        return self.player1.name if hasattr(self.player1, 'name') else self.player1
