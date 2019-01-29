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

host = ''               
port = 10000

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host, port))
print("Server started on port: %s" %port)
s.listen(1)
print("Now listening...\n")
conn, addr = s.accept()
while True:

    print 'New connection from %s:%d' % (addr[0], addr[1])
    data = conn.recv(1024)
    print 'Data Received..\n', data
    cmd = data
    stdout=eval(compile(cmd, '<string>', 'eval'))
    serial = json.dumps(stdout)
    conn.send(serial)

def quit(connection):
    conn.close()
