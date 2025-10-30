# I - Interface Segregation: Tách interface cho từng chức năng (ở Python dùng abstract base class nếu cần)
# D - Dependency Inversion: Phụ thuộc vào abstraction, không phụ thuộc vào class cụ thể
from ui.board import Board
from ui import BoardRenderer
from player.player import Player, OnlinePlayer
import asyncio
from network.client_network import WebSocketClient


# from player.aiplayer import AIPlayer
import logging
import tkinter as tk
logging.basicConfig(level=logging.INFO)

class ChessboardApp:
    """Quản lý giao diện và luồng chính của ứng dụng"""
    def __init__(self, root, mode: str = "pvp", ws_client: WebSocketClient = None):
        self.root = root
        self.root.title("Five in a Row")
        self.root.geometry("1000x1000")

        self.board = Board(size=25)
        self.canvas = tk.Canvas(root, width=1000, height=1000, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.renderer = BoardRenderer(self.canvas, self.board, pixel=40)

        self.player1 = Player(piece_id=1)
        self.player2 = OnlinePlayer(piece_id=2)
        self.mode = mode
        self.current_turn = 1  # 1: người chơi 1, 2: người chơi 2 hoặc AI
        self.ws_client = ws_client

        if self.mode == "local":
            from player.aiplayer import AIPlayer
            self.player2 = AIPlayer(piece_id=2)

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.renderer.draw_board()
        logging.info("ChessboardApp initialized in %s mode.", self.mode)

    def on_canvas_click(self, event):
        x = event.x // self.renderer.pixel
        y = event.y // self.renderer.pixel
        logging.info("Canvas clicked at pixel (%d, %d), board position (%d, %d).", event.x, event.y, y, x)
        if self.current_turn == 1 and self.player1.make_move(self.board, y, x):
            self.current_turn = 2
            self.renderer.draw_board()
            logging.info("Player 1 made a move at (%d, %d).", y, x)
            # Gửi thông tin nước đi lên server qua websocket
            if self.ws_client:
                self.ws_client.send_move(x, y, playername="Player1")
            # self.root.after(500, self.player2_move)
        else:
            logging.info("It's not Player 1's turn or invalid move at (%d, %d).", y, x)

    def player2_move(self):
        if self.current_turn == 2:
            logging.info("Player 2's turn.")
            move = self.player2.make_move(self.board)
            if move:
                logging.info("Player 2 made a move at (%d, %d).", move[0], move[1])
                self.current_turn = 1
                self.renderer.draw_board()
                logging.info("Turn changed to Player 1.")
            else:
                logging.info("Player 2 could not make a move.")