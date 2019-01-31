#!/bin/python
import sys
import os
import time
import argparse
import ConfigParser
from subprocess import Popen, PIPE
import  socket
import subprocess
from math import *
import json
import pickle


class Dirty_server():


    def server(self):

        host = ''
        port = 10000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        print("Server started on port: %s" %port)
        s.listen(1)
        print("Now listening...\n")
        self.conn, self.addr = s.accept()

    def exe(self):


        print 'Starting New connection from %s:%d' % (self.addr[0],self.addr[1])
        data = self.conn.recv(1024)
        print 'Data received..  ', data
        cmd = data
        #stdout=execfile(cmd)
        stdout=eval(compile(cmd, '<string>', 'eval'))

        serial = json.dumps(stdout)
        print 'Sending the result back ....\n'
        self.conn.send(serial)
        self.conn.close()
        print 'closing connection...\n'



ss=Dirty_server()
ss.server()
ss.exe()


