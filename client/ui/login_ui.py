import tkinter as tk
from tkinter import messagebox, font
from PIL import Image, ImageTk 
import os

class LoginWindow:
    """
    Giao diện Đăng nhập Tối giản - Phối màu "Gỗ và Giấy"
    """
    
    # --- Tùy chỉnh thiết kế (Bảng màu mới) ---
    BG_COLOR = "#F0EAD6"           # Màu nền (Beige/Vải lanh)
    CARD_COLOR = "#FAF8F0"         # Màu thẻ (Giấy Parchement/Kem)
    BUTTON_BG_COLOR = "#855E42"    # Màu nút (Gỗ Óc chó)
    BUTTON_ACTIVE_BG_COLOR = "#6F4E37" # Màu nút khi hover (Gỗ đậm hơn)
    TEXT_COLOR_DARK = "#4A3B30"    # Màu chữ chính (Nâu đậm)
    TEXT_COLOR_LIGHT = "#8A796D"   # Màu chữ phụ (Nâu-Xám)
    FONT_FAMILY = "Segoe UI"
    # --- Kết thúc tùy chỉnh ---

    def __init__(self, root, on_login_success):
        self.root = root
        self.on_login_success = on_login_success 

        self.main_canvas = tk.Canvas(root, bg=self.BG_COLOR, highlightthickness=0)
        self.main_canvas.pack(fill=tk.BOTH, expand=True)

        self.login_frame = tk.Frame(self.main_canvas, bg=self.CARD_COLOR, 
                                     bd=1, relief=tk.SOLID)
        self.login_frame.config(highlightbackground="#DCD3C0", highlightthickness=1) # Viền màu be
        
        self._create_widgets()

        # Đặt tương đối, tự động co dãn
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER) 

    def _create_widgets(self):
        
        # --- Tiêu đề Game "CỜ CARO" ---
        title_font = font.Font(family=self.FONT_FAMILY, size=48, weight="bold")
        lbl_title = tk.Label(
            self.login_frame, 
            text="CỜ CARO",
            font=title_font, 
            fg=self.TEXT_COLOR_DARK, 
            bg=self.CARD_COLOR
        )
        lbl_title.pack(pady=(80, 60), padx=100) # Thêm padding X

        # --- Nhập tên người chơi ---
        label_font = font.Font(family=self.FONT_FAMILY, size=16)
        lbl_username = tk.Label(
            self.login_frame, 
            text="Nhập tên của bạn",
            font=label_font, 
            bg=self.CARD_COLOR,
            fg=self.TEXT_COLOR_LIGHT
        )
        lbl_username.pack(pady=(10, 10))

        # --- Khung bọc Entry ---
        entry_font = font.Font(family=self.FONT_FAMILY, size=18)
        entry_frame = tk.Frame(self.login_frame, bg=self.CARD_COLOR, relief=tk.SOLID, bd=1)
        entry_frame.config(highlightbackground="#C0B0A0", highlightthickness=1) # Viền nâu nhạt
        
        self.ent_username = tk.Entry(
            entry_frame, 
            font=entry_font, 
            relief=tk.FLAT, # Bỏ viền
            bd=0,
            justify=tk.CENTER,
            fg=self.TEXT_COLOR_DARK,
            insertbackground=self.TEXT_COLOR_DARK # Màu con trỏ
        )
        self.ent_username.pack(ipady=12, fill=tk.X, padx=5)
        
        entry_frame.pack(pady=(0, 60), padx=100, fill=tk.X) # Đồng bộ padding X
        self.ent_username.focus_set()

        # --- Nút "Bắt Đầu" ---
        button_font = font.Font(family=self.FONT_FAMILY, size=20, weight="bold")
        self.btn_start = tk.Button(
            self.login_frame, 
            text="Bắt Đầu",
            font=button_font, 
            bg=self.BUTTON_BG_COLOR,
            fg="#FFFFFF", # Chữ trắng nổi bật trên nền gỗ
            relief=tk.FLAT, 
            pady=15,
            activebackground=self.BUTTON_ACTIVE_BG_COLOR,
            activeforeground="#FFFFFF",
            cursor="hand2",
            command=self.handle_start_click
        )
        self.btn_start.pack(pady=(20, 100), padx=100, fill=tk.X) # Đồng bộ padding X
        self.btn_start.bind("<Enter>", self._on_button_enter)
        self.btn_start.bind("<Leave>", self._on_button_leave)

    # --- Các hàm xử lý sự kiện ---

    def _on_button_enter(self, event):
        self.btn_start.config(bg=self.BUTTON_ACTIVE_BG_COLOR)

    def _on_button_leave(self, event):
        self.btn_start.config(bg=self.BUTTON_BG_COLOR)

    def handle_start_click(self):
        username = self.ent_username.get().strip()
        
        if not username:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên của bạn.")
            return

        messagebox.showinfo(
            "Đang kết nối",
            f"Chào mừng, {username}!\nĐang tìm trận đấu..."
        )

        if self.on_login_success:
            self.on_login_success(username) 
            
    def destroy(self):
        self.main_canvas.destroy()