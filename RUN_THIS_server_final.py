#!/usr/bin/python3

import socket
import threading

HOST = "0.0.0.0"  # or do HOST = socket.gethostname(socket.gethostname())
PORT = 9000

def site_homepage():
    with open("/home/ofprincek/github/http_tcp_based_server_from_scratch/homepage.html") as homepage:
        content=homepage.read()
        response = 'HTTP/1.1 200 OK\r\n\r\n' + content
        return response
    
def site_about():
    with open("/home/ofprincek/github/http_tcp_based_server_from_scratch/about.html") as about:
        content=about.read()
        response = 'HTTP/1.1 200 OK\r\n\r\n' + content
        return response

def url_not_found():
        content="URL not found, under construction.."
        response = 'HTTP/1.1 6767 METHOD NOT FOUND\r\n\r\n' + content
        return response

index={
    '/' : site_homepage,
    '/about' : site_about
}

def handle_client(client_socket, client_address):
     try:
         client_socket.settimeout(5) # if the client cannot connect within 5 secs, drops, to prevent against slowloris.

         client_request=client_socket.recv(1500).decode()
         client_request_headers=client_request.split('\n')
         first_line=client_request_headers[0]

         first_header_components = first_line.split()
         http_request=first_header_components[0]
         url_request=first_header_components[1]

         if http_request == "GET":
              handler = index.get(url_request, url_not_found)
              response = handler()

         else:
              response = 'HTTP/1.1 404 METHOD NOT PERMITTED\r\n\r\nAllowed: GET'
         client_socket.sendall((response.encode()))


     except socket.timeout:
          print(f"client : {client_address} timed out, dropping connection..")
     
     except Exception as e:
          print(f"Error handling client {client_address}, due to {e}")
     
     finally:
          client_socket.close()


my_server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
my_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_server_socket.bind((HOST, PORT))
my_server_socket.listen(100)

print(f"Server Online. Listening on port {PORT}...")


while True:
     client_socket, client_address = my_server_socket.accept() # accept() does the handshake after which we can assign a thread to the client.
     print(f"[CLIENT] {client_address} connected to your server..")
     thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
     thread.start()
    #  deliberately didn't do a join() here:
    # it's a blocking call. Calling it means: "pause execution of next line, 
    # here our next while itertation 
    # and don't proceed past it until the thread finishes."
    # without it, thread starts and returns control back instantly to thw while loop
    # meaning we can accept() further clients/requests.