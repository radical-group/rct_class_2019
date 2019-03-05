# Implements naive FIFO scheduler (thread safe)

import Queue

class fifo_scheduler(object):

    def __init__(self, priority, description):
        self.priority = priority
        self.description = description
        print 'New job:', description
        return

    def queue_fifo(self, units):

        # dummy cus to mimic cu description
        self.cus = OrderedDict((x,x) for x in reversed(range(10)))
        q = Queue.Queue()
        for i in self.cus:
            q.put(i)

        while not q.empty():
            print q.get()