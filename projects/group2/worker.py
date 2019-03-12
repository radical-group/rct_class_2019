import sys
import time
import zmq
import pika
import json
import uuid
from executor import function_executor as fexec
import multiprocessing as mp
import logging
import socket
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

PROCESSES = 10 
TASK_COUNT = 100

class Worker(object):
    """Fetches a Task message from a messaging system 

    Attributes:
        mq: messaging system name, zmq or rabbitmq
        q_name: A queue name to push a Task message
        uid: a unique identifier of Worker object
        hostname: a system hostname
        receiver: a PULL socket of messaging system
        sender: a PUSH socket of messaging system
    """
    #mq = "zmq" or "rabbitmq"
    q_name = "task_queue"

    def __init__(self, mq_choice="zmq"):
        self.mq = mq_choice
        # Assign ID to each worker
        self.uid = str(uuid.uuid4())
        # hostname of worker
        self.hostname = socket.gethostname()
        func = getattr(self, "_init_{}".format(self.mq))
        func()

    def _init_zmq(self):
        # Create zmq context and tcp receiver/sender connections 
        self.context = zmq.Context()
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.connect("tcp://127.0.0.1:5557")
        # send results
        self.sender = self.context.socket(zmq.PUSH)
        self.sender.connect("tcp://127.0.0.1:5558")

    def _init_rabbitmq(self):
        # create RMQ channel 
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=self.q_name, durable=False)
        self.receiver = channel

    def recv(self):
        """Pulls a message from a queue"""
        func = getattr(self, "_recv_{}".format(self.mq))
        return func()

    def _recv_zmq(self):
        return self.receiver.recv_json()

    def _recv_rabbitmq(self):
        method_frame, header_frame, body = self.receiver.basic_get(self.q_name)
        if method_frame:
            self.receiver.basic_ack(method_frame.delivery_tag)
            return json.loads(body)

    def send(self, msg):
        """Pushes a (result) message to a separate queue"""
        func = getattr(self, "_send_{}".format(self.mq))
        func(msg)

    def _send_zmq(self, msg):
        self.sender.send_json(msg)

    def _send_rabbitmq(self, msg):
        #TBD
        print (msg)

if __name__ == "__main__":

    # instance 1) for each task we have one worker: assume 8 workers, 8 cpus

    # instance 2) we assign as many workers as we have tasks but only 
    # allow execution if enough cores available: cpu_count()
  

    CPUS = mp.cpu_count()
    p = mp.Pool(PROCESSES)
    print ('Creating pool with {} processes\n'.format(PROCESSES))

    obj = Worker()
    results = []
    #for i in range(TASK_COUNT):
    # TODO: (hlee) timeout for loop
    while True:
        # Receive 1 message
        msg = obj.recv()
        msg['worker_id'] = obj.uid
        msg['worker_hostname'] = obj.hostname
        r = p.apply_async(fexec, args=(msg,), callback=logging.debug)
        #results.append(r)
    """
    TODO: (hlee) callback function
    # Collect results and send back
    for i in results:
        x = (i.get())
        logging.debug(x)
        #obj.send(x)
    """

