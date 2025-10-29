class GameManager:
	"""Quản lý trạng thái và logic của ván cờ"""
	def __init__(self, board_size=15):
		self.board_size = board_size
		self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
		self.current_player = 1
		self.winner = None

	def make_move(self, x, y, player):
		"""Xử lý nước đi của người chơi"""
		if self.board[y][x] == 0 and player == self.current_player:
			self.board[y][x] = player
			if self.check_win(x, y, player):
				self.winner = player
			else:
				self.current_player = 2 if player == 1 else 1
			return True
		return False

	def check_win(self, x, y, player):
		"""Kiểm tra người chơi có thắng không sau nước đi vừa rồi"""
		directions = [(1,0), (0,1), (1,1), (1,-1)]
		for dx, dy in directions:
			count = 1
			for dir in [1, -1]:
				nx, ny = x, y
				while True:
					nx += dx * dir
					ny += dy * dir
					if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[ny][nx] == player:
						count += 1
					else:
						break
			if count >= 5:
				return True
		return False

	def is_full(self):
		"""Kiểm tra bàn cờ đã đầy chưa"""
		return all(cell != 0 for row in self.board for cell in row)

	def reset(self):
		"""Khởi tạo lại ván mới"""
		self.board = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]
		self.current_player = 1
		self.winner = None

	def handle_move_message(self, data):
		"""Xử lý thông điệp move từ client và trả về response cho server"""
		if data.get("type") == "move":
			x = data.get("x")
			y = data.get("y")
			player = data.get("player")
			if self.make_move(x, y, player):
				response = {
					"status": "success",
					"board": self.board,
					"current_player": self.current_player,
					"winner": self.winner
				}
			else:
				response = {"status": "invalid_move"}
			return response
		return {"status": "unknown_type"}
