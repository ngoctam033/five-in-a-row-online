from game_manager import GameManager

class Room:
    def __init__(self, player1, player2, room_id=None):
        self.game_manager = GameManager()
        self.player1 = player1
        self.player2 = player2
        self.room_id = room_id

    def __repr__(self):
        return f"Room(player1={self.player1}, player2={self.player2})"
