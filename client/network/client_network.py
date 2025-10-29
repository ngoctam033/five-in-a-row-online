import asyncio
import websockets
import logging
import asyncio
import threading
import json
class WebSocketClient:
	"""Quản lý kết nối, giao tiếp, trạng thái và luồng với server qua websocket"""
	def __init__(self, uri, on_message=None):
		self.uri = uri
		self.connection = None
		self.on_message = on_message
		self._receive_task = None
		self.connected = False
		# Khởi tạo và kết nối ngay khi tạo đối tượng

	async def _init_ws(self):
		try:
			logging.info(f"Connecting to server at {self.uri}...")
			self.connection = await websockets.connect(self.uri)
			if self.connection:
				self.connected = True
				logging.info("Connected to server.")
				sent_success = await self.send("Hello from client!")
				if sent_success:
					logging.info("Initial hello message sent successfully.")
					# nhận lại phản hồi từ server
					response = await self.receive_once()
					print("Server response:", response)
					# Bắt đầu luồng nhận tin nhắn nếu có callback
					if self.on_message:
						loop = asyncio.get_event_loop()
						self._receive_task = loop.create_task(self._receive_loop())
				else:
					logging.warning("Failed to send initial hello message.")
			else:
				print("Failed to connect to server: No connection object.")
		except Exception as e:
			print(f"Failed to connect to server: {e}")
			
	async def send(self, message):
		"""Gửi message từ client đến server, trả về True nếu gửi thành công, False nếu lỗi hoặc không có kết nối"""
		if self.connection:
			try:
				await self.connection.send(message)
				logging.info(f"Sent message: {message}")
				return True
			except Exception as e:
				logging.warning(f"Error sending message: {e}")
				return False
		else:
			logging.warning("No connection to send message.")
			return False

	async def receive_once(self):
		"""Nhận một tin nhắn từ server (dùng khi không có callback)"""
		if self.connection:
			try:
				response = await self.connection.recv()
				logging.info(f"Received message: {response}")
				return response
			except Exception as e:
				logging.warning(f"Error receiving message: {e}")
				return None
		else:
			logging.warning("No connection to receive message.")
			return None
	
	async def send_move(self, x, y, player=1):
		"""
        Gửi thông tin nước đi lên server.
        Args:
            x (int): Tọa độ cột
            y (int): Tọa độ hàng
            player (int): Người chơi (mặc định 1)
        """
		if self.connection:
			move_data = {
						"type": "move",
						"player": player,
						"x": x,
						"y": y
						}
			message = json.dumps(move_data)
			await self.send(message)
			response = await self.receive_once()
			if response:
				print("Server response:", response)
			logging.info(f"Sent move to server: {move_data}")
		else:
			logging.warning("No connection to send move.")