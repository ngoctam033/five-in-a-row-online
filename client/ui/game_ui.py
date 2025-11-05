# I - Interface Segregation: Tách interface cho từng chức năng (ở Python dùng abstract base class nếu cần)
# D - Dependency Inversion: Phụ thuộc vào abstraction, không phụ thuộc vào class cụ thể
from ui.board import Board
from ui import BoardRenderer
from player.player import Player, OnlinePlayer
import json
from network.client_network import WebSocketClient
from logic.board import BoardGameLogic
import time


# from player.aiplayer import AIPlayer
import logging
import tkinter as tk
from tkinter import messagebox
logging.basicConfig(level=logging.INFO)

class ChessboardApp:
    """Quản lý giao diện và luồng chính của ứng dụng"""
    def __init__(self, root, mode: str = "pvp",
                 ws_client: WebSocketClient = None,
                 username1: str = "Player1",
                 username2: str = "Player2",
                 current_turn: str = "1"):
        self.root = root
        self.root.title("Five in a Row")
        self.root.geometry("1000x1000")

        self.board = Board(size=10)
        self.canvas = tk.Canvas(root, width=1000, height=1000, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.renderer = BoardRenderer(self.canvas, self.board, pixel=40)
        self.board_game_logic = BoardGameLogic()
        self.is_ended = False

        self.player1 = Player(piece_id=1, username=username1)
        self.player2 = OnlinePlayer(piece_id=2, username=username2)
        self.mode = mode
        # current_turn: 1 nếu là player1, 2 nếu là player2
        if current_turn == username1 or current_turn == str(username1):
            self.current_turn = 1
        elif current_turn == username2 or current_turn == str(username2):
            self.current_turn = 2
        else:
            self.current_turn = 1  # mặc định player1 đi trước
        self.ws_client = ws_client

        # if self.mode == "local":
        #     from player.aiplayer import AIPlayer
        #     self.player2 = AIPlayer(piece_id=2)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.renderer.draw_board()
        logging.info("ChessboardApp initialized in %s mode.", self.mode)
        # --- Thời gian ván đấu ---
        self.start_time = time.time()
        self.elapsed_label = tk.Label(root, text="Thời gian: 00:00", font=("Arial", 14), fg="blue")
        self.elapsed_label.place(x=850, y=60)
        self.update_elapsed_time()
        self.listen_opponent_move()

    def listen_opponent_move(self):
        def check_move():
            # logging.info("Polling for opponent move...")
            opponent_move = None
            if self.current_turn == 2:
                opponent_move = self.ws_client.receive_opponent_move()
                # logging.info("Checking for opponent move: %s", opponent_move)
                if opponent_move:
                    self.player2_move(opponent_move)
                    self.current_turn = 1
            check_win = self.board_game_logic.is_win(self.board.grid)
            if not self.is_ended:
                if check_win == "O won":
                    tk.messagebox.showinfo("Kết quả", "Bạn đã chiến thắng!")
                    self.is_ended = True
                elif check_win == "X won":
                    tk.messagebox.showinfo("Kết quả", "Bạn đã thua!")
                    self.is_ended = True
                if self.is_ended:
                    elapsed = int(time.time() - self.start_time)
                    minutes = elapsed // 60
                    seconds = elapsed % 60
                    tk.messagebox.showinfo("Thời gian trận đấu", f"Thời lượng: {minutes} phút {seconds} giây")
            # logging.info(f"Current turn after polling: Player {self.current_turn}.")
            self.root.after(500, check_move)  # luôn gọi lại sau 500ms
        self.root.after(500, check_move)

    def on_canvas_click(self, event):
        x = event.x // self.renderer.pixel
        y = event.y // self.renderer.pixel
        # logging.info("Canvas clicked at pixel (%d, %d), board position (%d, %d).", event.x, event.y, y, x)
        logging.info("Current turn: Player %d.", self.current_turn)
        if self.current_turn == 1:
            make_move = self.player1.make_move(self.board, y, x)
            self.renderer.draw_board()
            opponent_move = self.ws_client.send_move(x, y, playername=self.player1.username)
            logging.info("Opponent move received: %s", opponent_move) 
            if opponent_move:
                if opponent_move.get("type") == "error":
                    logging.error("Error from server: %s", opponent_move.get("message"))
                else:
                    self.current_turn = 2
            check_win = self.board_game_logic.is_win(self.board.grid)
            if not self.is_ended:
                if check_win == "O won":
                    tk.messagebox.showinfo("Kết quả", "Bạn đã chiến thắng!")
                    self.is_ended = True
                elif check_win == "X won":
                    tk.messagebox.showinfo("Kết quả", "Bạn đã thua!")
                    self.is_ended = True
                if self.is_ended:
                    elapsed = int(time.time() - self.start_time)
                    minutes = elapsed // 60
                    seconds = elapsed % 60
                    tk.messagebox.showinfo("Thời gian trận đấu", f"Thời lượng: {minutes} phút {seconds} giây")
        else:
            logging.info("It's not Player 1's turn or invalid move at (%d, %d).", y, x)
            check_win = self.board_game_logic.is_win(self.board.grid)
            if not self.is_ended:
                if check_win == "O won":
                    tk.messagebox.showinfo("Kết quả", "Bạn đã chiến thắng!")
                    self.is_ended = True
                elif check_win == "X won":
                    tk.messagebox.showinfo("Kết quả", "Bạn đã thua!")
                    self.is_ended = True
        

    def player2_move(self, move):
        if self.current_turn == 2:
            if isinstance(move, str):
                move = json.loads(move)
            logging.info(f"Player 2: {self.player2.username} turn.")
            x = move["x"]
            y = move["y"]
            move = self.player2.make_move(self.board, y, x)
            if move:
                logging.info("Player 2 made a move at (%d, %d).", x, y)
                self.current_turn = 1
                self.renderer.draw_board()
                logging.info("Turn changed to Player 1.")
            else:
                logging.info("Player 2 could not make a move.")
                
    def update_elapsed_time(self):
        """Hiển thị thời gian suy nghĩ của đối thủ (player2). Đếm khi current_turn==2, reset khi current_turn==1."""
        if not self.is_ended:
            if not hasattr(self, '_opponent_think_start'):
                self._opponent_think_start = None
            if self.current_turn == 2:
                # Nếu vừa chuyển sang lượt đối thủ thì bắt đầu đếm lại
                if self._opponent_think_start is None:
                    self._opponent_think_start = time.time()
                elapsed = int(time.time() - self._opponent_think_start)
                minutes = elapsed // 60
                seconds = elapsed % 60
                self.elapsed_label.config(text=f"Thời gian: {minutes:02d}:{seconds:02d}")
            else:
                # Nếu vừa chuyển sang lượt mình thì reset label và timer
                if self._opponent_think_start is not None:
                    self.elapsed_label.config(text="Thời gian: 00:00")
                    self._opponent_think_start = None
        self.root.after(1000, self.update_elapsed_time)