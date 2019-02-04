#!/bin/python
import sys
import os
import time
import argparse
import ConfigParser
from subprocess import Popen, PIPE
import  socket
import subprocess
import json

class Dirty_client():


    def client(self):

        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = ''
        port = 10000
        self.conn.connect((host, port))
    

    def serial_send(self):

        path= '/home/aymenlinux/RCT-EXE/cud.txt'
        config = ConfigParser.ConfigParser()
        config.read(path)
        prog=config.get('cud', 'executable')
        #prog1=config.get('cud','arguments')
        shell = prog
        self.conn.send(shell)
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




