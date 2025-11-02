import websocket
import logging
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

	def _init_ws(self):
		try:
			logging.info(f"Connecting to server at {self.uri}...")
			self.connection = websocket.create_connection(self.uri)
			if self.connection:
				self.connected = True
				logging.info("Connected to server.")
				sent_success = self.send("Hello from client!")
				if sent_success:
					logging.info("Initial hello message sent successfully.")
				else:
					logging.warning("Failed to send initial hello message.")
			else:
				print("Failed to connect to server: No connection object.")
		except Exception as e:
			print(f"Failed to connect to server: {e}")
			
	def send(self, message):
		"""Gửi message từ client đến server, trả về True nếu gửi thành công, False nếu lỗi hoặc không có kết nối"""
		if self.connection:
			try:
				# await self.connection.send(message)
				self.connection.send(message)
				logging.info(f"Sent message: {message}")
				return True
			except Exception as e:
				logging.warning(f"Error sending message: {e}")
				return False
		else:
			logging.warning("No connection to send message.")
			return False

	def receive_once(self):
		"""Nhận một tin nhắn từ server (dùng khi không có callback)"""
		if self.connection:
			try:
				response = self.connection.recv()
				# logging.info(f"Received message: {response}")
				return response
			except Exception as e:
				logging.warning(f"Error receiving message: {e}")
				return None
		else:
			logging.warning("No connection to receive message.")
			return None
	
	def send_move(self, x, y, playername):
		"""
		Gửi thông tin nước đi lên server.
		Args:
			x (int): Tọa độ cột
			y (int): Tọa độ hàng
			player_name (str): Tên người chơi thực hiện nước đi
		Return:
			response từ server nếu thành công, None nếu lỗi hoặc không có kết nối
		"""
		if self.connection:
			move_data = {
				"type": "move",
				"player": playername,
				"x": x,
				"y": y
			}
			message = json.dumps(move_data)
			sended = self.send(message)
			if not sended:
				logging.warning("Failed to send move data.")
				return None
			response = self.receive_once()
			return response
		else:
			logging.warning("No connection to send move.")
			return None

	def send_create_account(self, playername: str) -> bool:
		"""
		Gửi thông tin tạo tài khoản player lên server.
		Args:
			playername (str): Tên người chơi
		Return:
			True: Nếu gửi thành công
			False: Nếu có lỗi hoặc không có kết nối
		Tham khảo Hàm send_move
		Cấu trúc JSON gửi đi
		account_data = {
				"type": "create_account",
				"player": playername
			}
		"""
		if not self.connection:
			logging.warning("No active connection to send account creation request.")
			return False
		
		if not playername:
			logging.warning("Player name is empty - cannot send account creation request.")
			return False

		account_data = {
			"type": "create_account",
			"player": playername
		}

		try:
			message = json.dumps(account_data)
			sent_success = self.send(message)

			if sent_success: 
				response = self.receive_once()
				if response:
					logging.info(f"Server response after account creation: {response}")
				else:
					logging.warning("No response received from server after account creation request.")
				logging.info(f"Account creation request sent: {account_data}")
				return True
			else:
				logging.warning("Failed to send account creation message.")
				return False
		except Exception as e:
			logging.warning(f"Error sending account creation request: {e}")

	def send_get_online_players(self, player_name: str):
		"""
		Gửi yêu cầu lấy danh sách các player đang online từ server.
		Return:
			Danh sách player online nếu thành công, None nếu lỗi hoặc không có kết nối
		Tham khảo Hàm send_move
		Cấu trúc JSON gửi đi
		request_data = {
			"type": "get_online_players"
		}
		"""
		if not self.connection:
			logging.warning("No active connection to request online players.")
			return None

		request_data = {
			"type": "get_online_players",
			"player": player_name
		}

		try:
			message = json.dumps(request_data)
			sent_success = self.send(message)

			if sent_success:
				response = self.receive_once()
				if response:
					logging.info(f"Received online players list: {response}")
					players_list = json.loads(response)
					return players_list
				else:
					logging.warning("No response received from server for online players request.")
					return None
			else:
				logging.warning("Failed to send online players request.")
				return None
		except Exception as e:
			logging.warning(f"Error requesting online players: {e}")
			return None