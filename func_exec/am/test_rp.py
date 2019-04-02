#!/usr/bin/env python

import os
import sys

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

nodes = 4
cpn   = 8
pwd   = os.getcwd()

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
        pdesc = rp.ComputePilotDescription(pd_init)
        pilot = pmgr.submit_pilots(pdesc)

        umgr = rp.UnitManager(session=session)
        umgr.add_pilots(pilot)

        # start the initial CU
        cu_init = {'executable' :  '%s/cu_setup.py'       % pwd, 
                   'pre_exec'   : ['. %s/ve/bin/activate' % pwd]
                  }
        cud = rp.ComputeUnitDescription(cu_init)

        # run it, wait until it is being executed
        setup_cu = umgr.submit_units(cud)

        umgr.wait_units(state=['AGENT_EXECUTING'])

        # setup has been executed, grab the output
        sbox = setup_cu.sandbox
        env  = dict()
        setup_sbox = ru.Url(setup_cu.sandbox).path
        with open('%s/setup.env' % setup_sbox, 'r') as fin:
            for line in fin.readlines():
                kv   = line.split()[1]
                k, v = kv.split('=', 1)
                env[k]        = v  # for the other CUs

        # connect to the ZMQ channels
        zmq_work    = ru.zmq.Putter(channel='WRK', url=env['APP_WRK_PUT'])
        zmq_result  = ru.zmq.Getter(channel='RES', url=env['APP_RES_GET'])
        zmq_control = ru.zmq.Putter(channel='CTL', url=env['APP_CTL_PUT'])

        print 'zmq connected'

        # run the executor CUs
        cuds = list()
        for n in range(nodes):
            cu_exec = {'executable' :  '%s/cu_exec.py'             % pwd, 
                       'pre_exec'   : ['. ../unit.000000/setup.env',
                                       '. %s/ve/bin/activate' % pwd], 
                       'environment':  env
                      }
            cuds.append(rp.ComputeUnitDescription(cu_exec))

        umgr.submit_units(cuds)
        umgr.wait_units(state=['AGENT_EXECUTING'])

        print 'all execs are active'

        n_tasks = 100000
        cmd     = 'time.time'
        args    = []

        tasks   = list()
        for i in range(n_tasks):
            task = {'uid'  : 'task.%06d' % i,
                    'exe'  : cmd,
                    'args' : args}
            tasks.append(task)

        print 'tasks send'
        zmq_work.put(tasks)
        print 'tasks sent'

        ret = list()
        while True:

            if len(ret) == n_tasks:
                print 'tasks done'
                for task in ret:
                    print task
                sys.exit(0)

            res = zmq_result.get_nowait(timeout=100)

            if res:
                ret.extend(res)

    finally:
        session.close(download=True)


# ------------------------------------------------------------------------------



