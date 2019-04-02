#!/usr/bin/env python

import os
import sys
import time

import multiprocessing as mp

import radical.utils   as ru

from executor import Executor


# ------------------------------------------------------------------------------
#
class FuncExecApp(object):

    # --------------------------------------------------------------------------
    #
    def __init__(self, n_executors=1, executor_size=1):

        self._prof = ru.Profiler('radical.pilot.func_exec')

        self._prof.prof('init_start')

        # create work, result and control ZMQ bridges
        zmq_b_work    = ru.zmq.Queue({'name': 'WRK', 'uid': 'radical.utils.wrk'})
        zmq_b_result  = ru.zmq.Queue({'name': 'RES', 'uid': 'radical.utils.res'})
        zmq_b_control = ru.zmq.Queue({'name': 'CTL', 'uid': 'radical.utils.ctl'})

        env = os.environ
        env['APP_WRK_PUT'] = str(zmq_b_work.addr_in)
        env['APP_WRK_GET'] = str(zmq_b_work.addr_out)

        env['APP_RES_PUT'] = str(zmq_b_result.addr_in)
        env['APP_RES_GET'] = str(zmq_b_result.addr_out)

        env['APP_CTL_PUT'] = str(zmq_b_control.addr_in)
        env['APP_CTL_GET'] = str(zmq_b_control.addr_out)

        # start `n` executors as CUs of size `s`
        def _cu(size):
            cu = Executor(n_workers=size)
            cu.run()

        self._execs = list()
        for i in range(n_executors):
            env['RP_UNIT_ID'] = 'unit.%06d' % i
            proc = mp.Process(target=_cu, args=[executor_size])
            proc.start()
            self._execs.append(proc)

        # connect our endpoints
        self._zmq_work    = ru.zmq.Putter(channel='WRK', url=env['APP_WRK_PUT'])
        self._zmq_result  = ru.zmq.Getter(channel='RES', url=env['APP_RES_GET'])
        self._zmq_control = ru.zmq.Putter(channel='CTL', url=env['APP_CTL_PUT'])

        self._prof.prof('init_stop')


    # --------------------------------------------------------------------------
    #
    def run_tasks(self, tasks):
        '''
        submit the given tasks, wait for their completion.
        returns a copy of the original task list (order not preserved)
        '''

        self._prof.prof('run_start')
        n_tasks = len(tasks)

        self._zmq_work.put(tasks)

        ret = list()
        while True:

            if len(ret) == n_tasks:
                self._prof.prof('run_stop')
                return ret

            res = self._zmq_result.get_nowait(timeout=100)

            if res:
                ret.extend(res)


    # --------------------------------------------------------------------------
    #
    def stop(self):

        for e in self._execs:
            self._zmq_control.put({'cmd' : 'term'})

        for e in self._execs:
            e.join(timeout=1.0)

        for e in self._execs:
            e.terminate()


def usage(exit_code):

    print '''

    usage:     %(cmd)s n_tasks cmd arg_1 arg_2 ...

    examples:  %(cmd)s 10      time.time
               %(cmd)s 1000    time.sleep 0.1
               %(cmd)s 1000000 time.sleep foo       # undefined variable foo
               %(cmd)s 1000000 time.sleep "'foo'"   # needs float, not string

''' % {'cmd' : sys.argv[0]}

    sys.exit(exit_code)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage(1)

    n_tasks = int(sys.argv[1])
    cmd     =     sys.argv[2]
    args    =     sys.argv[3:]

    app     = FuncExecApp(n_executors=2, executor_size=4)

    tasks   = list()
    for i in range(n_tasks):
        task = {'uid'  : 'task.%06d' % i,
                'exe'  : cmd,
                'args' : args}
        tasks.append(task)

    # run_tasks returns a copy of the original task list
    tasks = app.run_tasks(tasks)

    for task in tasks:
        print task


    app.stop()


# ------------------------------------------------------------------------------

