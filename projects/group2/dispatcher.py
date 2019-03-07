import zmq
import pika
import json
import example_compute
from Task import Task
from operator import attrgetter

TOTAL_TASKS = 2 

class Dispatcher(object):
    mq = "zmq"
    # mq = "rabbitmq"
    q_name = "task_queue"

    def __init__(self):
        func = getattr(self, "init_{}".format(self.mq))
        func()

    def init_zmq(self):
        context = zmq.Context()
        zmq_socket = context.socket(zmq.PUSH)
        zmq_socket.bind("tcp://127.0.0.1:5557")
        self.mq_socket = zmq_socket

    def init_rabbitmq(self):
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        channel.queue_declare(queue=self.q_name, durable=False)
        self.mq_socket = channel

    def send(self, task_msg, iterate=10):
        # Type casting; Task -> python dict
        task_msg = task_msg.__dict__
        # Start your result manager and workers before you start your dispatchers
        for idx in range(iterate):
            task_msg['tid'] = idx
            self.mq_send(task_msg)

    def mq_send(self, msg):
        func = getattr(self, "{}_send".format(self.mq))
        func(msg)

    def zmq_send(self, msg):
        self.mq_socket.send_json(msg)

    def rabbitmq_send(self, msg):
        self.mq_socket.basic_publish(exchange='',
                      routing_key=self.q_name, 
                      body=json.dumps(msg),
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))

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
                  resources = 4)
            ]  

    obj = Dispatcher()
    tasks.sort(key=attrgetter('resources'))
    for task in tasks:
        obj.send(task)
