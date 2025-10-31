import tkinter as tk
from ui.game_ui import ChessboardApp
from network.client_network import WebSocketClient
import time
import os
from dotenv import load_dotenv

def main():
    load_dotenv()
    server_addr = os.getenv("server")
    # Giao diện nhập tên user ở terminal
    username = input("Nhập tên người chơi: ").strip()
    ws_client = WebSocketClient(server_addr)
    ws_client._init_ws()

    # Đợi kết nối websocket hoàn thành
    timeout = 5
    waited = 0
    while not ws_client.connected and waited < timeout:
        time.sleep(0.1)
        waited += 0.1

    root = tk.Tk()
    app = ChessboardApp(root, ws_client=ws_client, username=username)
    root.mainloop()

if __name__ == "__main__":
    main()