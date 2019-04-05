#!/usr/bin/env python

import os
import sys
import time

import multiprocessing as mp
import threading       as mt

import radical.utils   as ru

# wtf
import queue
mp.Queue.Empty = queue.Empty

_ve  = "/home/merzky/projects/rct/rct_class_2019/func_exec/am/ve"
_vea = "%s/bin/activate_this.py" % _ve
execfile(_vea, dict(__file__=_vea))


# ------------------------------------------------------------------------------
#
class Executor(object):
    '''
    This executor is running as an RP task and owns a complete node.  On each
    core of that node, it spawns a worker process to execute function calls.
    Communication to those processes is establshed via two mp.Queue instances,
    one for feeding call requests to the worker processes, and one to collect
    results from their execution

    Once the workers are prepared, the Executor will listens on an task level
    ZMQ channel for incoming call requests, which are then proxied to the
    workers as described above.  This happens in a separate thread.  Another
    thread is spawned to inversely collect the results as described above and to
    proxy them to an outgoing ZMQ channel.  The Executor main thread will listen
    on a 3rd ZMQ channel for control messages, and specifically for termination
    commands.
    '''

    # --------------------------------------------------------------------------
    #
    def __init__(self, n_workers=None):

        self._nw   = n_workers
        self._uid  = os.environ['RP_UNIT_ID']
        self._log  = ru.Logger('radical.pilot.func_exec')
        self._prof = ru.Profiler('radical.pilot.func_exec')


    # --------------------------------------------------------------------------
    #
    def _initialize(self):
        '''
        set up processes, threads and communication channels
        '''

        self._prof.prof('init_start', uid=self._uid)

        # get addresses
        addr = dict()
        with open('../unit.000000/addr.url', 'r') as fin:
            for line in fin.readlines():
                k, v = line.strip().split('=', 1)
                addr[k] = v

        # connect to 
        #
        #   - the queue which feeds us tasks
        #   - the queue were we send completed tasks
        #   - the command queue (for termination)
        #
        self._zmq_work    = ru.zmq.Getter(channel='WRK', url=addr['WRK_GET'])
        self._zmq_result  = ru.zmq.Putter(channel='RES', url=addr['RES_PUT'])
        self._zmq_control = ru.zmq.Getter(channel='CTL', url=addr['CTL_GET'])

        # use mp.Queue instances to proxy tasks to the worker processes
        self._mpq_work    = mp.Queue()
        self._mpq_result  = mp.Queue()

        # signal for thread termination
        self._term = mt.Event()

        # start threads to feed / drain the workers
        self._t_get_work    = mt.Thread(target=self._get_work)
        self._t_get_results = mt.Thread(target=self._get_results)

        self._t_get_work.daemon    = True
        self._t_get_results.daemon = True

        self._t_get_work.start()
        self._t_get_results.start()

        # start one worker per core
        if not self._nw:
            self._nw = mp.cpu_count() 

        self._log.debug('#workers: %d', self._nw)

        self._workers = list()
        for i in range(self._nw):
            wid  = '%s.%03d' % (self._uid, i)
            proc = mp.Process(target=self._work, args=[self._uid, wid])
            proc.start()
            self._workers.append(proc)

        self._prof.prof('init_stop', uid=self._uid)


    # --------------------------------------------------------------------------
    #
    def run(self):
        '''
        executor main loop: initialize all connections, processes, threads, then
        listen on the command channel for things to do (like, terminate).
        '''

        self._initialize()

        while True:

            msgs = self._zmq_control.get_nowait(100)

            if not msgs:
                continue

            for msg in msgs:

                self._prof.prof('cmd', uid=self._uid, msg=msg['cmd'])

                if msg['cmd'] == 'term':

                    # kill worker processes
                    for worker in self._workers:
                        worker.terminate()

                    sys.exit(0)

                else:
                    self._log.error('unknown command %s', msg)


    # --------------------------------------------------------------------------
    #
    def _get_work(self):
        '''
        thread feeding tasks pulled from the ZMQ work queue to worker processes
        '''

        while not self._term.is_set():

            tasks = self._zmq_work.get_nowait(100)

            if tasks:

                self._log.debug('=== got %d tasks', len(tasks))

                # send task individually to load balance workers
                for task in tasks:
                    self._mpq_work.put(task)


    # --------------------------------------------------------------------------
    #
    def _get_results(self):
        '''
        thread feeding back results from to workers to the result ZMQ queue
        '''

        while not self._term.is_set():

            # we always pull *individual* tasks from the result queue
            try:
                task = self._mpq_result.get(block=True, timeout=0.1)

            except mp.Queue.Empty:
                continue

            if task:
                self._zmq_result.put(task)


    # --------------------------------------------------------------------------
    #
    def _work(self, uid, wid):
        '''
        work loop for worker processes: pull a task from the work queue,
        run it, push the result onto the result queue
        '''

        self._prof.prof('work_start', comp=wid, uid=uid)

        while True:

            try:
                task = self._mpq_work.get(block=True, timeout=0.1)

            except mp.Queue.Empty:
                continue


            tid  = task['uid']
            exe  = task['exe']
            args = task.get('args', [])
            cmd  = '%s(%s)' % (exe, ','.join(args)) 

            self._prof.prof('task_get', comp=wid, uid=tid)
          # self._log.debug('get %s: %s', tid, cmd)

            task['res'] = None
            task['err'] = None

            try:
                task['res'] = eval(cmd)

            except Exception as e:
                task['err'] = str(e)

          # self._log.debug('put %s: %s', tid, str(task['res']))
            self._prof.prof('task_put', comp=wid, uid=tid)

            self._mpq_result.put(task)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    executor = Executor()
    executor.run()


# ------------------------------------------------------------------------------

