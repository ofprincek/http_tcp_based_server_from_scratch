import socket
import time

HOST="0.0.0.0" # address of the house
PORT=1600 # room number


my_server_socket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) # door for communication
my_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# now while, accept() is active in line 28, it'll not allow us to continue further down the code
# unless it gets it's value, to prevent this we do setblocking(False)
my_server_socket.setblocking(False)

# my_server_socket.bind(("0.0.0.0", 1600)) # (host, port)
my_server_socket.bind((HOST, PORT))

# now this alone will throw a resource temporrarily unavailable error unless the client can make
# request in milli seconds, and by setting blocking to false, we now run the full code without accept() blocking it


my_server_socket.listen(15)

print(f"listening on port {PORT}..")

while True:
    try:
        client_socket, client_address = my_server_socket.accept() # accepts the client's socket and IP address
        print(client_socket)
        print(client_address)
    except:
        time.sleep(0.5)
        continue
''' what this block essentially does is 
first forget while
we try to accept the client's request, if it works, meaning a client is in the connection queue
great we capture the details and print them
otherwise we wait .5 seconds and then continue the while loop.
this allows for multi-user functionality and for the program to be up and running forever(or atleast until we pull the plug)
'''