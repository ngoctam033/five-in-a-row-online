# login.py
import tkinter as tk
from tkinter import ttk

class LoginUI:
    def __init__(self, root, on_login_callback):
        self.root = root
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

        # ======= Nút Play =======
        play_button = ttk.Button(
            self.frame, 
            text="Play / Find Match", 
            command=self.on_play_click
        )
        play_button.pack(pady=10, ipadx=15, ipady=5)

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
        self.message_label.config(
            text=f"✅ Đã nhận được username: {username}", 
            foreground="green"
        )

        # Sau này có thể gửi username lên server
        if self.on_login_callback:
            self.on_login_callback(username)
