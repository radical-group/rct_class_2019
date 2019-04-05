#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import radical.utils     as ru
import radical.analytics as ra

import matplotlib.pyplot as plt
import numpy             as np


# ------------------------------------------------------------------------------
# task related events
e_get = {ru.STATE: None, ru.EVENT: 'task_get'}
e_put = {ru.STATE: None, ru.EVENT: 'task_put'}


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    src     = sys.argv[1]
    session = ra.Session(src, 'radical')
    tasks   = session.filter(etype='task', inplace=False)
    print '#entities: %d' % len(session.get())


    # --------------------------------------------------------------------------
    # event timeline
    data = dict()
    for task in session.get():

        tstamps = list()
        for event in [e_get, e_put]:
            times = task.timestamps(event=event)
            if times: tstamps.append(times[0])
            else    : tstamps.append(None)

        data[task.uid] = tstamps

    sorted_tasks = sorted(data.items(), key=lambda e: e[1][0])
    sorted_data  = list()
    index        = 0
    for task in sorted_tasks:
        sorted_data.append([index] + task[1])
        index += 1

    np_data = np.array(sorted_data)

    plt.figure(figsize=(20,14))
    for idx, e in enumerate([e_get, e_put]):
        plt.plot(np_data[:,0], np_data[:,(1 + idx)], label=e[ru.EVENT])

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.savefig('timeline.svg')
    plt.show()


    # --------------------------------------------------------------------------
    # task rate
    plt.figure(figsize=(20,14))

    data = session.rate(event=e_get, sampling=0.1)
    x = [e[0] for e in data]
    y = [e[1] for e in data]

    plt.plot(x, y, label='get')

    data = session.rate(event=e_put, sampling=0.1)
    x = [e[0] for e in data]
    y = [e[1] for e in data]

    plt.plot(x, y, label='put')

    plt.ylim(bottom=0)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.savefig('rate.svg')
    plt.show()


# ------------------------------------------------------------------------------

