# I - Interface Segregation: Tách interface cho từng chức năng (ở Python dùng abstract base class nếu cần)
# D - Dependency Inversion: Phụ thuộc vào abstraction, không phụ thuộc vào class cụ thể
from ui.board import Board
from ui import BoardRenderer
from player.player import Player, OnlinePlayer
import json
from network.client_network import WebSocketClient
from logic.board import BoardGameLogic
import time
from logger import logger
import tkinter as tk
from tkinter import ttk, font 

class ChessboardApp:
    """Quản lý giao diện và luồng chính của ứng dụng"""
    def __init__(self, root, mode: str = "pvp",
                 ws_client: WebSocketClient = None,
                 username1: str = "Player1",
                 username2: str = "Player2",
                 current_turn: str = "1"):
        self.root = root
        self.root.title("Five in a Row")

        self.font_title = font.Font(family="Segoe UI", size=16, weight="bold")
        self.font_body = font.Font(family="Segoe UI", size=11)
        self.font_timer = font.Font(family="Courier New", size=8, weight="bold")
        #cấu hình cửa sổ
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1) # bàn cờ
        self.root.grid_columnconfigure(1, weight=1) # thông tin 
        #tính toán tạo bàn cờ 
        self.board = Board(size=10)
        pixel_per_cell = 40 # Kích thước mỗi ô
        board_pixel_size = self.board.size * pixel_per_cell
        self.canvas = tk.Canvas(self.root, width=board_pixel_size, height=board_pixel_size, bg="white", borderwidth=0, highlightthickness=0)
        self.canvas.grid(row=0, column=0, padx=20, pady=20, sticky="nswe")

        self.info_frame = ttk.Frame(self.root, padding="20") #khung chứa toàn bộ thông tin
        self.info_frame.grid(row=0, column=1, padx=10, pady=20, sticky="nswe")

        # chứa tên player 1 và 2
        self.player1_label = ttk.Label(self.info_frame, text=f"Bạn (O): {username1}", font=self.font_body, foreground="blue")
        self.player1_label.pack(anchor="w", pady=2)
        
        self.player2_label = ttk.Label(self.info_frame, text=f"Đối thủ (X): {username2}", font=self.font_body, foreground="red")
        self.player2_label.pack(anchor="w", pady=2)

        # Trạng thái lượt đi (Sẽ cập nhật ở Bước 2)
        self.turn_label = ttk.Label(self.info_frame, text="Đang tải...", font=self.font_body, foreground="grey")
        self.turn_label.pack(anchor="w", pady=(20, 0))
        ttk.Separator(self.info_frame, orient='horizontal').pack(fill='x', pady=15)
        #Tạo đồng hồ
        ttk.Label(self.info_frame, text="THỜI GIAN", font=self.font_body).pack(anchor="w", pady=(10, 0))
        self.start_time = time.time()
        self.elapsed_label = ttk.Label(self.info_frame, text="00:00", font=self.font_timer, foreground="#333")
        self.elapsed_label.pack(anchor="w", pady=5)

        self.renderer = BoardRenderer(self.canvas, self.board, pixel=pixel_per_cell)
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
        logger.info("ChessboardApp initialized in %s mode.", self.mode)
        # --- Thời gian ván đấu ---
        # self.start_time = time.time()
        # self.elapsed_label = tk.Label(root, text="Thời gian: 00:00", font=("Arial", 14), fg="blue")
        # self.elapsed_label.place(x=850, y=60)
        self.update_elapsed_time()
        self.listen_opponent_move()
        self.elapsed_label.pack(pady=10)

    def listen_opponent_move(self):
        def check_move():
            logger.info("Polling for opponent move...")
            opponent_move = None
            if self.current_turn == 2:
                opponent_move = self.ws_client.receive_opponent_move()
                logger.info("Checking for opponent move: %s", opponent_move)
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
            logger.info(f"Current turn after polling: Player {self.current_turn}.")
            self.root.after(500, check_move)  # luôn gọi lại sau 500ms
        if not self.is_ended:
            self.root.after(500, check_move)

    def on_canvas_click(self, event):
        x = event.x // self.renderer.pixel
        y = event.y // self.renderer.pixel
        logger.info("Canvas clicked at pixel (%d, %d), board position (%d, %d).", event.x, event.y, y, x)
        logger.info("Current turn: Player %d.", self.current_turn)
        if self.current_turn == 1:
            make_move = self.player1.make_move(self.board, y, x)
            self.renderer.draw_board()
            # Log nước đi của người chơi
            # logger.info(f"Player 1 ({self.player1.username}) move: (row={y}, col={x})")
            opponent_move = self.ws_client.send_move(x, y, playername=self.player1.username)
            logger.info("Opponent move received: %s", opponent_move) 
            if opponent_move:
                if opponent_move.get("type") == "error":
                    logger.error(f"Error from server: {opponent_move.get('message')}")
                else:
                    self.current_turn = 2
            check_win = self.board_game_logic.is_win(self.board.grid)
            if not self.is_ended:
                if check_win == "O won":
                    logger.info("Player 1 wins.")
                    tk.messagebox.showinfo("Kết quả", "Bạn đã chiến thắng!")
                    self.is_ended = True
                elif check_win == "X won":
                    logger.info("Player 2 wins.")
                    tk.messagebox.showinfo("Kết quả", "Bạn đã thua!")
                    self.is_ended = True
                if self.is_ended:
                    elapsed = int(time.time() - self.start_time)
                    minutes = elapsed // 60
                    seconds = elapsed % 60
                    logger.info(f"Game ended. Total time: {minutes} phút {seconds} giây")
                    tk.messagebox.showinfo("Thời gian trận đấu", f"Thời lượng: {minutes} phút {seconds} giây")
        else:
            check_win = self.board_game_logic.is_win(self.board.grid)
            if not self.is_ended:
                if check_win == "O won":
                    logger.info("Player 1 wins.")
                    tk.messagebox.showinfo("Kết quả", "Bạn đã chiến thắng!")
                    self.is_ended = True
                elif check_win == "X won":
                    logger.info("Player 2 wins.")
                    tk.messagebox.showinfo("Kết quả", "Bạn đã thua!")
                    self.is_ended = True
        

    def player2_move(self, move):
        if self.current_turn == 2:
            if isinstance(move, str):
                move = json.loads(move)
            # logger.info(f"Player 2: {self.player2.username} turn.")
            x = move["x"]
            y = move["y"]
            move = self.player2.make_move(self.board, y, x)
            if move:
                # logger.info("Player 2 made a move at (%d, %d).", x, y)
                self.current_turn = 1
                self.renderer.draw_board()
                logger.info("Turn changed to Player 1.")
            else:
                logger.info("Player 2 could not make a move.")
                
    def update_elapsed_time(self):
        """Hiển thị thời gian suy nghĩ của đối thủ (player2). Đếm khi current_turn==2, reset khi current_turn==1."""
        if not self.is_ended:
            if not hasattr(self, '_turn_start_time'):
                self._turn_start_time = None
            if self.current_turn == 1:
                # Nếu vừa chuyển sang lượt đối thủ thì bắt đầu đếm lại
                if self._turn_start_time is None:
                    self._turn_start_time = time.time()
                elapsed = int(time.time() - self._turn_start_time)
                minutes = elapsed // 60
                seconds = elapsed % 60
                self.elapsed_label.config(text=f"{minutes:02d}:{seconds:02d}")
            else:
                # Nếu vừa chuyển sang lượt mình thì reset label và timer
                if self._turn_start_time is not None:
                    self.elapsed_label.config(text="00:00")
                    self._turn_start_time = None
        self.root.after(1000, self.update_elapsed_time)