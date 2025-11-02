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
					logging.info(f"Parsed JSON data: {data}")
					if data.get("type") == "create_account":
						response = self.create_player(websocket, player_name=data.get("player"))
					if data.get("type") == "get_online_players":
						response = self.get_online_players()
					if data.get("type") == "move":
						response = "This is a response for move message"
						response = self.get_opponent_move(data)
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

	def get_online_players(self):
		"""
		Trả về list name các người chơi đang online
		"""
		return [player.name for player in self.players]
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
	
	async def start(self):
		async with websockets.serve(self.process_message,
							  		self.host,
									self.port,
									ping_interval=60,   # gửi ping mỗi 60 giây
									ping_timeout=60     # timeout nếu không nhận được pong trong 60 giây
									):
			logging.info(f"WebSocket server started on port {self.port}")
			await asyncio.Future()  # Run forever
