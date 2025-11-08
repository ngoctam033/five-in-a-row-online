# Khởi tạo Client
class Client:
    def __init__(self, server_url):
        self.server_url = server_url
        self.ws = None
        self.player_id = None
        self.room_id = None
        self.board = Board(rows=15, cols=15)
        self.my_turn = False

    def connect(self):
        self.ws = WebSocket(self.server_url)
        self.ws.on_message = self.on_message
        self.ws.connect()

    # --- Đăng nhập ---
    def login(self, username):
        msg = {"type": "LOGIN", "username": username}
        self.ws.send(json.dumps(msg))

    # --- Lấy danh sách người chơi online ---
    def get_online_players(self):
        msg = {"type": "GET_ONLINE_PLAYERS"}
        self.ws.send(json.dumps(msg))

    # --- Gửi thách đấu ---
    def challenge_player(self, target_id):
        msg = {"type": "CHALLENGE_REQUEST", "target_id": target_id}
        self.ws.send(json.dumps(msg))

    # --- Chấp nhận hoặc từ chối thách đấu ---
    def respond_challenge(self, from_id, accept=True):
        msg_type = "CHALLENGE_ACCEPT" if accept else "CHALLENGE_DECLINE"
        msg = {"type": msg_type, "from": from_id}
        self.ws.send(json.dumps(msg))

    # --- Tạo hoặc tham gia phòng ---
    def create_room(self, options):
        msg = {"type": "CREATE_ROOM", "options": options}
        self.ws.send(json.dumps(msg))

    def join_room(self, room_id):
        msg = {"type": "JOIN_ROOM", "room_id": room_id}
        self.ws.send(json.dumps(msg))

    # --- Khi người chơi nhấn lên bàn cờ ---
    def on_board_click(self, r, c):
        if not self.my_turn: return
        if not self.board.is_empty(r, c): return
        msg = {"type": "MOVE", "room_id": self.room_id, "r": r, "c": c}
        self.ws.send(json.dumps(msg))

    # --- Xử lý phản hồi từ server ---
    def on_message(self, raw_msg):
        msg = json.loads(raw_msg)

        if msg['type'] == 'LOGIN_OK':
            self.player_id = msg['player_id']

        elif msg['type'] == 'ONLINE_PLAYERS_LIST':
            show_online_list(msg['players'])

        elif msg['type'] == 'CHALLENGE_INVITE':
            show_challenge_invite(msg['from'])

        elif msg['type'] == 'CHALLENGE_DECLINED':
            show_notice("Người chơi từ chối thách đấu")

        elif msg['type'] == 'GAME_START':
            self.room_id = msg['room_id']
            self.my_turn = msg['starting_player'] == self.player_id

        elif msg['type'] == 'MOVE_APPLIED':
            self.board.set_cell(msg['r'], msg['c'], msg['player_piece'])
            self.my_turn = (msg['next_player'] == self.player_id)

        elif msg['type'] == 'GAME_END':
            show_game_result(msg['winner'], msg['result'])
            reset_to_lobby()

        elif msg['type'] == 'INVALID_MOVE':
            show_error("Nước đi không hợp lệ!")
