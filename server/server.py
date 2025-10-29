import asyncio
import websockets
from game_manager import GameManager
import json
class WebSocketServer:
	def __init__(self, host='0.0.0.0', port=9000):
		self.host = host
		self.port = port
		self.game_manager = GameManager()

	async def process_message(self, websocket):
		print(f"Client connected: {websocket.remote_address}")
		try:
			async for message in websocket:
				print(f"Received: {message}")
				await websocket.send(f"Echo: {message}")
				# Xử lý thông điệp từ client
				data = json.loads(message)
				if data.get("type") == "move":
					response = self.game_manager.handle_move_message(data)
				
		except websockets.ConnectionClosed:
			print("Client disconnected")

	async def start(self):
		async with websockets.serve(self.process_message, self.host, self.port):
			print(f"WebSocket server started on port {self.port}")
			await asyncio.Future()  # Run forever
