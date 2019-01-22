import socket
import sys
import json
from subprocess import call

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print >>sys.stderr, 'starting up on %s port %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print >>sys.stderr, 'waiting for a connection'
    connection, client_address = sock.accept()

    try:
        print >>sys.stderr, 'connection from', client_address

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(1024)
            data_loaded = json.loads(data)
            return_data = call([data_loaded['executable'], data_loaded['arguments']])
            serialized_dict = json.dumps(return_data)


            message = serialized_dict

            # import pdb
            # pdb.set_trace()

            print >>sys.stderr, 'received "%s"' % data_loaded
            # function executor 
            if data:
                print >>sys.stderr, 'sending data back to the client'
                connection.sendall(message)
            else:
                print >>sys.stderr, 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()