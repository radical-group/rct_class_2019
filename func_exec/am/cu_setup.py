#!/usr/bin/env python

import time

import radical.utils as ru


_ve  = "/home/merzky/projects/rct/rct_class_2019/func_exec/am/ve"
_vea = "%s/bin/activate_this.py" % _ve
execfile(_vea, dict(__file__=_vea))


# ------------------------------------------------------------------------------a
#
if __name__ == '__main__':
    '''
    create work, result and control ZMQ bridges, and store their respective
    endpoints so that other CUs (executors) can use them.

    This CU will run forever, keeping the bridges alive on node_1, and will get
    terminnated when the pilot shuts down.
    '''

    zmq_b_work    = ru.zmq.Queue({'name': 'WRK', 'uid': 'radical.utils.wrk'})
    zmq_b_result  = ru.zmq.Queue({'name': 'RES', 'uid': 'radical.utils.res'})
    zmq_b_control = ru.zmq.Queue({'name': 'CTL', 'uid': 'radical.utils.ctl'})

    with open('./addr.url', 'w') as fout:

        fout.write("%s=%s\n" % ('WRK_PUT', zmq_b_work.addr_in))
        fout.write("%s=%s\n" % ('WRK_GET', zmq_b_work.addr_out))

        fout.write("%s=%s\n" % ('RES_PUT', zmq_b_result.addr_in))
        fout.write("%s=%s\n" % ('RES_GET', zmq_b_result.addr_out))

        fout.write("%s=%s\n" % ('CTL_PUT', zmq_b_control.addr_in))
        fout.write("%s=%s\n" % ('CTL_GET', zmq_b_control.addr_out))

    # wait forever
    while True:
        time.sleep(1)


# ------------------------------------------------------------------------------

