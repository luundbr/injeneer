#!/usr/bin/python

import socket
import time
import threading

class ReverseListener:
    def __init__(self, ip, port, once=True, cb=None):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((ip, port))
        self.server_socket.listen(5)
        self.once = once
        self.cb = cb
        self.listening_thread = None
        self.client_threads = []
        self.active = False
        self.client_connections = []

    def handle_client(self, conn, addr):
        print(f"{addr} connected")
        with conn:
            while self.active:
                if self.cb:
                    cmd = self.cb()
                else:
                    cmd = input("Enter command: ")

                conn.send((cmd + '\n').encode())

                data = conn.recv(1024)
                if not data:
                    break

                print(data.decode())

                if self.once:
                    break

                time.sleep(0.250)

        print(f"Connection with {addr} closed")
        self.client_connections.remove(conn)

    def start_listening(self):
        while self.active:
            conn, addr = self.server_socket.accept()
            self.client_connections.append(conn)
            client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
            self.client_threads.append(client_thread)

    def start(self):
        self.active = True
        print(f"Listening on {self.server_socket.getsockname()}")
        self.listening_thread = threading.Thread(target=self.start_listening)
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def stop(self):
        self.active = False

        for conn in self.client_connections:
            conn.close()

        self.server_socket.close()

        self.listening_thread.join()

        for client_thread in self.client_threads:
            client_thread.join()

        print("Server stopped")

if __name__ == "__main__":
    try:
        listener = ReverseListener('127.0.0.1', 8999, once=False)
        time.sleep(10)
    finally:
        listener.stop()
    
