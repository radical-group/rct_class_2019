import zmq
import pika
import sys
import json
import uuid
import logging
from Task import Task
from operator import attrgetter
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Dispatcher(object):
    """Dispater of tasks by messaging system
    
    Attributes:
        mq: messaging system name, zmq or rabbitmq
        q_name: A queue name to push a Task message
        mq_socket: a socket of messaging system
    """
    uid = str(uuid.uuid4())
    #mq = "zmq" or "rabbitmq"
    q_name = "task_queue"
    tid = 0

    def __init__(self, mq_choice="zmq"):
        """Inits message queue by a user choice, zmq (Default) or rabbitmq """
        self.mq = mq_choice
        func = getattr(self, "_init_{}".format(self.mq))
        func()

    def _init_zmq(self):
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://127.0.0.1:5557")
        self.mq_socket = zmq_socket

    def _init_rabbitmq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=self.q_name, durable=False)
        self.mq_socket = channel

    def send(self, task_msg, iterate=1):
        """Sends Task to a queue 

        Args:
            task_msg (Task): A Task object
            iterate (int): A number of duplicated messages for concurrency test
        
        """
        # Type casting; Task -> python dict
        task_msg = task_msg.__dict__
        task_msg['dispatcher_id'] = self.uid
        # Start your result manager and workers before you start your dispatchers
        for idx in range(iterate):
            task_msg['task_id'] = self.new_tid()
            task_msg['scheduled'] = str(datetime.now())
            logging.debug("msg pushed:{} to {}".format(task_msg, self.q_name))
            self.mq_send(task_msg)

    def mq_send(self, msg):
        func = getattr(self, "_{}_send".format(self.mq))
        func(msg)

    def _zmq_send(self, msg):
        self.mq_socket.send_json(msg)

    def _rabbitmq_send(self, msg):
        self.mq_socket.basic_publish(exchange='',
                      routing_key=self.q_name, 
                      body=json.dumps(msg),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

    def new_tid(self):
        self.tid += 1
        return self.tid

if __name__ == "__main__":

    tasks = [
                Task(function  = "example_compute.compute_flops", 
                  params    = [1, 2048],
                  resources = 1), 
                Task(function  = "example_compute.compute_flops", 
                  params    = [1, 4096],
                  resources = 2), 
                Task(function  = "example_compute.compute_flops", 
                  params    = [1, 8192],
                  resources = 4),
                Task(function  = "example_compute.compute_flops", 
                  params    = [1, 8192],
                  resources = 8)
            ]  

    obj = Dispatcher()
    tasks.sort(key=attrgetter('resources'))
    for task in tasks:
        obj.send(task)
