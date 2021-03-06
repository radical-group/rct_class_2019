import queue
import os
import zmq
import time
import msgpack
import pickle
import logging
import multiprocessing as mp
import threading as mt

from unit import Unit
import hide_globals
from hide_globals import exec_user as execute_cu

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

            result = execute_cu(call)

            logger.debug('Result is {result}'.format(result=result))

        except Exception as e:
            logger.warn(e)
            raise Exception

        logger.info('Function executed')

        return result

#class ComputeUnit():
	 #### A CU is a container that runs one instance of an executor.


#    def CU_Execute():
#        return
    #DELAY = 0.5


def start_cu(addr):
    # Starts a persistent "compute unit" that listens for messages from the queue. 
    # Each message contains multi-line code to be executed by our executor.
    with Executor(addr) as worker:

        while True:
            msg = worker.req_msg()
            unit = pickle.loads(msg['data'])
            try:
                worker.execute(unit)
            except KeyboardInterrupt:
                break

if __name__ == '__main__':

    # Hard code number of cores for now.
    CORES = 4

    # Spawn the queue on an independent thread
    queue_t = mt.Thread(target = queue.cu_queue)
    queue_t.start()
    time.sleep(3)

    # Get the queue address
    addr = None
    with open('test.bridge.url', 'r') as fin:
        for line in fin.readlines():
            tag, addr = line.split()
            if tag == 'GET':
                break

    print 'GET: %s' % addr

    workers = [addr]*CORES

    # create function executors
    mp.Pool(CORES).map(start_cu, workers)
