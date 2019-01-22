import socket
import sys
import json


def get_constants(prefix):
    """Create a dictionary mapping socket module constants to their names."""
    return dict( (getattr(socket, n), n)
                 for n in dir(socket)
                 if n.startswith(prefix)
                 )

families = get_constants('AF_')
types = get_constants('SOCK_')
protocols = get_constants('IPPROTO_')

# Create a TCP/IP socket
sock = socket.create_connection(('localhost', 10000))

print >>sys.stderr, 'Family  :', families[sock.family]
print >>sys.stderr, 'Type    :', types[sock.type]
print >>sys.stderr, 'Protocol:', protocols[sock.proto]
print >>sys.stderr

class cu(dict):
    def __init__(self, executable, arguments):

        self['executable'] = executable
        self['arguments']  = arguments


usr_executable = raw_input("executable? ")
usr_argument = raw_input("arguments? ")
cu = cu(usr_executable, usr_argument)
serialized_dict = json.dumps(cu)

# import pdb
# pdb.set_trace()

message = serialized_dict


try:
    
    # Send data
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    amount_received = 0
    amount_expected = len(message)
    
    while amount_received < amount_expected:
        data = sock.recv(1024)
        a_dict = json.loads(data)
        amount_received += len(a_dict)
        print >>sys.stderr, 'received "%s"' % a_dict

finally:
    print >>sys.stderr, 'closing socket'
    sock.close()