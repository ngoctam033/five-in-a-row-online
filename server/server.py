import asyncio
import websockets
from game_manager import GameManager
import json
import logging
from player import Player
from room import Room
logging.basicConfig(level=logging.INFO)
class WebSocketServer:
	def __init__(self, host='0.0.0.0', port=9000):
		self.host = host
		self.port = port
		self.rooms = []
		self.players = []

	async def process_message(self, websocket):
		logging.info(f"Client connected: {websocket.remote_address}")
		try:
			async for message in websocket:
				# logging.info(f"Received: {message}")
				try:
					data = json.loads(message)
					response = "This is a response for move message"
					logging.info(f"Parsed JSON data: {data}")
					if data.get("type") == "create_account":
						response = self.create_player(websocket, player_name=data.get("player"))
					if data.get("type") == "create_room":
						logging.info("Creating room with players: %s vs %s", data.get("player"), data.get("opponent"))
						response = self.create_room_with_players(player1_name=data.get("player"), player2_name=data.get("opponent"))
					if data.get("type") == "get_online_players":
						response = self.get_online_players(user_name=data.get("player"))
					if data.get("type") == "move":
						response = self.get_opponent_move(data)
					if data.get("type") == "check_challengeable":
						response = self.check_challengeable(user_name=data.get("player"), opponent_name=data.get("opponent"))
					await websocket.send(json.dumps(response))
				except json.JSONDecodeError:
					logging.warning("Received non-JSON message: %s", message)
		except websockets.ConnectionClosed:
			logging.info("Client disconnected")
			self.players = [p for p in self.players if p.websocket != websocket]
			await websocket.close()  # Đảm bảo đóng kết nối phía server
	
	def create_player(self, websocket, player_name):
		# Kiểm tra player đã tồn tại chưa (theo websocket)
		if any(p.websocket == websocket for p in self.players):
			logging.info(f"Player for websocket {websocket.remote_address} already exists.")
			return False
		player_id = str(websocket.remote_address)
		player = Player(player_id=player_id, name=player_name, piece_id=1, websocket=websocket)
		self.players.append(player)
		return True

	def get_online_players(self, user_name):
		"""
		Trả về list name các người chơi đang online, ngoại trừ user_name
		Args:
			user_name (str): tên người chơi yêu cầu
		"""
		return [player.name for player in self.players if player.name != user_name]
	def get_opponent_move(self, data):
		"""
		Trả về nước đi cuối cùng của đối thủ trong room cho client
		Args:
			data: dict chứa thông tin
			ví dụ:
				move_data = {
				"type": "move",
				"player": playername,
				"x": x,
				"y": y
				}
		Return:
			dict: thông tin nước đi của đối thủ (nếu có), None nếu chưa có nước đi
		"""
		return {
			"x": 1,
			"y": 1,
			"player": "opponent_name",
			"type": "opponent_move"
		}

	def check_challengeable(self, user_name, opponent_name):
		"""
		Kiểm tra xem hai user có thể ghép cặp thách đấu với nhau không.
		Điều kiện:
		- Cả hai user đều đang online
		- Cả hai user đều chưa tham gia phòng nào
		Args:
			user_name (str): tên người chơi yêu cầu
			opponent_name (str): tên đối thủ
		Return:
			bool: True nếu có thể thách đấu, False nếu không
		"""
		user = next((p for p in self.players if p.name == user_name), None)
		opponent = next((p for p in self.players if p.name == opponent_name), None)
		logging.info(f"Checking challengeable: user={user}, opponent={opponent}")
		if not user or not opponent:
			return False
		room_user = self.find_room_by_playername(user_name)
		room_opponent = self.find_room_by_playername(opponent_name)
		# Nếu cả hai cùng chung một room thì trả về True
		if room_user and room_opponent and room_user == room_opponent:
			return True
		# Nếu opponent đã ở phòng khác thì không thể thách đấu
		if room_opponent is not None:
			return False
		# Nếu cả hai chưa ở phòng nào thì có thể thách đấu
		return True
		
	def find_room_by_playername(self, playername):
		"""
		Tìm kiếm room có player1 hoặc player2 có tên bằng playername
		Args:
			playername (str): tên người chơi cần tìm
		Return:
			Room object nếu tìm thấy, None nếu không có
		"""
		for room in self.rooms:
			if (room.player1 and room.player1.name == playername) or (room.player2 and room.player2.name == playername):
				return room
		return None
	
	def create_room_with_players(self, player1_name, player2_name):
		"""
		Tạo một room mới với 2 player theo tên, thêm vào danh sách rooms.
		Kiểm tra hợp lệ: cả 2 đều online, chưa ở phòng nào, không trùng tên.
		Args:
			player1_name (str): tên người chơi 1
			player2_name (str): tên người chơi 2
		Return:
			dict: thông tin room nếu tạo thành công, None nếu lỗi
		"""
		if player1_name == player2_name:
			return None
		player1 = next((p for p in self.players if p.name == player1_name), None)
		player2 = next((p for p in self.players if p.name == player2_name), None)
		if not player1 or not player2:
			return None
		# Kiểm tra cả 2 chưa ở phòng nào
		if self.find_room_by_playername(player1_name) or self.find_room_by_playername(player2_name):
			return None
		# self.notify_opponent_challenged(player2_name, player1_name)
		# Tạo room id duy nhất
		room_id = f"room_{len(self.rooms)+1}"
		room = Room(room_id=room_id, player1=player1, player2=player2)
		self.rooms.append(room)
		# Trả về thông tin room dạng dict
		return {
			"room_id": room_id,
			"player1": player1.name,
			"player2": player2.name
		}
	# def notify_opponent_challenged(self, opponent_name, challenger_name):
	# 	"""
	# 	Gửi thông báo cho player2 (opponent) rằng đã có đối thủ thách đấu và chờ phản hồi.
	# 	Args:
	# 		opponent_name (str): tên người chơi bị thách đấu
	# 		challenger_name (str): tên người chơi gửi thách đấu
	# 	Return:
	# 		dict: phản hồi từ opponent hoặc None nếu timeout/lỗi
	# 	"""
	# 	opponent = next((p for p in self.players if p.name == opponent_name), None)
	# 	if opponent and opponent.websocket:
	# 		message = {
	# 			"type": "challenged",
	# 			"opponent": opponent_name,
	# 			"challenger": challenger_name,
	# 			"msg": f"Bạn đã được {challenger_name} thách đấu!"
	# 		}
	# 		try:
	# 			opponent.websocket.send(json.dumps(message))
	# 			logging.info(f"Sent challenge notification to {opponent_name}")
	# 			# Chờ phản hồi từ opponent (timeout 30s)
	# 			try:
	# 				response = asyncio.wait_for(opponent.websocket.recv(), timeout=30)
	# 				logging.info(f"Received challenge response from {opponent_name}: {response}")
	# 				response_data = json.loads(response)
	# 				if response_data.get("type") == "challenge_response":
	# 					return response_data
	# 				else:
	# 					logging.warning(f"Unexpected response type from {opponent_name}: {response_data}")
	# 					return None
	# 			except asyncio.TimeoutError:
	# 				logging.warning(f"Timeout waiting for challenge response from {opponent_name}")
	# 				return None
	# 		except Exception as e:
	# 			logging.warning(f"Failed to notify opponent {opponent_name}: {e}")
	# 			return None
	# 	return None
	async def start(self):
		async with websockets.serve(self.process_message,
							  		self.host,
									self.port,
									ping_interval=600,   # gửi ping mỗi 600 giây
									ping_timeout=600     # timeout nếu không nhận được pong trong 600 giây
									):
			logging.info(f"WebSocket server started on port {self.port}")
			await asyncio.Future()  # Run forever


