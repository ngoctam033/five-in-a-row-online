import asyncio
import websockets
from game_manager import GameManager
import json
from utils.logger import logger
from player import Player
from room import Room
from typing import List

class WebSocketServer:
	def __init__(self, host='0.0.0.0', port=9000):
		self.host = host
		self.port = port
		self.rooms: List[Room] = []
		self.players: List[Player] = []

	async def process_message(self, websocket):
		logger.info(f"Client connected: {websocket.remote_address}")
		try:
			async for message in websocket:
				# logger.info(f"Received: {message}")
				try:
					data = json.loads(message)
					response = "This is a response for move message"
					# logger.info(f"Parsed JSON data: {data}")
					if data.get("type") == "create_account":
						response = self.create_player(websocket, player_name=data.get("player"))
					if data.get("type") == "create_room":
						# logger.info("Creating room with players: %s vs %s", data.get("player"), data.get("opponent"))
						response = self.create_room_with_players(player1_name=data.get("player"), player2_name=data.get("opponent"))
						# logger.info(f"Room creation response: {response}")
					if data.get("type") == "get_online_players":
						response = self.get_online_players(user_name=data.get("player"))
						# logger.info(f"Online players for {data.get('player')}: {response}")
					if data.get("type") == "move":
						response = await self.get_opponent_move(data)
					if data.get("type") == "check_challengeable":
						response = await self.check_challengeable(user_name=data.get("player"), opponent_name=data.get("opponent"))
					await websocket.send(json.dumps(response))
				except json.JSONDecodeError:
					logger.warning("Received non-JSON message: %s", message)
		except websockets.ConnectionClosed:
			logger.info("Client disconnected")
			self.players = [p for p in self.players if p.websocket != websocket]
			await websocket.close()  # Đảm bảo đóng kết nối phía server
	
	def create_player(self, websocket, player_name):
		# Kiểm tra player đã tồn tại chưa (theo websocket)
		if any(p.websocket == websocket for p in self.players):
			logger.info(f"Player for websocket {websocket.remote_address} already exists.")
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
	
	async def get_opponent_move(self, data):
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
		player_name = data.get("player")
		room = self.find_room_by_playername(player_name)
		if not room:
			logger.warning(f"Player {player_name} sent move but is not in a room.")
			return {"type": "error", "message": "Bạn không ở trong phòng."}

		# Kiểm tra lượt đi
		current_player = None
		if hasattr(room, 'next_player'):
			current_player = room.next_player()
		elif hasattr(room, 'current_player'):
			current_player = room.current_player()
		if current_player != player_name:
			logger.warning(f"Player {player_name} tried to move, but it's not their turn.")
			return {"type": "error", "message": "Chưa đến lượt của bạn."}

		logger.info(f"Current turn {current_player}")
		# Tìm đối thủ
		opponent = None
		if room.player1 and room.player1.name == player_name:
			opponent = room.player2
		elif room.player2 and room.player2.name == player_name:
			opponent = room.player1

		if not opponent or not opponent.websocket:
			logger.warning(f"Player {player_name} sent move, but opponent is not connected.")
			return {"type": "error", "message": "Đối thủ không có kết nối."}

		# Chuẩn bị dữ liệu gửi cho đối thủ
		opponent_move_data = {
			"type": "opponent_move",
			"player": player_name,
			"x": data.get("x"),
			"y": data.get("y")
		}

		# Gửi nước đi cho đối thủ
		try:
			await opponent.websocket.send(json.dumps(opponent_move_data))
			# logger.info(f"Sent opponent move to {opponent.name}: {opponent_move_data}")
			logger.info(f"Đã chuyển tiếp nước đi từ {player_name} đến {opponent.name}.")
			# Đổi lượt current player trong room
			room.current_turn = 2 if room.current_turn == 1 else 1
			logger.info(f"Current turn {room.current_player()}")
			return {"type": "move_success", "message": "Nước đi đã được máy chủ ghi nhận."}
		except websockets.ConnectionClosed:
			logger.error(f"Lỗi: Không thể gửi nước đi đến {opponent.name}, kết nối đã đóng.")
			return {"type": "error", "message": "Không thể gửi nước đi, đối thủ đã ngắt kết nối."}
		except Exception as e:
			logger.error(f"Lỗi không xác định khi gửi nước đi: {e}")
			return {"type": "error", "message": "Lỗi máy chủ khi xử lý nước đi."}
	def check_challengeable(self, user_name, opponent_name):
		"""
		Kiểm tra xem hai user có thể ghép cặp thách đấu với nhau không.
		Nếu có thể, gửi thông điệp thách đấu đến opponent và chờ phản hồi (Yes/No).
		Return:
			True nếu đối thủ đồng ý, False nếu từ chối hoặc timeout/lỗi
		"""
		user = next((p for p in self.players if p.name == user_name), None)
		opponent = next((p for p in self.players if p.name == opponent_name), None)
		logger.info(f"Checking challengeable: user={user}, opponent={opponent}")
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
			logger.warning(f"Cannot create room: one or both players not found (player1: {player1}, player2: {player2})")
			return None
		room1 = self.find_room_by_playername(player1_name)
		room2 = self.find_room_by_playername(player2_name)
		# Nếu cả hai user đang ở cùng một room thì trả về thông tin room đó
		if room1 and room2 and room1 == room2:
			room = room1
			return {
				"room_id": room.room_id,
				"player1": room.player1.name,
				"player2": room.player2.name,
				"current_turn": room.current_player()
			}
		# Nếu một trong hai đã ở phòng khác thì không tạo mới
		if room1 or room2:
			logger.warning(f"Cannot create room: one or both players are already in a room (player1: {player1_name}, player2: {player2_name})")
			return None
		# Tạo room id duy nhất
		room_id = f"room_{len(self.rooms)+1}"
		room = Room(room_id=room_id, player1=player1, player2=player2)
		self.rooms.append(room)
		# Trả về thông tin room dạng dict
		return {
			"room_id": room_id,
			"player1": player1.name,
			"player2": player2.name,
			"current_turn": room.current_player()
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
	# 			logger.info(f"Sent challenge notification to {opponent_name}")
	# 			# Chờ phản hồi từ opponent (timeout 30s)
	# 			try:
	# 				response = asyncio.wait_for(opponent.websocket.recv(), timeout=30)
	# 				logger.info(f"Received challenge response from {opponent_name}: {response}")
	# 				response_data = json.loads(response)
	# 				if response_data.get("type") == "challenge_response":
	# 					return response_data
	# 				else:
	# 					logger.warning(f"Unexpected response type from {opponent_name}: {response_data}")
	# 					return None
	# 			except asyncio.TimeoutError:
	# 				logger.warning(f"Timeout waiting for challenge response from {opponent_name}")
	# 				return None
	# 		except Exception as e:
	# 			logger.warning(f"Failed to notify opponent {opponent_name}: {e}")
	# 			return None
	# 	return None
	async def start(self):
		async with websockets.serve(self.process_message,
							  		self.host,
									self.port,
									ping_interval=600,   # gửi ping mỗi 600 giây
									ping_timeout=600     # timeout nếu không nhận được pong trong 600 giây
									):
			logger.info(f"WebSocket server started on port {self.port}")
			await asyncio.Future()  # Run forever


