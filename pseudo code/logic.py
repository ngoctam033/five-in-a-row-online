class Room:
    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.board = [[EMPTY for _ in range(15)] for _ in range(15)]
        self.current_player_id = player1.id
        self.history = []

    def apply_move(self, player, r, c):
        if self.board[r][c] != EMPTY: return False
        if player.id != self.current_player_id: return False

        self.board[r][c] = player.piece
        self.history.append((player.id, r, c))
        self.current_player_id = self.next_player(player.id)
        return True

    def check_win(self, r, c):
        piece = self.board[r][c]
        directions = [(1,0),(0,1),(1,1),(1,-1)]
        for dr,dc in directions:
            count = 1 + self.count_dir(r,c,dr,dc,piece) + self.count_dir(r,c,-dr,-dc,piece)
            if count >= 5:
                return True
        return False

    def count_dir(self, r, c, dr, dc, piece):
        i, cnt = 1, 0
        while True:
            nr, nc = r + dr*i, c + dc*i
            if not in_bounds(nr,nc) or self.board[nr][nc] != piece:
                break
            cnt += 1
            i += 1
        return cnt

    def is_full(self):
        for row in self.board:
            if EMPTY in row: return False
        return True

    def next_player(self, current_id):
        return self.players[0].id if self.players[1].id == current_id else self.players[1].id

    def notify_loser(self, winner_id):
        for p in self.players:
            if p.id != winner_id:
                p.send({'type': 'GAME_END', 'winner': winner_id, 'result': 'Thua'})
