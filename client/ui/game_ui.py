import tkinter as tk
from tkinter import ttk, messagebox

class GameUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Five in a Row")
        self.root.configure(bg="#F0F0F0") # Màu nền cho cửa sổ
        # Sử dụng theme 'clam' để có giao diện hiện đại hơn
        style = ttk.Style()
        style.theme_use('clam')
        # Khởi tạo logic game và mạng
        self.game = Game()
        self.network = NetworkManager(queue.Queue())
        self.message_queue = self.network.message_queue
        # Trạng thái game
        self.my_turn = False
        self.my_piece_id = 0
        self.username = ""
        self.game_started = False
        self.timer_id = None
        # Frame chính
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_mode_selection_ui()


    # ----- chọn chế độ -------
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


    # ------ kết nối -------
    def show_login_ui(self):
        self.clear_main_frame()
        self.login_frame = ttk.Frame(self.main_frame)
        self.login_frame.pack(expand=True)

        ttk.Label(self.login_frame, text="KẾT NỐI SERVER", font=("Arial", 18, "bold")).pack(pady=10)

        ttk.Label(self.login_frame, text="Tên người chơi:", font=("Arial", 12)).pack(pady=(10,0))
        self.name_entry = ttk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.name_entry.pack(pady=5, padx=20)

        ttk.Label(self.login_frame, text="Địa chỉ IP của Server:", font=("Arial", 12)).pack(pady=(10,0))
        self.ip_entry = ttk.Entry(self.login_frame, font=("Arial", 12), width=30)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(pady=5, padx=20)

    def connect_to_server(self):
        self.username = self.name_entry.get().strip()
        ip = self.ip_entry.get().strip()
        if not self.username or not ip:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên và địa chỉ IP.")
            return
        
        if self.network.connect(ip, 13000):
            self.network.send_message(f"LOGIN|{self.username}")
            self.root.after(100, self.process_messages)
            self.show_waiting_screen()
        else:
            messagebox.showerror("Lỗi kết nối", f"Không thể kết nối đến {ip}:13000.")


    # ------ Chế độ offline ------
    def start_offline_game(self):
        self.root.title("Five in a Row - Chơi với máy")
        self.setup_game_view()
        self.status_bar.config(text="Chế độ Offline: Bạn đi trước (Quân Đen).")
    
    # ------- Màn chờ --------
#     def show_waiting_screen(self): ...

    # ----- giao diện chính -------
    def setup_game_view(self):
        self.clear_main_frame()
        # Frame chứa thông tin và bàn cờ
        game_container = ttk.Frame(self.main_frame)
        game_container.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Thanh trạng thái ở trên
        self.status_bar = ttk.Label(game_container, text="...", font=("Arial", 14, "italic"), anchor=tk.CENTER)
        self.status_bar.pack(pady=(0, 10), fill=tk.X)
        
        # Tích hợp giao diện bàn cờ mới
        self.game_board = GameBoardUI(game_container, size=25, cell_size=28)
        self.game_board.move_callback = self.on_board_click

    # ------ xử lý nước đi -------
    def on_board_click(self, row, col):
        if self.game.board[row][col] != 0: return

        if self.game_started: # online
            if self.my_turn: 
                self.network.send_message(f"MOVE|{col},{row}")
                self.game.make_move(row, col, self.my_piece_id)
                # kiem tra thang
                winner, line = self.game.check_win_and_get_line(row, col)
                if winner: 
                    self.game_board.draw_winning_line(line[0], line[1])
                    self.handle_game_result("Bạn đã chiến thắng!")
                    return
                self.my_turn = False
                self.stop_timer()
                self.status_bar.config(text="Đang chờ đối thủ...")
            else: 
                self.handle_click_offline(row, col)

    def handle_click_offline(self, row, col):
        self.game.make_move(row, col, 1)
        self.game_board.place_piece(row, col, 1)
        winner, line = self.game.check_win_and_get_line(row, col)
        if winner: 
            self.game_board.draw_winning_line(line[0], line[1])
            self.handle_game_result_offline(winner)
            return
        
        self.status_bar.config(text="Máy đang suy nghĩ...")
        self.root.after(500, self.execute_ai_turn)

    def execute_ai_turn(self):
        ai_row, ai_col = self.game.best_move(self.game.board)
        self.game.make_move(ai_row, ai_col, 2)
        self.game_board.place_piece(ai_row, ai_col, 2)
        winner, line = self.game.check_win_and_get_line(ai_row, ai_col)
        if winner:
            self.game_board.draw_winning_line(line[0], line[1])
            self.handle_game_result_offline(winner)
        else:
            self.status_bar.config(text="Tới lượt bạn.")

    # ------ xử lý message từ server -------
    # def process_messages(self):
    
    # ------- timer -------
#     def start_timer(self, remaining_time): ...
#     def update_timer(self): ...
#     def stop_timer(self): ...

    # ------ Kết thúc -------
    def handle_game_result(self, text):
        self.my_turn = False
        self.game_started = False
        self.stop_timer()
        messagebox.showinfo("Kết thúc", text)
        if messagebox.askyesno("Chơi lại?", "Bạn có muốn chơi lại không?"):
            self.game.reset_board()
            self.game_board.reset()
            self.status_bar.config(text="Chờ bắt đầu lại...")
            self.show_waiting_screen()
        else:
            self.create_mode_selection_ui()
#     def handle_game_result_offline(self, winner): ...
#     def clear_main_frame(self): ...


#     def show_play_again_dialog(self, message): ...
#     # and helper methods to receive network events:
#     def handle_network_event(self, event_type, payload): ...