
import tkinter as tk
from ui.game_ui import ChessboardApp
from ui.login_ui import LoginUI
from network.client_network import WebSocketClient
import time
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    server_addr = os.getenv("server")
    ws_client = WebSocketClient(server_addr)
    ws_client._init_ws()

    # Đợi kết nối websocket hoàn thành
    timeout = 5
    waited = 0
    while not ws_client.connected and waited < timeout:
        time.sleep(0.1)
        waited += 0.1

    root = tk.Tk()
    def start_game(username):
        # Xóa giao diện login
        for widget in root.winfo_children():
            widget.destroy()
        app = ChessboardApp(root, ws_client=ws_client, username1=username, username2="Player2")

    login_ui = LoginUI(root, ws_client=ws_client, on_login_callback=start_game)
    root.mainloop()

if __name__ == "__main__":
    main()