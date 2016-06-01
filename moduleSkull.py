#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
'''
Module Skeleton virtual class
'''

import time,datetime
import zmq
import json
from config import *


class module(object):
	def __init__(self,name,port,hubport=False):
		print "Creating module ",name
		self.modulename=name
		print name," listen CMDs on:",port
		self.zmqcontext = zmq.Context()
		if hubport:	    
			print name," sending CMDs to:",hubport
			self.hasParent=True
			self.hubCmdPort=hubport
		    	self.socketHUBCmd = self.zmqcontext.socket(zmq.REQ)
		    	self.socketHUBCmd.connect("tcp://localhost:%s" % self.hubCmdPort)
		else:
			self.hasParent=False
		self.CMDs={ 
  		":register": self.register, \
  		":registrar": self.registrar, \
  		":test": self.test, \
  		"!": self.exeModuleCmd \
		}
		self.myCmdPort=port
		self.modules={}
		self.RUN=True
		#self.socketStream = self.zmqcontext.socket(zmq.PUB)
		#self.socketStream.bind("tcp://*:%s" % servers['zmqStreamPort'])
	    	self.mySocketCmd = self.zmqcontext.socket(zmq.REP)
	    	self.mySocketCmd.bind("tcp://*:%s" % self.myCmdPort)
		self.zmqQueue()

	def addCMDs(self,CMDs):
		self.CMDs.update(CMDs)


	#this thread is responsible for all the 
	#CMD from other modules
	@threaded
	def zmqQueue(self):
	    while self.RUN:
		try:
	    		message = self.mySocketCmd.recv()
		except:
			print "Clossing ZMQ queue"
			self.mySocketCmd.close()
			return
		#print("Received request: %s" % message)

		#  Do some 'work'
		reply=self.cmd(message)

		#  Send reply back to client
    		self.mySocketCmd.send(str(reply))

	def registrar(self,arg):
		r=json.loads(arg)
		module=r['module']
		self.modules.pop(module,None)
		self.modules[module]={'name':r['module'],'port':r['port']}
		socketCmd = self.zmqcontext.socket(zmq.REQ)
		socketCmd.connect ("tcp://localhost:%s" % r['port'])
		self.modules[module]['CMDsocket']=socketCmd
		self.modules[module]['CMDs']=r['CMDs']
		#print self.modules[module]
		print module," sucesfully registed"
		return json.dumps({'OK':True})




	def listModules(self):
		for m in self.modules.keys():
			print m

	def exeModuleCmd(self,arg):
		s=arg.split()
		if len(s)==0:
			return 0
		module=s[0]
		if not (module in self.modules.keys()):
			print module,"Not such module"
			return 0
		cmd=arg[len(module):].strip()
		print "exec:",cmd,' on ',module,' from ',self.modulename
		self.modules[module]['CMDsocket'].send(cmd)
		reply=self.modules[module]['CMDsocket'].recv()
		return reply

	def register(self):
		modulecmd=str(self.CMDs.keys())
		cmdjson=json.dumps({'module':self.modulename,\
				    'port':self.myCmdPort,\
				    'CMDs':modulecmd})
		cmd=':registrar '+cmdjson
		self.socketHUBCmd.send(cmd)
		reply=json.loads(self.socketHUBCmd.recv())
		if reply['OK']:
			print self.modulename," CMD PORT:",self.myCmdPort
			print self.modulename," CMDs:",modulecmd

		
	def cmd(self,cmd):
                for c in self.CMDs.keys():
			l=len(c)
			if (cmd[:l]==c):
				arg=cmd[l:].strip()
				#print "K",c,"KK",cmd,"KKK",arg
				return self.CMDs[c](arg)
				break

		return self.cmd_dummy(cmd)



	def cmd_dummy(self,arg):
		print "DUMMY CMD:",arg
		return

	def test(self,arg):
		print "TEST CMD:",arg
		return

	def run(self):
	  	while self.RUN:
			time.sleep(1)

	def end(self):
	  	self.RUN=False


class engine(module):
	pass

class trackermodule(module):
	def cmd_info(self,arg):
		return "INFO"

	def __init__(self,name,port,hubport):
		super(trackermodule,self).__init__(name,port,hubport)
		CMDs={ 
		":info": self.cmd_info \
		}
		self.addCMDs(CMDs)
		self.register()


if __name__ == '__main__':
	port=7770
	trackerport=7771
  	e=engine('engine',port)
  	m=trackermodule('tracker',trackerport,port)
	e.listModules()
	print e.cmd('!tracker :info')
	try:
		m.run()
	except:
		m.end()
		e.end()
		e.zmqcontext.term()



