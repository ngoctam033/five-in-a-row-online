"""
Protocol Module - Định nghĩa giao thức giao tiếp
Simple network communication protocol for Five-in-a-Row game
"""

class MessageType:
    """Message types for client-server communication"""
    
    # Authentication
    LOGIN = "LOGIN"
    LOGIN_SUCCESS = "LOGIN_SUCCESS"
    LOGIN_FAIL = "LOGIN_FAIL"
    
    # Game matching
    WAITING = "WAITING"
    GAME_START = "GAME_START"
    
    # Game play
    MOVE = "MOVE"
    UPDATE_BOARD = "UPDATE_BOARD"
    YOUR_TURN = "YOUR_TURN"
    
    # Game results
    GAME_WIN = "GAME_WIN"
    GAME_LOSE = "GAME_LOSE"
    
    # Connection
    CONNECTION_LOST = "CONNECTION_LOST"

class Protocol:
    """Protocol helper functions"""
    
    @staticmethod
    def create_login_message(username):
        """Create login message"""
        return f"LOGIN|{username}"
    
    @staticmethod
    def create_move_message(col, row):
        """Create move message"""
        return f"MOVE|{col},{row}"
    
    @staticmethod
    def parse_message(message):
        """Parse incoming message"""
        parts = message.strip().split('|')
        if len(parts) >= 1:
            command = parts[0]
            data = parts[1:] if len(parts) > 1 else []
            return command, data
        return None, []
    
    @staticmethod
    def create_game_start_message(opponent_name, player_id):
        """Create game start message"""
        return f"GAME_START|{opponent_name}|{player_id}"
    
    @staticmethod
    def create_update_board_message(move_data, piece_id):
        """Create board update message"""
        return f"UPDATE_BOARD|{move_data}|{piece_id}"
