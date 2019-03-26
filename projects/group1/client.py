#!/usr/bin/env python

import zmq
import time
import msgpack
import pickle

from unit import Unit

DELAY = 0.5

# ------------------------------------------------------------------------------
#
#os.spawnl(os.P_NOWAIT, 'queue.cu_queue()')
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

cores = 16
tasks = 16

msg = {'data' : 16}
socket.send(msgpack.packb(msg))

for n in xrange(tasks):

    unit = Unit('import time \ntime.sleep(1)')

    msg = {'data' : pickle.dumps(unit)}
    socket.send(msgpack.packb(msg))
    print '-> %s' % n
    # time.sleep(DELAY)

# ------------------------------------------------------------------------------

