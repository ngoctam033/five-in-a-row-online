import asyncio
from server import WebSocketServer

async def main():
    ws_server = WebSocketServer()
    await ws_server.start()

if __name__ == "__main__":
    asyncio.run(main())
