import zmq
import pika
from Task import Task
import sys
import json
import yaml
import uuid
import logging
import time
import argparse
from operator import attrgetter
from datetime import datetime
# grpc
import func_exec_pb2
import func_exec_pb2_grpc


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Dispatcher(object):
    """Dispater of tasks by messaging system
    
    Attributes:
        mq: messaging system name, zmq or rabbitmq
        q_name: A queue name to push a Task message
        mq_socket: a socket of messaging system
        tid: a task id (auto-increment)
        task: A list of Task object to dispatch
        response: A list of Task response only for grpc
    """
    uid = str(uuid.uuid4())
    #mq = "zmq" or "rabbitmq"
    q_name = "task_queue"
    tid = 0
    task = []
    response = []

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

    def _init_rpyc(self):
        import rpyc
        self.mq_socket = rpyc.classic.connect("localhost")

    def _init_grpc(self):
        import grpc
        self.mq_socket = grpc.insecure_channel('localhost:50051')

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
            task_msg['scheduled'] = str(time.time())
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

    def _rpyc_send(self, msg):
        if isinstance(msg['params'], list):
            params = [ str (x) for x in msg['params'] ]
        else:
            params = msg['params']
        sep = msg['function'].split(".", 1)
        function = msg['function']
        if len(sep) > 1:
            try:
                self.mq_socket.execute("import {}".format (sep[0]))
            except:
                pass
        if params:
            self.mq_socket.execute("{}({})".format(msg['function'], ','.join(params)))
        else:
            self.mq_socket.execute("{}".format(msg['function']))

    def _grpc_send(self, msg):
        stub = func_exec_pb2_grpc.FuncExecStub(self.mq_socket)
        response = stub.GetTask.future(func_exec_pb2.TaskRequest(fname=msg['function'],params=(",".join(msg['params']))))
        self.response.append(response)

    def new_tid(self):
        self.tid += 1
        return self.tid

    def set_argument(self):
        parser = argparse.ArgumentParser("Python function dispatcher")
        parser.add_argument("--yaml", help="yaml file to load")
        args = parser.parse_args()
        self.args = args
        if args.yaml:
            with open(args.yaml) as f:
                data = yaml.load(f, Loader=yaml.Loader)
            # Reset mq from yaml
            if self.mq != data['mq']:
                self.__init__(data['mq'])
            self.task = data['task']
            return data['task']
        return None

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
    # Overriden by cmd params
    tasks_from_yaml = obj.set_argument()
    if tasks_from_yaml:
        tasks = tasks_from_yaml
    tasks.sort(key=attrgetter('resources'))
    for task in tasks:
        obj.send(task)

    if obj.mq == "grpc":
        for response in obj.response:
            logging.info("response:{}".format(response.result()))
            # REMOVE response.. pop
