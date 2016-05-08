#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
'''
LX200 command set
'''
import ephem
import time,datetime
import threading
import ramps
import tle
import math
import zmq
import json
from config import *


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class commands():
	def __init__(self):
		print "Conductor create"
		self.CMDs={ 
		chr(6):self.cmd_ack,  \
		":info": self.cmd_info,  \
  		":FirmWareDate": self.cmd_firware_date,  \
  		":GVF": self.cmd_firware_ver,  \
  		":V": self.cmd_firware_ver,  \
  		":GVD": self.cmd_firware_date,  \
  		":GC": self.cmd_getLocalDate,  \
  		":GL": self.cmd_getLocalTime,  \
  		":GS": self.cmd_getSideralTime,  \
  		":Sr": self.cmd_setTargetRA,  \
  		":Sd": self.cmd_setTargetDEC,  \
  		":MS": self.cmd_slew,  \
  		":Q":  self.cmd_stopSlew,  \
  		":Gr": self.cmd_getTargetRA,  \
  		":Gd": self.cmd_getTargetDEC,  \
  		":GR": self.cmd_getTelescopeRA,  \
  		":GD": self.cmd_getTelescopeDEC,  \
  		":RS": self.cmd_setMaxSlewRate,  \
  		":RM": self.cmd_slewRate,  \
  		":Me": self.cmd_pulseE,  \
  		":Mw": self.cmd_pulseW,  \
  		":Mn": self.cmd_pulseN,  \
  		":Ms": self.cmd_pulseS,  \
  		":CM": self.cmd_align2target,  \
  		"@getObserver": self.getObserver
		}
		self.targetRA=0		
		self.targetDEC=0
		self.RA=0		
		self.DEC=0
		self.RUN=True
		self.observerInit()
		self.pulseStep=ephem.degrees('00:00:01')
		a=ephem.degrees('00:20:00')
		self.m=ramps.mount(a)
		vRA=ephem.hours("00:00:01")
		vDEC=ephem.degrees("00:00:00")
		self.m.trackSpeed(vRA,vDEC)

		self.zmqcontext = zmq.Context()

		self.socketStream = self.zmqcontext.socket(zmq.PUB)
		self.socketStream.bind("tcp://*:%s" % zmqStreamPort)

		self.zmqQueue()


	#this thread is responsible for all the 
	#external CMD
	@threaded
	def zmqQueue(self):
	    socketCmd = self.zmqcontext.socket(zmq.REP)
	    socketCmd.bind("tcp://*:%s" % zmqCmdPort)
	    while self.RUN:
		try:
	    		message = socketCmd.recv()
		except:
			print "Clossing ZMQ queue"
			socketCmd.close()
			return
		print("Received request: %s" % message)

		#  Do some 'work'
		reply=self.cmd(message)

		#  Send reply back to client
    		socketCmd.send(str(reply))

	def observerInit(self):
		self.observer=ephem.Observer()
		self.observer.lat=here['lat']
		self.observer.lon=here['lon']
		self.observer.horizon=here['horizon']
		self.observer.elev=here['elev']
		self.observer.temp=here['temp']
		self.observer.compute_pressure()

	def getObserver(self,arg):
		observer = {'lat':self.observer.lat,'lon':self.observer.lon,\
				'horizon':self.observer.horizon,\
				'elev':self.observer.elev,'temp':self.observer.temp}
		return json.dumps(observer)

    	def end(self):
        	print "Ending.."
		self.RUN=False
		self.m.end()
		self.zmqcontext.term()


		

	def run(self):
		#self.go2ISS()
		#self.ISSspeed()
	  	while self.RUN:
			time.sleep(0.1)
			#update 
			self.observer.date=ephem.Date(datetime.datetime.utcnow())
			sideral=self.observer.sidereal_time()
			ra=ephem.hours(sideral-self.m.axis1.beta).norm
			if ra==ephem.hours("24:00:00"):
				ra=ephem.hours("00:00:00")
			self.RA=ra
			self.DEC=ephem.degrees(self.m.axis2.beta)
			msg = {'time':str(self.observer.date),'LST':str(sideral),\
				'RA':str(self.RA),'DEC':str(self.DEC),\
				'targetRA':str(self.targetRA),'targetDEC':str(self.targetDEC),\
				'speedRA':str(self.m.axis1.v),'speedDEC':str(self.m.axis2.v),\
				'trackingSpeedRA':str(self.m.axis1.vtracking),'trackingSpeedDEC':str(self.m.axis2.vtracking),\
				'slewendRA':str(self.m.axis1.slewend),'slewendDEC':str(self.m.axis2.slewend)\
				}
			self.socketStream.send(mogrify('values',msg))

			#self.go2ISS()
			#self.ISSspeed()
			#print self.iss.ra,self.iss.dec

			#print self.RA,self.DEC

		self.end()
		print "MOTORS STOPPED"

	def go2ISS(self):
			observer=self.observer
			observer.date=ephem.Date(datetime.datetime.utcnow())
			self.iss.compute(observer)
			self.targetRA=self.iss.ra
			self.targetDEC=self.iss.dec
			self.cmd_slew('')
  			return "target#"

	def ISSspeed(self):
			observer=self.observer
			observer.date=ephem.Date(datetime.datetime.utcnow())
			self.iss.compute(self.observer)
			RA0=self.iss.ra
			DEC0=self.iss.dec
			observer.date=observer.date+ephem.second
			self.iss.compute(observer)
			RA1=self.iss.ra
			DEC1=self.iss.dec
			vRA=-(RA1-RA0)
			vDEC=DEC1-DEC0
			self.m.trackSpeed(vRA,vDEC)
  			return "target#"

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



	def cmd_ack(self,arg):
		return "P"

	def cmd_info(self,arg):
		return "pyLX200 driver#"

	def cmd_firware_date(self,arg):
		return "01/02/2016#"

	def cmd_firware_ver(self,arg):
		return "LX200 Master. Python mount controler. Ver 0.1#"

	def cmd_getLocalDate(self,arg):
		return time.strftime("%m/%d/%y")+'#'
	
	def cmd_getLocalTime(self,arg):
		return time.strftime("%H:%M:%S")+'#'

	def cmd_getSideralTime(self,arg):
		sideralTime=self.observer.sidereal_time()
		return str(sideralTime)+'#'

	def cmd_getTargetRA(self,arg):
		return str(self.targetRA)+'#'

	def cmd_getTargetDEC(self,arg):
		return str(self.targetDEC)+'#'

	def cmd_setTargetRA(self,arg):
		self.targetRA=ephem.hours(arg)
		return 1

	def cmd_setTargetDEC(self,arg):
		arg=arg.replace('*',':')
		arg=arg.replace(chr(223),':')
		arg=arg.replace('’',':')
		self.targetDEC=ephem.degrees(arg)
		return 1

	def cmd_align2target(self,arg):
		ra=self.hourAngle(self.targetRA)
		self.m.sync(ra,self.targetDEC)
		return "target#"

	def cmd_slew(self,arg):
		ra=self.hourAngle(self.targetRA)
		print "slewing to:",ra,self.targetDEC," from:",self.hourAngle(self.RA),self.DEC
		self.m.slew(ra,self.targetDEC)
		#return values 0==OK, 1 == below Horizon
		return "0#"

	def hourAngle(self,ra):
		self.observer.date=ephem.now()
		sideral=self.observer.sidereal_time()
		ra_=ephem.hours(sideral-ra).znorm
		if ra_==ephem.hours("24:00:00"):
			ra=ephem.hours("00:00:00")
		return ra_		

	def cmd_stopSlew(self,arg):
		self.m.stopSlew()
		return 1

	def track(self):
		vRA=ephem.hours("00:00:01")
		vDEC=ephem.degrees("00:00:00")
		self.m.track(vRA,vDEC)
		return
		


	def cmd_getTelescopeRA(self,arg):
		self.observer.date=ephem.Date(datetime.datetime.utcnow())
		sideral=self.observer.sidereal_time()
		ra=ephem.hours(sideral-self.m.axis1.beta).norm
		if ra==ephem.hours("24:00:00"):
			ra=ephem.hours("00:00:00")
		self.RA=ra
		data=str(self.RA)
		H,M,S=data.split(':')
		H=int(H)
		M=int(M)
		S=round(float(S))
		d="%02d:%02d:%02d"  % (H,M,S)
		return d+'#'

	def cmd_getTelescopeDEC(self,arg):
		sign=math.copysign(1,self.m.axis2.beta)	
		self.DEC=ephem.degrees(self.m.axis2.beta)
		data=str(self.DEC)
		D,M,S=data.split(':')
		if  D[0]=='-':
			sign='-'
		else:
			sign='+'
		D=int(D)
		M=int(M)
		S=round(float(S))
		d="%s%02d*%02d:%02d"  % (sign,abs(D),M,S)
		d=d.replace('*',chr(223))
		return d+'#'

    	def cmd_pulseE(self,arg):
		self.targetRA=self.targetRA+self.pulseStep
		self.cmd_slew('')

    	def cmd_pulseW(self,arg):
		self.targetRA=self.targetRA-self.pulseStep
		self.cmd_slew('')

    	def cmd_pulseN(self,arg):
		self.targetDEC=self.targetDEC+self.pulseStep
		self.cmd_slew('')

    	def cmd_pulseS(self,arg):
		self.targetDEC=self.targetDEC-self.pulseStep
		self.cmd_slew('')

	def cmd_setMaxSlewRate(self,arg):
		return 1

	def cmd_slewRate(self,arg):
		return 1




if __name__ == '__main__':
  	m=commands()
	#m.run()
	try:
		m.run()
	except:
		m.end()



