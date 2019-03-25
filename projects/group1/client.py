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

start = time.time()

for n in xrange(500):

    unit = Unit('import time \ntime.sleep', args=(1,))

    msg = {'data' : pickle.dumps(unit)}
    socket.send(msgpack.packb(msg))
    print '-> %s' % n
    time.sleep(DELAY)

end = time.time()

print end - start

# ------------------------------------------------------------------------------

