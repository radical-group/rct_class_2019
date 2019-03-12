#!/usr/bin/env python
#simple ZMQ multiprocessing model based on @andre-merzky zmq example
#Feb 22 2019
import os
import zmq
import time
import msgpack
import sys
import os
import logging
import multiprocessing
from multiprocessing import Process, Lock, Pool

# ------------------------------------------------------------------------------
#
lock = Lock()
logger = multiprocessing.get_logger()
DELAY = 0.0
addr = None

with open('test.bridge.url', 'r') as fin:
    for line in fin.readlines():
        tag, addr = line.split()
        if tag == 'GET':
            break
print 'GET: %s' % addr

class zmqex():

    def recv(self):
        context    = zmq.Context()
        socket     = context.socket(zmq.REQ)
        socket.hwm = 1
        socket.connect(addr)      
        logging.basicConfig(level=logging.DEBUG)
        socket.send('request %d' % os.getpid())
        msg = msgpack.unpackb(socket.recv())   
        
        self.modl       = msg['modules']
        self.executable = msg['executable']
        self.arguments  = msg['arguments']


    def exe(self):

        lock.acquire()
        mod=self.modl
        if mod !="":
            try:
                exec "import {}".format(mod)
            except Exception:
                 pass 

        try:
            cmd=self.executable
            std=eval(compile(cmd, '<string>', 'eval'))
            print std
            
        finally:
            pass

        lock.release()

if __name__ == '__main__':
    cc=zmqex()   
    cc.recv()
    NumTask=4
    multiprocessing.log_to_stderr()
    logger.setLevel(logging.INFO)
    processes = []
    for w in range(NumTask):
        p = multiprocessing.Process(target=cc.exe)
        processes.append(p)
        p.start()
    for p in processes:
        p.join()
 
    # ------------------------------------------------------------------------------

