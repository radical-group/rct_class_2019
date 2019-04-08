#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import radical.utils     as ru
import radical.analytics as ra

import matplotlib        as mpl
import matplotlib.pyplot as plt
import numpy             as np

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 14}

plt.rcParams['axes.titlesize']   = 14
plt.rcParams['axes.labelsize']   = 14
plt.rcParams['axes.linewidth']   =  2
plt.rcParams['lines.linewidth']  =  2
plt.rcParams['lines.markersize'] = 14
plt.rcParams['xtick.labelsize']  = 14
plt.rcParams['ytick.labelsize']  = 14
plt.rc('font', **font)



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

    with open('fex_timeline.dat', 'w') as fout:
        d0 = list(np_data[:,0])
        d1 = list(np_data[:,1])
        d2 = list(np_data[:,2])
        for n in range(len(d0)):
            x, y, z = d0[n], d1[n], d2[n]
            if None not in [x, y, z]:
                fout.write('%f,%f,%f\n' % (x, y, z))

    plt.figure(figsize=(10,4))
    for idx, e in enumerate([e_get, e_put]):
        plt.plot(np_data[:,0], np_data[:,(1 + idx)], label=e[ru.EVENT][-3:])

    plt.legend(ncol=2, fancybox=True, shadow=True)
    plt.savefig('fex_timeline.png', bbox_inches="tight")
    plt.show()


    # --------------------------------------------------------------------------
    # task rate
    plt.figure(figsize=(10,4))

    data = session.rate(event=e_get, sampling=0.1)
    x = [e[0] for e in data]
    y = [e[1] for e in data]

    plt.plot(x, y, label='get')

    data = session.rate(event=e_put, sampling=0.1)
    x = [e[0] for e in data]
    y = [e[1] for e in data]

    with open('fex_rate.dat', 'w') as fout:
        for n in range(len(x)):
            fout.write('%f,%f\n' % (x[n], y[n]))

    plt.plot(x, y, label='put')

    plt.ylim(bottom=0)
    plt.legend(ncol=2, fancybox=True, shadow=True)
    plt.savefig('fex_rate.png', bbox_inches="tight")
    plt.show()


# ------------------------------------------------------------------------------

