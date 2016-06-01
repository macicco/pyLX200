#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import zmq
import time,datetime
import ephem
import json
import tle
import math

from config import *



class tracker:
	def __init__(self):
		self.last={}
		self.CMDs={ 
		"@readTLEfile":self.readTLEfile,  \
		"@loadTLE": self.loadTLE,  \
		"@setTLE2follow": self.setTLE2follow,  \
		":test": self.test,  \
		}
		self.timestep=0.1
		self.context = zmq.Context()
		self.socketStream = self.context.socket(zmq.SUB)
		#CONFLATE: get only one message 
		#(do not work with the stock version of zmq, works from ver 4.1.4)
		self.socketStream.setsockopt(zmq.CONFLATE, 1)
		self.socketStream.connect ("tcp://localhost:%s" % servers['zmqStreamPort'])
		self.socketStream.setsockopt(zmq.SUBSCRIBE, 'values')
	
		self.socketEngineCmd = self.context.socket(zmq.REQ)
		self.socketEngineCmd.connect ("tcp://localhost:%s" % servers['zmqEngineCmdPort'])
		self.RUN=True		
		self.zmqQueue()
		self.register()
		self.gearInit()
		self.observerInit()
		self.TLEs=tle.TLEhandler()
		self.a=0
		self.go2rise=False



	def readTLEfile(self,arg):
		pass

	def loadTLE(self,arg):
		pass

	def setTLE2follow(self,arg):
		pass


	def test(self,arg):
		print "TEST"
		return

	def register(self):
		modulecmd=str(self.CMDs.keys())
		cmdjson=json.dumps({'module':'tracker','port':servers['zmqTrakerCmdPort'],'moduleCMDs':modulecmd})
		cmd='@registrar '+cmdjson
		print cmd
		self.socketEngineCmd.send(cmd)
		reply=json.loads(self.socketEngineCmd.recv())
		print reply

	def observerInit(self):
		self.socketEngineCmd.send('@getObserver')
		reply=json.loads(self.socketEngineCmd.recv())
		self.observer=ephem.Observer()
		self.observer.lat=ephem.degrees(str(reply['lat']))
		self.observer.lon=ephem.degrees(str(reply['lon']))
		self.observer.horizon=ephem.degrees(str(reply['horizon']))
		self.observer.elev=reply['elev']
		self.observer.temp=reply['temp']
		self.observer.compute_pressure()

	def gearInit(self):
		self.socketEngineCmd.send('@getGear')
		reply=json.loads(self.socketEngineCmd.recv())
		self.pointError=ephem.degrees(str(reply['pointError']))
		print self.pointError
		

	def trackSatellite(self,sat):
		error=self.pointError
		satRA,satDEC = self.satPosition(sat)
		vsatRA,vsatDEC = self.satSpeed(sat)
		self.sendTrackSpeed(vsatRA,vsatDEC)
		errorRA=ephem.degrees(abs(satRA-self.RA))
		errorDEC=ephem.degrees(abs(satDEC-self.DEC))
		if abs(errorRA)>=error or abs(errorDEC)>=error:
			print "Too much error. Slewing",errorRA,errorDEC,str(error)
			self.sendSlew(satRA,satDEC)
		else:
			pass
			print "OK",(errorRA),(errorDEC),str(error)

	def circle(self,re,dec,r,v):
		#not finished
		self.a=v*self.timestep+self.a
		vRA=r*math.sin(self.a)
		vDEC=r*math.cos(self.a)
		self.sendTrackSpeed(vRA,vDEC)


	def sendSlew(self,RA,DEC):
		self.socketEngineCmd.send(':Sr '+str(RA))
		reply=self.socketEngineCmd.recv()
		self.socketEngineCmd.send(':Sd '+str(DEC))
		reply=self.socketEngineCmd.recv()
		self.socketEngineCmd.send(':MS')
		reply=self.socketEngineCmd.recv()

	def sendTrackSpeed(self,vRA,vDEC):
		self.socketEngineCmd.send('@setTrackSpeed '+str(vRA)+' '+str(vDEC))
		reply=self.socketEngineCmd.recv()

	@threaded
	def zmqQueue(self):
	    socketTrakerCmd = self.context.socket(zmq.REP)
	    socketTrakerCmd.bind("tcp://*:%s" % servers['zmqTrackerCmdPort'])
	    print "tracker CMD queue init"
	    while self.RUN:
		print "waiting"
		try:
	    		message = socketTrakerCmd.recv()
		except:
			print "Clossing ZMQ queue"
			socketTrakerCmd.close()
			return
		#print("Received request: %s" % message)
		print "zmqqqqq"
		#  Do some 'work'
		reply=self.cmd(message)

		#  Send reply back to client
    		socketTrakerCmd.send(str(reply))

	def cmd(self,cmd):
                for c in self.CMDs.keys():
			l=len(c)
			if (cmd[:l]==c):
				arg=cmd[l:].strip()
				print "K",c,"KK",cmd,"KKK",arg
				return self.CMDs[c](arg)
				break

		return self.cmd_dummy(cmd)

	def cmd_dummy(self,arg):
		print "DUMMY CMD:",arg
		return 

	def run(self):
		while self.RUN:
			time.sleep(self.timestep)
			self.values=self.lastValue()
			#Call to the RA/DEC primitives for accuracy
			self.socketEngineCmd.send('@getRA')
			self.RA=ephem.hours(self.socketEngineCmd.recv())
			self.socketEngineCmd.send('@getDEC')
			self.DEC=ephem.degrees(self.socketEngineCmd.recv())
			#self.trackSatellite('METEOSAT-7')
			#self.trackSatellite('KAZSAT 3')
			#self.trackSatellite('ISS')
			#self.trackSatellite('DEIMOS 2')	
			#self.circle(0,0,ephem.degrees('0:30:00'),0.1)

	def satPosition(self,sat):
			observer=self.observer
			s=self.TLEs.TLE(sat)
			observer.date=ephem.Date(datetime.datetime.utcnow())
			s.compute(observer)
			ra,dec=(s.ra,s.dec)
			if engine['overhorizon'] and s.alt<0:
				if engine['go2rising']:
					info=observer.next_pass(s)
					ra,dec=observer.radec_of(info[1],observer.horizon)			
					print "Next pass",info,ra,dec
				else:
					ra,dec=(self.RA,self.DEC)
			return ra,dec


	def satSpeed(self,sat):
			seconds=self.timestep
			observer=self.observer
			s=self.TLEs.TLE(sat)
			observer.date=ephem.Date(datetime.datetime.utcnow())
			s.compute(observer)
			RA0=s.ra
			DEC0=s.dec
			observer.date=observer.date+ephem.second*seconds
			s.compute(observer)
			RA1=s.ra
			DEC1=s.dec
			vRA=ephem.degrees((RA1-RA0)/seconds-ephem.hours('00:00:01'))
			vDEC=ephem.degrees((DEC1-DEC0)/seconds)
			if engine['overhorizon'] and s.alt<0:
				vRA,vDEC=(0,0)
  			return (vRA,vDEC)

	def lastValue(self):
		self.last
		try:
			m= self.socketStream.recv(flags=zmq.NOBLOCK)
			topic, msg  = demogrify(m)
			self.last=msg
		except:
			msg=self.last
    		return msg

	def end(self):
		self.RUN=False

if __name__ == '__main__':
	t=tracker()
	t.run()
	try:
		t.run()
	except:
		t.end()

	

