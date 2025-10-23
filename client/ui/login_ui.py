import tkinter as tk
from tkinter import ttk

class LoginUI(ttk.Frame):
    def __init__(self, parent, on_connect):
        super().__init__(parent)
        self.on_connect = on_connect

        ttk.Label(self, text="Nhập tên người chơi: ").pack(pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5)

        ttk.Label(self, text="Nhập IP Server:").pack(pady=5)
        self.ip_entry = ttk.Entry(self)
        self.ip_entry.pack(pady=5)

        ttk.Button(self, text="Kết nối", command=self._on_connect_pressed).pack(pady=10)
    def _on_connect_pressed(self): 
        username = self.username_entry.get().strip()
        ip = self.ip_entry.get().strip()
        if not username or not ip:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tên và IP server")
            return
        # Gọi callback cho UI chính (GameUI)
        self.on_connect(username, ip)

