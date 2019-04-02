#!/usr/bin/env python

import sys
import time

import radical.utils as ru


# ------------------------------------------------------------------------------a
#
if __name__ == '__main__':

    # create work, result and control ZMQ bridges
    zmq_b_work    = ru.zmq.Queue({'name': 'WRK', 'uid': 'radical.utils.wrk'})
    zmq_b_result  = ru.zmq.Queue({'name': 'RES', 'uid': 'radical.utils.res'})
    zmq_b_control = ru.zmq.Queue({'name': 'CTL', 'uid': 'radical.utils.ctl'})

    with open('./setup.env', 'w') as fout:

        fout.write("export %s=%s\n" % ('APP_WRK_PUT', zmq_b_work.addr_in))
        fout.write("export %s=%s\n" % ('APP_WRK_GET', zmq_b_work.addr_out))

        fout.write("export %s=%s\n" % ('APP_RES_PUT', zmq_b_result.addr_in))
        fout.write("export %s=%s\n" % ('APP_RES_GET', zmq_b_result.addr_out))

        fout.write("export %s=%s\n" % ('APP_CTL_PUT', zmq_b_control.addr_in))
        fout.write("export %s=%s\n" % ('APP_CTL_GET', zmq_b_control.addr_out))
        fout.flush()

    # wait forever
    while True:
        time.sleep(1)


# ------------------------------------------------------------------------------

