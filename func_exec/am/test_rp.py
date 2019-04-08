#!/usr/bin/env python

import os
import sys
import time

import radical.utils as ru
import radical.pilot as rp


# This runs RP with the function executor as workload.  We first run a single
# compute unit on core no. 0 which sets up the communication bridges.  We let
# that unit run, but read its output to get the endpoint information, and set
# that as environment for all other compute units (and for the application
# itself)
#
# Next we run one compute unit per node, and start feeding tasks to the
# resulting executor nnet via the initially established ZMQ bridges.
#
# Once we get all results, we terminate RP (which cancels the units of the
# executor network).
#
# Note that one executor will have a core missing, fir account for the setup CU.

ntasks = 1024 * 128
chunk  = ntasks
nodes  = 10
cpn    = 41
pwd    = os.getcwd()

# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    session = rp.Session()
    try:

        pmgr    = rp.PilotManager(session=session)
        pd_init = {'resource'      : 'local.localhost',
                   'runtime'       : 60,
                   'exit_on_error' : True,
                   'cores'         : cpn * nodes
                  }
        pd_init = {'resource'      : 'ornl.summit',
                   'runtime'       : 60,
                   'exit_on_error' : True,
                   'cores'         : cpn * nodes,
                   'queue'         : 'batch',
                   'project'       : 'BIP178',
                  }
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)

        umgr = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        # start the initial CU
        cu_init = {'executable' : '%s/cu_setup.py' % pwd}
        cud = rp.ComputeUnitDescription(cu_init)

        # run it, wait until it is being executed
        setup_cu = umgr.submit_units(cud)

        umgr.wait_units(state=['AGENT_EXECUTING'])

        # wait a while until the addr info arrive on the file system (timeout
        # after a min)
        setup_sbox = ru.Url(setup_cu.sandbox).path
        addr_fname = '%s/addr.url' % setup_sbox

        t_0 = time.time()
        while time.time() - t_0 < 60:
            if os.path.isfile(addr_fname):
                break
            else:
                time.sleep(1)

        if not os.path.isfile(addr_fname):
            raise RuntimeError('cannot find address info in %s' % addr_fname)

        # setup has been executed, grab the output
        addr = dict()
        with open(addr_fname, 'r') as fin:
            for line in fin.readlines():
                k, v = line.strip().split('=', 1)
                addr[k] = v

        # connect to the ZMQ channels
        zmq_work    = ru.zmq.Putter(channel='WRK', url=addr['WRK_PUT'])
        zmq_result  = ru.zmq.Getter(channel='RES', url=addr['RES_GET'])
        zmq_control = ru.zmq.Putter(channel='CTL', url=addr['CTL_PUT'])

        print 'zmq connected'

        cmd     = 'time.time'
        args    = []
        tasks   = list()
        for i in range(ntasks):
            task = {'uid'  : 'task.%06d' % i,
                    'exe'  : cmd,
                    'args' : args}
            tasks.append(task)

        print 'tasks send'
        n = 0
        while n < ntasks:
            zmq_work.put(tasks[n:n + chunk])
            n += chunk

        print 'tasks sent'

        # run the executor CUs
        cuds = list()
        for n in range(nodes):
            cu_exec = {'executable' : '%s/cu_exec.py' % pwd}
            cuds.append(rp.ComputeUnitDescription(cu_exec))

        umgr.submit_units(cuds)
        umgr.wait_units(state=['AGENT_EXECUTING'])

        print 'all execs are active'

        ret = list()
        while True:

            if len(ret) == ntasks:
                print 'tasks done'
                for task in ret:
                    if task['err']: sys.stdout.write('-')
                    else          : sys.stdout.write('+')
                print
                sys.exit(0)

            res = zmq_result.get_nowait(timeout=100)

            if res:
                ret.extend(res)

    finally:
        session.close(download=False)


# ------------------------------------------------------------------------------



