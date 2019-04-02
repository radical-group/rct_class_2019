#!/usr/bin/env python

__copyright__ = 'Copyright 2013-2016, http://radical.rutgers.edu'
__license__   = 'MIT'


import sys

import radical.utils     as ru
import radical.analytics as ra

import matplotlib.pyplot as plt
import numpy             as np


# We plot timelines for all events listed in `event_list` for all entities of
# type `event_entity`..  Before plotting, we sort those entities by the
# timestamp of the first event in the event list

event_entity = 'task'
e_get = {ru.STATE: None, ru.EVENT: 'task_get'}
e_put = {ru.STATE: None, ru.EVENT: 'task_put'}


# ------------------------------------------------------------------------------
#
if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "\n\tusage: %s <dir|tarball>\n" % sys.argv[0]
        sys.exit(1)

    src     = sys.argv[1]
    stype   = 'radical'
    session = ra.Session(src, stype)

    session.filter(etype=event_entity, inplace=True)
    print '#entities: %d' % len(session.get())


    # --------------------------------------------------------------------------
    # event timeline
    data = dict()
    for thing in session.get():

        tstamps = list()

        for event in [e_get, e_put]:
            times = thing.timestamps(event=event)
            if times: tstamps.append(times[0])
            else    : tstamps.append(None)

        data[thing.uid] = tstamps

    sorted_things = sorted(data.items(), key=lambda e: e[1][0])
    sorted_data   = list()
    index         = 0
    for thing in sorted_things:
        sorted_data.append([index] + thing[1])
        index += 1

    np_data = np.array(sorted_data)

    plt.figure(figsize=(20,14))
    for idx, e in enumerate([e_get, e_put]):
        plt.plot(np_data[:,0], np_data[:,(1 + idx)], label=e[ru.EVENT])

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.savefig('07_event_timeline.svg')
    plt.show()

    # --------------------------------------------------------------------------
    # task concurrency
    #
    data = session.concurrency(event=[e_get, e_put], sampling=0.1)

    import pprint
    pprint.pprint(data)

    x = [e[0] for e in data]
    y = [e[1] for e in data]

    plt.figure(figsize=(20,14))
    plt.plot(x, y, label='get / put')

    plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.15),
          ncol=2, fancybox=True, shadow=True)
    plt.savefig('06_concurrency.svg')
    plt.show()



# ------------------------------------------------------------------------------


# ------------------------------------------------------------------------------

