import socket
import time

HOST="0.0.0.0" # address of the house
PORT=1600 # room number


my_server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) # door for communication
my_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

my_server_socket.bind((HOST, PORT))

my_server_socket.listen(15)

print(f"listening on port {PORT}..")

# reason removing the setblocking was removing try and except first, otherwise it'll give error and just end, while loop will not continue

while True:
    client_socket, client_address = my_server_socket.accept()
    client_request=client_socket.recv(1500).decode() # this gets the http request made by the client in a nice string format
    print(client_request)

    # extracting the first line from request decoded
    client_request_headers=client_request.split('\n')
    print(client_request_headers[0])

    # breaking that first line into parts by split()
    first_header_components=client_request_headers[0].split()
    http_request=first_header_components[0]
    request_path=first_header_components[1]
    if http_request=="GET":
        if request_path == '/' :
            with open("/home/ofprincek/github/http_tcp_based_server_from_scratch/index.html") as indx: # please modify the filepath here, based on your terminal.
                content=indx.read()
                indx.close()
    
            # HTML response format:
            # STATUS LINE -
            # HEADERS 
            # MESSAGE-BODY
            response= 'HTTP/1.1 200 OK\r\n\r\n' + content
    else:
        response= 'HTTP/1.1 404 METHOD NOT PERMITTED\r\n\r\nALLOW :GET'
        
    client_socket.sendall(response.encode()) # we could've used send() but it doesn't guarantee everything will reach
    client_socket.close()