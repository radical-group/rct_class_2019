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


conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
port = 10000

conn.connect((host, port))
while True:
    path= '/home/aymenlinux/RCT-EXE/cud.txt'
    config = ConfigParser.ConfigParser()
    config.read(path)
    prog=config.get('cud', 'executable')
    #prog1=config.get('cud','arguments')
    shell = prog
    conn.send(shell)
    data = conn.recv(1024)
    stdout = json.loads(data)
    print stdout                             

def quit(connection):
    conn.close()
