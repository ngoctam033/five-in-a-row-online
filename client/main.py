import tkinter as tk
from ui.game_ui import ChessboardApp
from network.client_network import WebSocketClient
import time
import os
from dotenv import load_dotenv
import asyncio

async def main():
    load_dotenv()
    server_addr = os.getenv("server")
    ws_client = WebSocketClient(server_addr)
    await ws_client._init_ws()

    # Đợi kết nối websocket hoàn thành
    timeout = 5
    waited = 0
    while not ws_client.connected and waited < timeout:
        time.sleep(0.1)
        waited += 0.1

    if ws_client.connected and ws_client.connection is not None:
        root = tk.Tk()
        app = ChessboardApp(root, ws_client=ws_client)
        root.mainloop()
    else:
        print("Không thể kết nối đến server websocket. Ứng dụng sẽ không khởi động.")

if __name__ == "__main__":
    asyncio.run(main())