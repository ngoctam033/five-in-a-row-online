class Server:
    def __init__(self):
        self.game_manager = GameManager()
        self.ws_server = WebSocketServer(on_connect=self.on_connect)

    def on_connect(self, ws):
        player = Player(ws)
        while ws.open:
            raw = ws.receive()
            msg = json.loads(raw)
            self.handle_message(player, msg)

    def handle_message(self, player, msg):
        t = msg['type']

        # --- Đăng nhập ---
        if t == 'LOGIN':
            player.name = msg['username']
            self.game_manager.add_player(player)
            player.send({'type': 'LOGIN_OK', 'player_id': player.id})

        # --- Lấy danh sách online ---
        elif t == 'GET_ONLINE_PLAYERS':
            players = self.game_manager.get_online_players()
            player.send({'type': 'ONLINE_PLAYERS_LIST', 'players': players})

        # --- Gửi lời thách đấu ---
        elif t == 'CHALLENGE_REQUEST':
            target = self.game_manager.get_player(msg['target_id'])
            if target:
                target.send({'type': 'CHALLENGE_INVITE', 'from': player.id})

        # --- Chấp nhận hoặc từ chối thách đấu ---
        elif t == 'CHALLENGE_ACCEPT':
            from_player = self.game_manager.get_player(msg['from'])
            room = self.game_manager.create_room(from_player, player)
            for p in [player, from_player]:
                p.send({'type': 'GAME_START', 'room_id': room.id,
                        'starting_player': room.current_player_id})

        elif t == 'CHALLENGE_DECLINE':
            from_player = self.game_manager.get_player(msg['from'])
            from_player.send({'type': 'CHALLENGE_DECLINED'})

        # --- Tạo / tham gia phòng (thủ công) ---
        elif t == 'CREATE_ROOM':
            room = self.game_manager.create_room(player, msg.get('options'))
            player.send({'type': 'ROOM_CREATED', 'room_id': room.id})

        elif t == 'JOIN_ROOM':
            room = self.game_manager.join_room(player, msg['room_id'])
            broadcast(room, {'type': 'PLAYER_JOINED', 'player': player.summary()})

        # --- Nước đi ---
        elif t == 'MOVE':
            room = self.game_manager.find_room(msg['room_id'])
            success = room.apply_move(player, msg['r'], msg['c'])
            if success:
                broadcast(room, {
                    'type': 'MOVE_APPLIED',
                    'r': msg['r'], 'c': msg['c'],
                    'player_piece': player.piece,
                    'next_player': room.current_player_id
                })
                if room.check_win(msg['r'], msg['c']):
                    broadcast(room, {
                        'type': 'GAME_END',
                        'winner': player.id,
                        'result': 'Thắng'
                    })
                    room.notify_loser(player.id)
                elif room.is_full():
                    broadcast(room, {
                        'type': 'GAME_END',
                        'winner': None,
                        'result': 'Hòa'
                    })
            else:
                player.send({'type': 'INVALID_MOVE'})
