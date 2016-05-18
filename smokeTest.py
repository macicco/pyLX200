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


pi=math.pi
H=catalogues.HiparcosCatalogue()



zmqFlag=True #use ZMQ socket if False use INET sockets

if zmqFlag:
	context = zmq.Context()
	sock = context.socket(zmq.REQ)
	sock.connect ("tcp://localhost:%s" % servers['zmqEngineCmdPort'])
else:
	HOST = 'localhost'   # Symbolic name meaning all available interfaces
	PORT = servers['socketPort'] # Arbitrary non-privileged port
	# Create a TCP/IP socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Connect the socket to the port where the server is listening
	server_address = (HOST, PORT)
	print >>sys.stderr, 'connecting to %s port %s' % server_address
	sock.connect(server_address)


def drawCostellationsFigures(costellations=['Aur']):
	coords=[]
	figures=catalogues.CostellationFigures()
	#costellations=set(map(lambda x:x[0],figures))
	#if True:
	for costellation in costellations:
		print costellation
		data=filter(lambda x:x[0]==costellation,figures)[0]		
		data=list(group(data[2:],2))
		for s in data:	
			star1=H.search(s[0])
			star2=H.search(s[1])
			if star1!=None and star2!=None:
				npJ2000=ephem.Equatorial(star2[4],star2[5])
				np=ephem.Equatorial(npJ2000,epoch='2016.4')
				ra = np.ra
				dec =np.dec
				cmd1=str(ephem.hours(ra))
				cmd2=str(dec)
				coords.append([cmd1,cmd2])
	return coords

def recv():
	if zmqFlag:
		return sock.recv()
	else:
		return sock.recv(16)

def costellations():
	RUN=True
	while RUN:
		time.sleep(0.1)	
		coste=['Tau','Gem','Cnc','Leo','Vir','Lib','Sco','Sgr','Cap','Aqr','Psc','Ari']
		coords=drawCostellationsFigures(coste)
		try:
		  while True:
		     for coord in coords:
			print coord
			r_cmd=':Sr '+coord[0]
			print >>sys.stderr, 'sending "%s"' % r_cmd
			sock.send(r_cmd+'#')
			time.sleep(0.1)	
			data=recv()
			print >>sys.stderr, 'received "%s"' % data
			d_cmd=':Sd '+coord[1]
			print >>sys.stderr, 'sending "%s"' % d_cmd
			sock.send(d_cmd+'#')
			time.sleep(0.1)	
			data = recv()
			print >>sys.stderr, 'received "%s"' % data
		    	#sock.sendall(':Q#')
			sock.send(':MS#')
			data = recv()
	    		time.sleep(5)	

		finally:
			print >>sys.stderr, 'closing socket'
			sock.close()
			RUN=False

def testOvershoot():
		coords=[[]]

costellations()

