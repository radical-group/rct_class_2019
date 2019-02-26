#!/bin/python

import sys
import os
import argparse
import socket
import json
import pickle
import ast 
import importlib 

class func_executor():
   

    def server(self):

        host = ''
        port = 10000
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        print("Server started on port: %s" %port)
        s.listen(1)
        print("Now listening...\n")
        self.conn, self.addr = s.accept()
	print 'Starting New connection from %s:%d' % (self.addr[0],self.addr[1])

    def recv(self):

        self.rec_data = self.conn.recv(1024)
	print 'Received data  :',self.rec_data


    def import_module(self,mod):

        exec "import {}".format(mod)
    	print mod,'module loaded\n'

	
    def executor(self):
	
        data=json.loads(self.rec_data)
	mod=data[0]
	print 'Data received & executing\n'
	cmd = (data[1])
        std = eval(compile(cmd, '<string>', 'eval'))
        serial = json.dumps(std)
        print ('Sending the result back ...')
        self.conn.send(serial)
        self.conn.close()
        print ('closing connection...')

