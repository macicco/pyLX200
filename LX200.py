#!/usr/bin/python
'''
LX200 command set

socat TCP:localhost:6666,reuseaddr pty,link=/tmp/lx200
https://github.com/peterjc/longsight/blob/master/telescope_server.py
'''

import socket
import sys
import select
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
    total_data=[]
    data=''
    while True:
            data=the_socket.recv(1)
	    if data=='':
		continue
	
            if End in data:
                total_data.append(data[:data.find(End)])
		cmd=''.join(total_data).replace('\n','').replace('\r','')
		if len(cmd)==0:
			continue
		else:
			break
	    else:
            	total_data.append(data)

    print "CMD parse:",cmd
    return cmd

#Function for handling connections. This will be used to create threads
def clientthread(conn):
    RUN=True
    data=''
    #Sending message to connected client
    #conn.send('LX200 mount controler:OK\n') #send only takes string
     
    #infinite loop so that function do not terminate and thread do not end.
    while RUN:
    	try:
        	ready_to_read, ready_to_write, in_error = \
        	    select.select([conn,], [conn,], [], 5)
    	except select.error:
         	# connection error event here, maybe reconnect
        	print 'connection error'
        	break

    	#if len(ready_to_read) > 0:
	if True:
	    	cmd=recv_end(conn)
		print "<-",cmd
		reply=conductor.cmd(cmd)
		print "->",reply
    		conn.send(str(reply)+'\n')

    	if len(ready_to_write) <= 0 :
        	print 'connection closed'
        	break


    #came out of loop
    conn.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
    conn.close()
    print "Disconnecting.."
 
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


