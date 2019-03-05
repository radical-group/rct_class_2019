import time
import zmq
import pika
import json
import random
import example_compute
import executor
import multiprocessing as mp


PROCESSES = 10 
TASK_COUNT = 10 

class Worker(object):
    mq = "zmq"
    mq = "rabbitmq"
    q_name = "task_queue"

    def __init__(self):
        # Assign ID to each worker
        self.id = random.randrange(1,10005)
        #print ("I am worker #%s" % (self.id))
        func = getattr(self, "init_{}".format(self.mq))
        func()

    def init_zmq(self):
        # Create zmq context and tcp receiver/sender connections 
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect("tcp://127.0.0.1:5557")
        # send results
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.connect("tcp://127.0.0.1:5558")

    def init_rabbitmq(self):
        # create RMQ channel 
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=self.q_name, durable=False)
        self.receiver = channel

    def recv(self):
        func = getattr(self, "recv_{}".format(self.mq))
        return func()

    def recv_zmq(self):
        return self.receiver.recv_json()

    def recv_rabbitmq(self):
        method_frame, header_frame, body = self.receiver.basic_get(self.q_name)
        if method_frame:
            self.receiver.basic_ack(method_frame.delivery_tag)
            return json.loads(body)

    def send(self, msg):
        func = getattr(self, "send_{}".format(self.mq))
        func(msg)

    def send_zmq(self, msg):
        self.sender.send_json(msg)

    def send_rabbitmq(self, msg):
        #TBD
        print (msg)

    @staticmethod
    def function_executor(work):
        pe = executor.pythonExecutor()
        pe.function = work['function']
        pe.params = work['params']
        res = pe.executor()
        result = { 'worker_id' :  work['uid'], 'task_id' : work['tid'],
                'result': res }
        return result

if __name__ == "__main__":

    # instance 1) for each task we have one worker: assume 8 workers, 8 cpus

    # instance 2) we assign as many workers as we have tasks but only 
    # allow execution if enough cores available: cpu_count()
  

    CPUS = mp.cpu_count()
    p = mp.Pool(PROCESSES)
    print 'Creating pool with {} processes\n'.format(PROCESSES)

    obj = Worker()
    results = []
    for i in range(10):
        # Receive 1 message
        msg = obj.recv()
        msg['uid'] = obj.id
        r = p.apply_async(obj.function_executor, args=(msg,))
        results.append(r)
    # Collect results and send back
    for i in results:
        x = (i.get())
        obj.send(x)
