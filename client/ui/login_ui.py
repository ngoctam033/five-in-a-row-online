import tkinter as tk
from tkinter import ttk

class LoginUI:
    def show_login_ui(self):
        self.clear_main_frame()
        self.login_frame = ttk.Frame(self.main_frame)
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="Kết nối Server", font=("Arial", 18, "bold")).pack(pady=10)

        ttk.Label(self.login_frame, text="Tên người chơi", font=("Arial", 12)).pack(pady(10,0))
        self.name_entry = ttk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.name_entry.pack(pady=5, padx=20)

        ttk.Label(self.login_frame, text="Địa chỉ IP của server", font=("Arial", 12)).pack(pady=(10,0))
        self.ip_entry = ttk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.ip_entry.insert()
        self.ip_entry.pack(pady=5, padx=20)

        ttk.Button(self.login_frame, text="Tìm trận", style='Accent.TButton', command=self.connect_to_server).pack(pady=20, ipady=5, ipadx=10)

