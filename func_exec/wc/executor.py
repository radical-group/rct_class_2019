#!/usr/bin/env python

import os
import zmq
import time
import msgpack
import pickle
import logging

from unit import Unit

logger  = logging.getLogger(__name__)
logging.basicConfig(level=logging.NOTSET)

class Executor():

    def __init__(self, addr):
        self.addr    = addr
        self.context = None
        self.socket  = None

    def __enter__(self):

        logger.info('Starting to enter Executor instance')

        self.context = zmq.Context()
        self.socket  = self.context.socket(zmq.REQ)

        self.socket.hwm = 1

        self.socket.connect(self.addr)

        logger.info('Finished entering Executor instance')

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        logger.info('Starting to exit Executor instance')

        self.socket.close()

        logger.info('Finished exiting Executor instance')

    def req_msg(self):

        logger.info('Sending request to {addr}'.format(addr=self.addr))

        self.socket.send('request %d' % os.getpid())
        msg = msgpack.unpackb(self.socket.recv())

        logger.info('Request received')

        return msg

    def execute(self, unit):

        logger.info('Beginning to execute function')

        result = None
        call   = None

        try:
            call = unit.call()

            logger.debug('Executing {call}'.format(call=call))

            result = eval(call)

            logger.debug('Result is {result}'.format(result=result))

        except Exception as e:
            logger.warn('Uh Oh, Spaghetti O')

        logger.info('Function executed')

        return result

if __name__ == '__main__':

    DELAY = 0.5

    addr = None
    with open('test.bridge.url', 'r') as fin:
        for line in fin.readlines():
            tag, addr = line.split()
            if tag == 'GET':
                break

    print 'GET: %s' % addr

    with Executor(addr) as executor:

        while True:
            msg = executor.req_msg()

            unit = pickle.loads(msg['data'])

            executor.execute(unit)

            time.sleep(DELAY)
