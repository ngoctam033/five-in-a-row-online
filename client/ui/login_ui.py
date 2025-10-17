import tkinter as tk
from tkinter import ttk
class LoginUI:
    def __init__(self, root):
        self.root = root
        # Tạo một frame chính để chứa các giao diện khác nhau
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Cấu hình style cho các widget của ttk
        self.style = ttk.Style()
        self.style.configure('Accent.TButton', font=('Arial', 14))

    def clear_main_frame(self):
        """Xóa tất cả widget con trong main_frame."""
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def create_mode_selection_ui(self):
        self.clear_main_frame()
        self.mode_selection_frame = ttk.Frame(self.main_frame)
        self.mode_selection_frame.pack(expand=True)

        ttk.Label(self.mode_selection_frame, text="CHỌN CHẾ ĐỘ CHƠI", font=("Arial", 24, "bold")).pack(pady=20)
        ttk.Button(self.mode_selection_frame, text="Chơi Online", style='Accent.TButton', command=self.show_login_ui).pack(pady=10, ipady=5, ipadx=10)
        ttk.Button(self.mode_selection_frame, text="Chơi Offline (Với Máy)", command=self.start_offline_game).pack(pady=10, ipady=5, ipadx=10)

         # Cấu hình style cho nút nhấn
        s = ttk.Style()
        s.configure('Accent.TButton', font=('Arial', 14), background='#3498DB', foreground='white')
        s.map('Accent.TButton', background=[('active', '#2980B9')])
    
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
    
    def run(self):
        """Run the demo application"""
        self.mainloop()
