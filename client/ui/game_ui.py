import tkinter as tk
from tkinter import ttk, messagebox

class GameScreen:
    def setup_game_view(self):
        self.clear_main_frame()

        #frame chua thong tin va ban co
        game_container = ttk.Frame(self.main_frame)
        game_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        #thanh trang thai o tren
        self.status_bar = ttk.Label(game_container, text='...', font=("Arial", 14, "italic"), anchor=tk.CENTER)
        self.status_bar.pack(pady=(0,10), fill=tk.X)

        #tich hop giao dien ban co
        self.gameboard = GameBoardUI(game_container, size=25, cell_size=28)
        self.gameboard.move_callback = self.on_board_click

    def start_timer(self, remaining_time):
        self.stop_timer()
        self.remaining_time = remaining_time
        self.update_timer()

    # def update_timer():

    # def stop_timer():

    # def handle_game_result():

    # def handle_game_result_offline():

    # def show_play_again_dialog():