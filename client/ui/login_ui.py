# login.py
import tkinter as tk
from tkinter import ttk
import threading
import json
from ui.game_ui import ChessboardApp
from network.client_network import WebSocketClient
import logging
logging.basicConfig(level=logging.INFO)

class LoginUI:
    def __init__(self, root, ws_client: WebSocketClient,
                 on_login_callback):
        self.root = root
        self.ws_client = ws_client
        self.on_login_callback = on_login_callback

        # ======= Cấu hình cửa sổ =======
        self.window_width = 600
        self.window_height = 400
        self.center_window()  # Gọi hàm căn giữa cửa sổ
        self.root.resizable(False, False)  # Không cho resize
        self.root.configure(bg="#f8f9fa")

        # ======= Tạo khung chính =======
        self.frame = ttk.Frame(root, padding=20)
        self.frame.pack(expand=True)

        # ======= Logo + tiêu đề =======
        ttk.Label(
            self.frame, 
            text="🎮 CỜ CARO ONLINE 🎮", 
            font=("Arial", 26, "bold"), 
            foreground="#007bff"
        ).pack(pady=(20, 10))

        ttk.Label(
            self.frame, 
            text="Nhập tên người chơi:", 
            font=("Arial", 14)
        ).pack(pady=(20, 0))

        # ======= Ô nhập tên =======
        self.name_entry = ttk.Entry(self.frame, font=("Arial", 13), width=35)
        self.name_entry.pack(pady=10)
        self.name_entry.focus()

        # ======= Vùng hiển thị thông báo =======
        self.message_label = ttk.Label(
            self.frame, 
            text="", 
            font=("Arial", 12), 
            foreground="green"
        )
        self.message_label.pack(pady=15)
        # +++
        # gửi thông tin username để tạo tài khoản đến server
        find_match_button = ttk.Button(
            self.frame, 
            text="Find Match", 
            command=self.on_find_match_click
        )
        find_match_button.pack(pady=10, ipadx=15, ipady=5)
        # ======= Nút Play =======
        # play_button = ttk.Button(
        #     self.frame, 
        #     text="Play / Find Match", 
        #     command=self.on_play_click
        # )
        # play_button.pack(pady=10, ipadx=15, ipady=5)

    def on_find_match_click(self):
        username = self.name_entry.get().strip()
        if not self.ws_client:
            self.message_label.config(text="❌ Không có kết nối server.", foreground="red")
            return
        self.ws_client.send_create_account(username)
        online_players = self.get_online_players(username)
        if not online_players:
            self.message_label.config(text="❌ Không lấy được danh sách user online.", foreground="red")
            return
        self.show_online_players_window(online_players)

    def get_online_players(self, username):
        return self.ws_client.send_get_online_players(username)

    def show_online_players_window(self, online_players):
        top = tk.Toplevel(self.root)
        top.title("Danh sách người chơi online")
        top.geometry("400x400")
        label = ttk.Label(top, text="Người chơi đang online:", font=("Arial", 14, "bold"))
        label.pack(pady=10)
        self.selected_opponent = None
        listbox = tk.Listbox(top, font=("Arial", 13), width=30, height=15, selectmode=tk.SINGLE)
        for user in online_players:
            listbox.insert(tk.END, user)
        listbox.pack(pady=10)
        listbox.bind('<<ListboxSelect>>', lambda event: self.handle_opponent_selection(listbox))

    def handle_opponent_selection(self, listbox):
        selection = listbox.curselection()
        if selection:
            idx = selection[0]
            opponent_name = listbox.get(idx)
            self.selected_opponent = opponent_name
            # Tô đậm vùng chọn
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(idx)
            listbox.activate(idx)
            self.check_and_start_challenge(opponent_name)

    def check_and_start_challenge(self, opponent_name):
        user_name = self.name_entry.get().strip()
        challengeable = self.ws_client.send_check_challengeable(user_name, opponent_name)
        print(f"Challengeable ({user_name} vs {opponent_name}): {challengeable}")
        if challengeable:
            self.selected_opponent = opponent_name

            sended = self.ws_client.send_create_room(user_name, opponent_name)
            if self.on_login_callback:
                self.on_login_callback(user_name, opponent_name, sended["current_turn"])
            # logging.info(f"Create room request sent: {sended}")
        else:
            self.message_label.config(text=f"❌ Không thể thách đấu với {opponent_name}.", foreground="red")
            self.selected_opponent = None


    # ------------------------------------
    def center_window(self):
        """Căn giữa cửa sổ trên màn hình."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (self.window_width / 2))
        y = int((screen_height / 2) - (self.window_height / 2))
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")

    # ------------------------------------
    def on_play_click(self):
        username = self.name_entry.get().strip()
        if not username:
            self.message_label.config(text="⚠️ Vui lòng nhập tên!", foreground="red")
            return
        # Nếu đã chọn opponent và challengeable thì bắt đầu game
        if hasattr(self, 'selected_opponent') and self.selected_opponent:
            self.message_label.config(text=f"✅ Bắt đầu trận đấu với {self.selected_opponent}", foreground="green")
            if self.on_login_callback:
                self.on_login_callback(username, self.selected_opponent)
            # Có thể truyền thêm opponent cho ChessboardApp nếu cần
        else:
            self.message_label.config(text="⚠️ Vui lòng chọn đối thủ hợp lệ!", foreground="red")
