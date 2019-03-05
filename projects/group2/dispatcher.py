import zmq
import pika
import json

class Dispatcher(object):
    mq = "zmq"
    mq = "rabbitmq"
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

    task = { 
            'function' : "example_compute.compute_flops",
            'params': [1, 2048],
            'resources': 1
            }

    obj = Dispatcher()
    obj.send(task)
