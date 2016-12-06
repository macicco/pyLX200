#!/usr/bin/python

import socket
import sys
import select
import time
import catalogues
import ephem
import math
import zmq
from config import *



	context = zmq.Context()
	sock = context.socket(zmq.REQ)
	sock.connect ("tcp://localhost:%s" % servers['zmqEngineCmdPort'])

			vRA='-00:00:15'
			vDEC='00:00:00'
			sock.send('@setTrackSpeed '+str(vRA)+' '+str(vDEC))
			reply=sock.recv()

			sock.send(r_cmd+'#')
			time.sleep(0.1)	
			data=sock.recv()
			sock.close()

