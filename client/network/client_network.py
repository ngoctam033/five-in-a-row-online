import socket
import threading
import queue

class NetworkManager:
    def __init__(self, message_queue):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.message_queue = message_queue
