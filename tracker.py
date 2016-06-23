#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
import zmq
import time,datetime
import ephem
import json
import tle
import math
import moduleSkull
from config import *



class tracker(moduleSkull.module):
	def __init__(self):
		port=servers['zmqTrackerCmdPort']
		hubport=servers['zmqEngineCmdPort']
		super(tracker,self).__init__('tracker',port,hubport)
		CMDs={ 
		"@readTLEfile":self.readTLEfile,  \
		"@loadTLE": self.loadTLE,  \
		"@setTLE2follow": self.setTLE2follow  \
		}
		self.register()
		self.timestep=0.1
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


	def observerInit(self):
		self.socketHUBCmd.send('@getObserver')
		reply=json.loads(self.socketHUBCmd.recv())
		self.observer=ephem.Observer()
		self.observer.lat=ephem.degrees(str(reply['lat']))
		self.observer.lon=ephem.degrees(str(reply['lon']))
		self.observer.horizon=ephem.degrees(str(reply['horizon']))
		self.observer.elev=reply['elev']
		self.observer.temp=reply['temp']
		self.observer.compute_pressure()

	def gearInit(self):
		self.socketHUBCmd.send('@getGear')
		reply=json.loads(self.socketHUBCmd.recv())
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
		self.socketHUBCmd.send(':Sr '+str(RA))
		reply=self.socketHUBCmd.recv()
		self.socketHUBCmd.send(':Sd '+str(DEC))
		reply=self.socketHUBCmd.recv()
		self.socketHUBCmd.send(':MS')
		reply=self.socketHUBCmd.recv()

	def sendTrackSpeed(self,vRA,vDEC):
		self.socketHUBCmd.send('@setTrackSpeed '+str(vRA)+' '+str(vDEC))
		reply=self.socketHUBCmd.recv()




	def run(self):
		while self.RUN:
			time.sleep(self.timestep)
			#self.values=self.lastValue()
			#Call to the RA/DEC primitives for accuracy
			self.socketHUBCmd.send('@getRA')
			self.RA=ephem.hours(self.socketHUBCmd.recv())
			self.socketHUBCmd.send('@getDEC')
			self.DEC=ephem.degrees(self.socketHUBCmd.recv())
			#self.trackSatellite('METEOSAT-7')
			#self.trackSatellite('KAZSAT 3')
			self.trackSatellite('ISS')
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



if __name__ == '__main__':
	t=tracker()
	t.run()
	exit()
	try:
		t.run()
	except:
		t.end()

	

