import sys
import time
import zmq
import pika
import json
import uuid
from executor import function_executor as fexec
import multiprocessing as mp
import logging
import socket # gethostname
import yaml
import argparse
from Task import Task
# grpc
import func_exec_pb2
import func_exec_pb2_grpc
from example_compute import compute_flops

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
        logging.info("mq:{}".format(self.mq))
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

    def _init_rpyc(self):
        from rpc_service import FuncExecRPyC
        t = FuncExecRPyC()
        t.server.start()

    def _init_grpc(self):
        from concurrent import futures
        import grpc

        server = grpc.server(futures.ThreadPoolExecutor(max_workers=PROCESSES))
        func_exec_pb2_grpc.add_FuncExecServicer_to_server(FuncExecServicer(), server)
        server.add_insecure_port('localhost:50051')
        server.start()
        try:
            while True:
                time.sleep(60 * 60 * 24)
        except KeyboardInterrupt:
            server.stop(0)

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
        else:
            return {}

    def _recv_grpc(self):
        return {}

    def send(self, msg):
        """Pushes a (result) message to a separate queue"""
        func = getattr(self, "_send_{}".format(self.mq))
        func(msg)

    def _send_zmq(self, msg):
        self.sender.send_json(msg)

    def _send_rabbitmq(self, msg):
        #TBD
        print (msg)

    def _send_grpc(self, msg):
        loggin.debug(msg)

    def set_argument(self):
        parser = argparse.ArgumentParser("Python function worker")
        parser.add_argument("--yaml", help="yaml file to load")
        args = parser.parse_args()
        self.args = args
        if args.yaml:
            with open(args.yaml) as f:
                data = yaml.load(f, Loader=yaml.Loader)
            # Reset mq from yaml
            if self.mq != data['mq']:
                self.__init__(data['mq'])

# For grpc
class FuncExecServicer(func_exec_pb2_grpc.FuncExecServicer):

    def GetTask(self, request, context):
        logging.debug("start:{}".format(time.time()))
        logging.debug("function call:{}({})".format(request.fname, request.params))
        res = eval("{}({})".format(request.fname, request.params))
        logging.debug("end:{}".format(time.time()))
        return func_exec_pb2.TaskReply(result='%s' % res)

    def RunExec(self, request, context):
        logging.debug("allocation by exec:{}={}".format(request.fname, request.params))
        exec("{}={}".format(request.fname, request.params))
        return func_exec_pb2.TaskReply(result='')


if __name__ == "__main__":

    # instance 1) for each task we have one worker: assume 8 workers, 8 cpus

    # instance 2) we assign as many workers as we have tasks but only 
    # allow execution if enough cores available: cpu_count()
  

    CPUS = mp.cpu_count()
    p = mp.Pool(PROCESSES)
    print ('Creating pool with {} processes\n'.format(PROCESSES))

    obj = Worker()
    # Read yaml from cmd if given
    obj.set_argument()
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

