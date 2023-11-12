#!/usr/bin/python

import socket
import time

def reverse_listener(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((ip, port))
    server_socket.listen(1)
    
    print(f"Listening on {ip}:{port}")

    conn, addr = server_socket.accept()

    print(addr, 'connected')

    while 1:
        cmd = input()

        conn.send((cmd + '\n').encode())

        data = conn.recv(1024)

        print(data.decode())

        time.sleep(0.250)
        
    conn.close()

if __name__ == "__main__":
    reverse_listener("127.0.0.1", 8999)
