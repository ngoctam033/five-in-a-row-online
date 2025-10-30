import asyncio
import websockets
from game_manager import GameManager
import json
import logging
from player import Player
logging.basicConfig(level=logging.INFO)
class WebSocketServer:
	def __init__(self, host='0.0.0.0', port=9000):
		self.host = host
		self.port = port
		self.game_manager = GameManager()
		self.players = {}  # websocket -> Player mapping, dùng để lưu trữ thông tin người chơi kết nối

	async def process_message(self, websocket):
		logging.info(f"Client connected: {websocket.remote_address}")
		try:
			async for message in websocket:
				logging.info(f"Received: {message}")
				try:
					data = json.loads(message)
					if websocket not in self.players:
						self.create_player(websocket)
					if data.get("type") == "move":
						response = "This is a response for move message"
						# response = self.game_manager.handle_move_message(data)
						await websocket.send(json.dumps(response))
				except json.JSONDecodeError:
					logging.warning("Received non-JSON message:", message)
		except websockets.ConnectionClosed:
			logging.info("Client disconnected")
			# Xóa player khi client ngắt kết nối
			if websocket in self.players:
				del self.players[websocket]

	def create_player(self, websocket):
		player_id = str(websocket.remote_address)
		player = Player(player_id=player_id, name=f"Player_{player_id}", piece_id=1)
		self.players[websocket] = player
		logging.info(f"Created Player: {player}")

	async def start(self):
		async with websockets.serve(self.process_message, self.host, self.port):
			logging.info(f"WebSocket server started on port {self.port}")
			await asyncio.Future()  # Run forever
