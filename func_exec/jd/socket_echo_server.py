import socket
import sys
import json
# from subprocess import call

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

            
            # cmd = "{}({})".format(data_loaded['executable'], data_loaded['arguments'])

            # The eval() function lets a Python program run Python code within 
            # itself

            # return_data = eval(cmd)

            # But we can still import modules and use them, with the builtin function __import__
            return_data = eval("__import__('time')", {})
            # return_data = call([data_loaded['executable'], data_loaded['arguments']])
            serialized_dict = json.dumps(return_data)
            
            print >>sys.stderr, 'received "%s"' % data_loaded
            # function executor 
            if data:
                print >>sys.stderr, 'sending data back to the client'
                connection.sendall(serialized_dict)
            else:
                print >>sys.stderr, 'no more data from', client_address
                break
            
    finally:
        # Clean up the connection
        connection.close()