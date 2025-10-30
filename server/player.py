class Player:
    """Lưu trữ thông tin người chơi cờ caro"""
    def __init__(self, player_id, name, piece_id, is_online=True):
        self.player_id = player_id      # Mã định danh người chơi (có thể là số hoặc chuỗi)
        self.name = name                # Tên người chơi
        self.piece_id = piece_id        # Loại quân cờ (1 hoặc 2)
        self.score = 0                  # Điểm số (nếu có)

    def to_dict(self):
        """Trả về thông tin người chơi dưới dạng dict (dùng cho truyền qua mạng hoặc lưu trữ)"""
        return {
            "player_id": self.player_id,
            "name": self.name,
            "piece_id": self.piece_id,
            "is_online": self.is_online,
            "score": self.score
        }

    def __repr__(self):
        return f"Player({self.player_id}, {self.name}, piece={self.piece_id}, online={self.is_online}, score={self.score})"