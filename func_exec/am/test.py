#!/usr/bin/env python

import os
import sys
import time
import psutil

import threading       as mt
import multiprocessing as mp


# ------------------------------------------------------------------------------
#
class Unit(object):

    # --------------------------------------------------------------------------
    #
    def __init__(self, descr):

        self.descr  = descr
        self.uid    = descr['uid']
        self.exe    = descr['exe']
        self.args   = descr['args']
        self.result = None
        self.worker = None


    # --------------------------------------------------------------------------
    #
    def wait(self):

        while self.result is None:
            time.sleep(0.1)


# ------------------------------------------------------------------------------
#
class Executor:

    # --------------------------------------------------------------------------
    #
    def __init__(self, n):

        self._units    = dict()
        self._work_q   = mp.Queue()
        self._result_q = mp.Queue()

        self._p_collect = mt.Thread(target=self._collect)
        self._p_collect.start()

        self._procs    = [mp.Process(target=self._work, args=['w.%02d' % i])
                           for i in range(n)]
        for p in self._procs:
            p.start()


    # --------------------------------------------------------------------------
    #
    def _out(self, pid, msg):

        sys.stdout.write('%-10s: %s\n' % (pid, msg))
        sys.stdout.flush()


    # --------------------------------------------------------------------------
    #
    def _collect(self):

        while True:

            ret = self._result_q.get()

            if not ret:
                return

            uid, wid, res = ret

            self._units[uid].result = res
            self._units[uid].worker = wid

         #  self._out(pid, '---> %s [%s]: %s' % (uid, wid, res))


    # --------------------------------------------------------------------------
    #
    def submit(self, cud):

        cu = Unit(cud)

        self._units[cu.uid] = cu

        self._work_q.put(cud)

        return cu


    # --------------------------------------------------------------------------
    #
    def _work(self, wid):

      # self._out(wid, '%s start' % wid)

        while True:

            try:

                try:
                    cud = self._work_q.get()
                except:
                    time.sleep(1)
                    continue

              # self._out(wid, '%s: get %s' % (wid, cu))
                if not cud:
                  # self._out(wid, '%s: break' % wid)
                    break

                uid  = cud['uid']
                exe  = cud['exe']
                args = cud.get('args', [])
                cmd  = '%s(%s)' % (exe, ','.join(args)) 
                res  = eval(cmd)

                self._result_q.put([uid, wid, res])

            except Exception as e:
                self._out(wid, '!!', wid, e)

      # self._out(wid, 'done')


    # --------------------------------------------------------------------------
    #
    def terminate(self):

        for p in self._procs:
            self._work_q.put(None)

        self._result_q.put(None)


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    n    = 16       # number of worker processes
    N    = 100000   # number of tasks

    cus  = list()
    prof = list()
    prof.append(time.time())

    r = Executor(n=n)

    prof.append(time.time())
    for i in range(N):
        cud = {'uid'  : 'cu.%06d' % i,
               'exe'  : 'time.time',
               'args' : []}
        cu  = r.submit(cud)
        cus.append(cu)

    prof.append(time.time())
    for cu in cus:
        cu.wait()
     #  print '--> %s [%s]: %s' % (cu.uid, cu.worker, cu.result)
    prof.append(time.time())

    r.terminate()
    prof.append(time.time())


    print 'workers: %10d' % n
    print 'tasks  : %10d' % N

    diff = prof[1] - prof[0]
    print 'start  : %10.2f s' % (diff)

    diff = prof[2] - prof[1]
    print 'submit : %10.2f s  [%8d tasks/s]' % (diff, N / diff)

    diff = prof[3] - prof[2]
    print 'collect: %10.2f s  [%8d tasks/s]' % (diff, N / diff)

    diff = prof[4] - prof[3]
    print 'term   : %10.2f s' % (diff)

    diff = prof[4] - prof[0]
    print 'total  : %10.2f s' % (diff)

    p = psutil.Process(os.getpid())
    print 'memory : %10.2f MB]' % (p.memory_info().rss / (1024 * 1024))


# ------------------------------------------------------------------------------

