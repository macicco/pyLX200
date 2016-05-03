#!/usr/bin/python

import socket
import sys
import select
import time
import catalogues
import ephem
import math
from thread import *

pi=math.pi
H=catalogues.HiparcosCatalogue()

HOST = 'localhost'   # Symbolic name meaning all available interfaces
PORT = 6666 # Arbitrary non-privileged port

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (HOST, PORT)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

RUN=True


def group(lst, n):
  for i in range(0, len(lst), n):
    val = lst[i:i+n]
    if len(val) == n:
      yield tuple(val)


def drawCostellationsFigures(costellation='Boo'):
	coords=[]
	figures=catalogues.CostellationFigures()
	costellations=set(map(lambda x:x[0],figures))
	if True:
	#for costellation in costellations:
		data=filter(lambda x:x[0]==costellation,figures)[0]		
		data=list(group(data[2:],2))
		for s in data:	
			star1=H.search(s[0])
			star2=H.search(s[1])
			if star1!=None and star2!=None:
				costellation_line=((star1[4]*180/pi,star1[5]*180/pi),(star2[4]*180/pi,star2[5]*180/pi))
				#print costellation_line
				ra=ephem.degrees(star2[4])
				dec=ephem.degrees(star2[5])
				cmd1=str(ephem.hours(ra))
				cmd2=str(dec)
				coords.append([cmd1,cmd2])
	return coords


while RUN:
 time.sleep(0.1)	
 coords=drawCostellationsFigures()
 try:
    
    # Send data
    messages =[chr(6),':info',':GR',':Sr 01:00:00',':Sd 35:00',':MS'] 
   
    #for msg in messages:	
    for coord in coords:
	    print coord
	    r_cmd=':Sr '+coord[0]
	    print >>sys.stderr, 'sending "%s"' % r_cmd
	    sock.sendall(r_cmd+'#')
	    time.sleep(0.1)	
	    data = sock.recv(16)
            print >>sys.stderr, 'received "%s"' % data
	    d_cmd=':Sd '+coord[1]
	    print >>sys.stderr, 'sending "%s"' % d_cmd
	    sock.sendall(d_cmd+'#')
	    time.sleep(0.1)	
	    data = sock.recv(16)
            print >>sys.stderr, 'received "%s"' % data
	    time.sleep(5)	
	    sock.sendall(':MS#')


 finally:
    print >>sys.stderr, 'closing socket'
    sock.close()
    RUN=False
