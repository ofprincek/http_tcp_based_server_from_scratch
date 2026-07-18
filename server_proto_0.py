import socket
import time

server_host="0.0.0.0"
server_port=8080

server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((server_host, server_port))

server_socket.listen(5)

print(f"The Server is Listening.. on port {server_port}")
while True:
    client_socket, client_address = server_socket.accept()
    request=client_socket.recv(1500).decode()
    print(request)

