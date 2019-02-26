#!/bin/python
import sys
import os
import argparse
import  socket
import json

class Dirty_client():


    def client(self):

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ''
        port = 10000
        self.conn.connect((host, port))
    

    def serial_send(self):
	
	dic = { "modules" :"numpy","executable" : "numpy.sin(2+1)","arguments":" "}
	modl    = dic['modules']
        execut  = dic['executable']
        args    = dic['arguments']
	print 'Sent Module   :' ,modl
	print 'Sent Executable   :' ,execut
	print 'Sent Arguments   :' ,args
	if not args:
 
        	cud = [(modl),(execut)]
		serial = json.dumps(cud)
        	self.conn.sendall(serial)
        	print 'Data sent !\n'
	else :
		cud=[(modl),(execut),(args)]
        	serial = json.dumps(cud)
        	self.conn.sendall(serial)
        	print 'Data sent !\n'

    def serial_recv(self):

        print 'waiting for reply....\n'
        data = self.conn.recv(1024)

        if data :
                print 'Data recieved from the server !'
                stdout = json.loads(data)
                print stdout
        else :
                print 'No data recieved back !'
                sys.exit()
        self.conn.close()


cc=Dirty_client()   
cc.client()
cc.serial_send()
cc.serial_recv()  




