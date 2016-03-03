#!/usr/bin/python
'''
LX200 command set

socat TCP:localhost:6666,reuseaddr pty,link=/tmp/lx200
https://github.com/peterjc/longsight/blob/master/telescope_server.py
'''

import socket
import sys

from thread import *

import LX200CMD
 
HOST = ''   # Symbolic name meaning all available interfaces
PORT = 6666 # Arbitrary non-privileged port
 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'Starting LX200 mount controler.'
print 'Socket created',HOST+":",str(PORT)

#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bind complete'
 
#Start listening on socket
s.listen(10)
print 'Socket now listening'
 
#Start LX200 master
conductor=LX200CMD.lx200conductor()

#End='something useable as an end marker'
def recv_end(the_socket):
    End='#'
    total_data=[];data=''
    while True:
            data=the_socket.recv(1)
	    if data=='':
		continue
	    print repr(data)
            if End in data:
		print "end found"
                total_data.append(data[:data.find(End)])
                break
	    else:
            	total_data.append(data)

    return ''.join(total_data)

#Functihttps://github.com/peterjc/longsight/blob/master/telescope_server.pyon for handling connections. This will be used to create threads
def clientthread(conn):
    RUN=True
    #Sending message to connected client
    #conn.send('LX200 mount controler:OK\n') #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while RUN:
	try:
	        #Receiving from client
		while True:
		        data += conn.recv(16)
			if not data:
		                break
			while data:
				while data[0:1] == "#"
					data=data[1:]
				if not data:
					break
				if "#" in data:
					cmd=data[:data.index("#")]
					break
		#data=recv_end(conn)
		print "<-",cmd
		reply=conductor.cmd(cmd)
		print "->",reply
    		conn.sendall(str(reply)+'\n')
	except:
		print "exit...."
		RUN=False

     
    #came out of loop
    conn.close()
 
#now keep talking with the client
RUN=True
while RUN:
  try:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))

  except:
    RUN=False
	
s.close()
conductor.end()


