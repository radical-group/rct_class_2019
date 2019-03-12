#!/usr/bin/env python
import zmq
import time
import msgpack
import sys
import os


DELAY = 0.5
# ------------------------------------------------------------------------------
#
NumTask=4
addr = None
with open('test.bridge.url', 'r') as fin:
    for line in fin.readlines():
        tag, addr = line.split()
        if tag == 'PUT':
            break

print 'PUT: %s' % addr
context    = zmq.Context()
socket     = context.socket(zmq.PUSH)
socket.hwm = 1
socket.connect(addr)

for n in xrange(NumTask):
    #msg = {"modules" :"","executable" :'print "hello world"',"arguments":" "}
    #msg = {"modules" :"numpy","executable" :'numpy.sin(1+2)',"arguments":" "}
    #msg = {"modules" :"os","executable" :'os.system(ls -all)',"arguments":" "}
    msg = {"modules" :"time","executable" :'time.time()',"arguments":" "}

    socket.send(msgpack.packb(msg))
   
print (NumTask ,' Task submitted ' )

# ------------------------------------------------------------------------------

