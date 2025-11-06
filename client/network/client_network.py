import websocket
from logger import logger
import json
import time
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
			logger.info(f"Connecting to server at {self.uri}...")
			self.connection = websocket.create_connection(self.uri)
			if self.connection:
				self.connected = True
				logger.info("Connected to server.")
				sent_success = self.send("Hello from client!")
				if sent_success:
					logger.info("Initial hello message sent successfully.")
				else:
					logger.warning("Failed to send initial hello message.")
			else:
				print("Failed to connect to server: No connection object.")
		except Exception as e:
			print(f"Failed to connect to server: {e}")
			
	def send(self, message):
		"""
		Gửi message từ client đến server,
		trả về True nếu gửi thành công,
		False nếu lỗi hoặc không có kết nối
		"""
		if self.connection:
			try:
				self.connection.send(message)
				logger.info(f"Sent message: {message}")
				return True
			except Exception as e:
				# logger.warning(f"Error sending message: {e}")
				return False
		else:
			logger.warning("No connection to send message.")
			return False

	def receive_once(self, timeout=0.1):
		"""
		Nhận một tin nhắn từ server (dùng khi không có callback), không blocking lâu.
		Nếu không có dữ liệu trong timeout giây thì trả về None.
		"""
		if self.connection:
			oldtimeout = self.connection.gettimeout() if hasattr(self.connection, 'gettimeout') else None
			try:
				self.connection.settimeout(timeout)
				response = self.connection.recv()
				# logger.info(f"Received message: {response}")
				return response
			except Exception as e:
				# logger.warning(f"Error receiving message: {e}")
				return None
			finally:
				if oldtimeout is not None:
					self.connection.settimeout(oldtimeout)
		else:
			logger.warning("No connection to receive message.")
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
				logger.warning("Failed to send move data.")
				return None
			response = self.receive_once()
			return json.loads(response)
		else:
			logger.warning("No connection to send move.")
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
			logger.warning("No active connection to send account creation request.")
			return False
		
		if not playername:
			logger.warning("Player name is empty - cannot send account creation request.")
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
					logger.info(f"Server response after account creation: {response}")
				else:
					logger.warning("No response received from server after account creation request.")
				logger.info(f"Account creation request sent: {account_data}")
				return True
			else:
				logger.warning("Failed to send account creation message.")
				return False
		except Exception as e:
			logger.warning(f"Error sending account creation request: {e}")

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
			logger.warning("No active connection to request online players.")
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
					logger.info(f"Received online players list: {response}")
					players_list = json.loads(response)
					return players_list
				else:
					logger.warning("No response received from server for online players request.")
					return None
			else:
				logger.warning("Failed to send online players request.")
				return None
		except Exception as e:
			logger.warning(f"Error requesting online players: {e}")
			return None
		
	def send_check_challengeable(self, user_name: str, opponent_name: str) -> bool:
		"""
		Gửi yêu cầu kiểm tra xem user_name và opponent_name có thể thách đấu với nhau không.
		Args:
			user_name (str): tên người chơi gửi yêu cầu
			opponent_name (str): tên người chơi bị thách đấu
		Return:
			True nếu server xác nhận có thể thách đấu, False nếu không hoặc lỗi.
		"""
		if not self.connection:
			logger.warning("No active connection to check challengeable.")
			return False

		request_data = {
			"type": "check_challengeable",
			"player": user_name,
			"opponent": opponent_name
		}

		try:
			message = json.dumps(request_data)
			sent_success = self.send(message)

			if sent_success:
				response = self.receive_once()
				if response:
					logger.info(f"Received challengeable check response: {response}")
					result = json.loads(response)
					# True/False
					return result
				else:
					logger.warning("No response received from server for challengeable check.")
					return None
			else:
				logger.warning("Failed to send challengeable check request.")
				return None
		except Exception as e:
			logger.warning(f"Error requesting challengeable check: {e}")
			return None
	
	def receive_opponent_move(self):
		"""
		Nhận message về nước đi của đối thủ từ server.
		Return:
			dict: thông tin nước đi của đối thủ nếu nhận được, None nếu lỗi hoặc không có kết nối
		"""
		if not self.connection:
			logger.warning("No connection to receive opponent move.")
			return None
		try:
			message = self.receive_once()
			if message is None:
				return None
			data = json.loads(message)
			if isinstance(data, dict) and data.get("type") == "opponent_move":
				logger.info(f"Received opponent move: {data}")
				return data
			else:
				logger.info(f"Received non-opponent move message: {data}")
				return None
		except Exception as e:
			logger.warning(f"Error receiving opponent move: {e}")
			return None
	
	def send_create_room(self, user_name: str, opponent_name: str):
		"""
		Gửi yêu cầu tạo phòng với 2 người chơi lên server.
		Args:
			user_name (str): tên người chơi gửi yêu cầu
			opponent_name (str): tên đối thủ
		Return:
			Thông tin phòng từ server nếu thành công, None nếu lỗi hoặc không có kết nối
		"""
		if not self.connection:
			logger.warning("No active connection to create room.")
			return None

		request_data = {
			"type": "create_room",
			"player": user_name,
			"opponent": opponent_name
		}

		try:
			message = json.dumps(request_data)
			sent_success = self.send(message)

			if sent_success:
				response = self.receive_once()
				if response:
					logger.info(f"Received create room response: {response}")
					room_info = json.loads(response)
					return room_info
				else:
					logger.warning("No response received from server for create room request.")
					return None
			else:
				logger.warning("Failed to send create room request.")
				return None
		except Exception as e:
			logger.warning(f"Error requesting create room: {e}")
			return None
		

	def send_winner_info(self, winner_name: str):
		"""
		Gửi thông tin người chiến thắng lên server.
		Args:
			room_id (str): ID của phòng chơi
			winner_name (str): tên người chiến thắng
		Return:
			Phản hồi từ server nếu thành công, None nếu lỗi hoặc không có kết nối
		"""
		if not self.connection:
			logger.warning("No active connection to send winner info.")
			return None

		request_data = {
			"type": "winner_info",
			"winner": winner_name
		}

		try:
			message = json.dumps(request_data)
			sent_success = self.send(message)

			if sent_success:
				response = self.receive_once()
				if response:
					logger.info(f"Received winner info response: {response}")
					result = json.loads(response)
					return result
				else:
					logger.warning("No response received from server for winner info request.")
					return None
			else:
				logger.warning("Failed to send winner info request.")
				return None
		except Exception as e:
			logger.warning(f"Error requesting winner info: {e}")
			return None
		
	def receive_challenge_request(self):
		"""
		Nhận message về lời thách đấu từ server.
		Return:
			dict: thông tin thách đấu nếu nhận được, None nếu lỗi hoặc không có kết nối
		"""
		if not self.connection:
			logger.warning("No connection to receive challenge request.")
			return None
		try:
			message = self.receive_once()
			if message is None:
				return None
			data = json.loads(message)
			if isinstance(data, dict) and data.get("type") == "challenge_request":
				logger.info(f"Received challenge request: {data}")
				return data
			else:
				logger.info(f"Received non-challenge request message: {data}")
				return None
		except Exception as e:
			logger.warning(f"Error receiving challenge request: {e}")
			return None
		
	def wait_for_challenge_response(self, user_name, opponent_name, timeout=30):
		"""
		Chờ phản hồi thách đấu từ server trong tối đa timeout giây.
		Nếu đối thủ đồng ý, trả về True, nếu từ chối hoặc hết thời gian trả về False.
		"""
		start_time = time.time()
		while time.time() - start_time <= timeout:
			response = self.receive_once(timeout=0.5)
			if response:
				try:
					data = json.loads(response)
					if data.get("type") == "challenge_response":
						return bool(data.get("accept", False))
				except Exception as e:
					logger.warning(f"Error parsing challenge response: {e}")
			time.sleep(0.1)  # tránh busy loop
		logger.info("Challenge response timed out.")
		return False