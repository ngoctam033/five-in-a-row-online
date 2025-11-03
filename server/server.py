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
				try:
					data = json.loads(message)
					response = None  # Sẽ được gán giá trị sau
					logging.info(f"Parsed JSON data: {data}")

					msg_type = data.get("type")
					if msg_type == "move":
						response = await self.get_opponent_move(data)
					else:
						if msg_type == "create_account":
							response = self.create_player(websocket, player_name=data.get("player"))
						elif msg_type == "get_online_players":
							response = self.get_online_players(user_name=data.get("player"))
						elif msg_type == "check_challengeable":
							response = self.check_challengeable(user_name=data.get("player"), opponent_name=data.get("opponent"))
						else:
							response = {"type": "error", "message": "Unknown message type"}
					if response:
						await websocket.send(json.dumps(response))

				except json.JSONDecodeError:
					logging.warning("Received non-JSON message: %s", message)
		except websockets.ConnectionClosed:
			logging.info("Client disconnected")
			self.players = [p for p in self.players if p.websocket != websocket]
			await websocket.close()
	
	def create_player(self, websocket, player_name):
		if any(p.websocket == websocket for p in self.players):
			logging.info(f"Player for websocket {websocket.remote_address} already exists.")
			return False
		player_id = str(websocket.remote_address)
		player = Player(player_id=player_id, name=player_name, piece_id=1, websocket=websocket)
		self.players.append(player)
		return True

	def get_online_players(self, user_name):
		return [player.name for player in self.players if player.name != user_name]

	
	async def get_opponent_move(self, data):
		player_name = data.get("player")
		
		# 1. Tìm phòng của người chơi
		room = self.find_room_by_playername(player_name)
		if not room:
			logging.warning(f"Player {player_name} sent move but is not in a room.")
			return {"type": "error", "message": "Bạn không ở trong phòng."}

		# 2. Tìm đối thủ
		opponent = None
		if room.player1 and room.player1.name == player_name:
			opponent = room.player2
		elif room.player2 and room.player2.name == player_name:
			opponent = room.player1

		if not opponent or not opponent.websocket:
			logging.warning(f"Player {player_name} sent move, but opponent is not connected.")
			return {"type": "error", "message": "Đối thủ không có kết nối."}

		# 3. Chuẩn bị dữ liệu gửi cho đối thủ
		# Client của đối thủ sẽ nhận được tin nhắn type "opponent_move"
		opponent_move_data = {
			"type": "opponent_move",
			"player": player_name,  # Người đã thực hiện nước đi
			"x": data.get("x"),
			"y": data.get("y")
		}

		# 4. Gửi nước đi cho đối thủ
		try:
			await opponent.websocket.send(json.dumps(opponent_move_data))
			logging.info(f"Đã chuyển tiếp nước đi từ {player_name} đến {opponent.name}.")
			
			# 5. Trả về thông báo thành công cho người gửi ban đầu
			return {"type": "move_success", "message": "Nước đi đã được máy chủ ghi nhận."}
		
		except websockets.ConnectionClosed:
			logging.error(f"Lỗi: Không thể gửi nước đi đến {opponent.name}, kết nối đã đóng.")
			return {"type": "error", "message": "Không thể gửi nước đi, đối thủ đã ngắt kết nối."}
		except Exception as e:
			logging.error(f"Lỗi không xác định khi gửi nước đi: {e}")
			return {"type": "error", "message": "Lỗi máy chủ khi xử lý nước đi."}

	def check_challengeable(self, user_name, opponent_name):
		user = next((p for p in self.players if p.name == user_name), None)
		opponent = next((p for p in self.players if p.name == opponent_name), None)
		logging.info(f"Checking challengeable: user={user}, opponent={opponent}")
		if not user or not opponent:
			return False
		if self.find_room_by_playername(opponent_name) is not None:
			return False
		return True
		
	def find_room_by_playername(self, playername):
		for room in self.rooms:
			if (room.player1 and room.player1.name == playername) or (room.player2 and room.player2.name == playername):
				return room
		return None
	
	async def start(self):
		async with websockets.serve(self.process_message,
							  		self.host,
									self.port,
									ping_interval=600,
									ping_timeout=600
									):
			logging.info(f"WebSocket server started on port {self.port}")
			await asyncio.Future()  # Run forever
