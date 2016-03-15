#!/usr/bin/python
# -*- coding: iso-8859-15 -*-
'''
LX200 command set
'''
import ephem
import time,datetime
import threading
import ramps
import math

def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()
    return wrapper

class lx200conductor():
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
  		":Me": self.cmd_pulseE,  \
  		":Mw": self.cmd_pulseW,  \
  		":Mn": self.cmd_pulseN,  \
  		":Ms": self.cmd_pulseS,  \
  		":CM": self.cmd_dummy
		}
		self.targetRA=0		
		self.targetDEC=0	
		self.RA=0		
		self.DEC=0
		self.RUN=True
		self.slewing=False
		self.setObserver()
		self.pulseStep=ephem.degrees('00:00:01')
		v=ephem.degrees('5:00:00')
		a=ephem.degrees('01:00:00')
		self.m=ramps.mount(a,v)
		self.run()	

	def setObserver(self):
		here = ephem.Observer()
		here.lat="00:00:00"
		here.lon="00:00:00"
		here.horizon="00:00:00"
		here.elev = 700
		here.temp = 25e0
		here.compute_pressure()
		self.observer=here

    	def end(self):
        	print "conductor ending.."
		self.RUN=False
		self.m.end()

		
	@threaded
	def run(self):
		print "Starting motors."
	  	while self.RUN:
			self.observer.date=ephem.now()
			sideral=self.observer.sidereal_time()
			nowRA=ephem.hours(self.targetRA-sideral).norm
			if nowRA==ephem.hours("24:00:00"):
				nowRA=ephem.hours("00:00:00")
			if self.slewing:
				#print "Slew:",self.targetRA,self.targetDEC
				self.m.slew(nowRA,self.targetDEC)
			if False:
				vRA=ephem.hours("00:00:01")
				vDEC=ephem.degrees("00:00:15")
				#print "Track:",vRA
				self.m.axis1.track(vRA)
				self.m.axis2.track(vDEC)
			time.sleep(0.25)
			ra=ephem.hours(self.m.axis1.beta).norm
			if ra==ephem.hours("24:00:00"):
				ra=ephem.hours("00:00:00")
			self.RA=ra
			self.DEC=ephem.degrees(self.m.axis2.beta).znorm


		self.end()
		print "MOTORS STOPPED"



	def cmd(self,cmd):
		print cmd
                for c in self.CMDs.keys():
			l=len(c)
			if (cmd[:l]==c):
				arg=cmd[l:].strip()
				#print "K",c,"KK",cmd,"KKK",arg
				return self.CMDs[c](arg)
				break

		return self.cmd_dummy(cmd)



	def cmd_dummy(self,arg):
		return arg,"#"

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
		return self.targetRA

	def cmd_getTargetDEC(self,arg):
		return self.targetDEC

	def cmd_setTargetRA(self,arg):
		self.targetRA=ephem.hours(arg)
		return 1

	def cmd_slew(self,arg):
		self.slewing=True
		return 0

	def cmd_stopSlew(self,arg):
		self.slewing=False
		self.m.slew(self.RA,self.DEC)
		return 
		
	def cmd_setTargetDEC(self,arg):
		arg=arg.replace('*',':')
		arg=arg.replace('’',':')
		self.targetDEC=ephem.degrees(arg)
		print arg,self.targetDEC
		return 1

	def cmd_getTelescopeRA(self,arg):
		data=str(self.RA)
		H,M,S=data.split(':')
		H=int(H)
		M=int(M)
		S=round(float(S))
		#d=data[:data.index(".")]
		d="%02d:%02d:%02d"  % (H,M,S)
		return d+'#'

	def cmd_getTelescopeDEC(self,arg):
		data=str(self.DEC)
		D,M,S=data.split(':')
		D=int(D)
		M=int(M)
		S=round(float(S))
		#print D,M,S 
		d="%+03d*%02d:%02d"  % (D,M,S)
		#d="%+03d*%02d"  % (D,M)
		return d+'#'

    	def cmd_pulseE(self,arg):
		self.targetRA=self.targetRA+self.pulseStep

    	def cmd_pulseW(self,arg):
		self.targetRA=self.targetRA-self.pulseStep

    	def cmd_pulseN(self,arg):
		self.targetDEC=self.targetDEC+self.pulseStep

    	def cmd_pulseS(self,arg):
		self.targetDEC=self.targetDEC-self.pulseStep

	def cmd_setMaxSlewRate(self,arg):
		return

if __name__ == '__main__':
	c=lx200conductor()
	c.cmd(':CM')
	c.cmd(':info')

'''
  		":GVN": self.cmd_firware_number,  \
  		":GVP": self.cmd_firware_product,  \
  		":GVT": self.cmd_firware_time,  \

  		":GM": self.cmd_getSite1Name,  \
  		":Sa": self.cmd_dummy,  \
  		":Sz": self.cmd_dummy,  \

  		":Sg": self.cmd_setSiteLongitude,  \
  		":St": self.cmd_setSiteLatitude,  \
  		":SL": self.cmd_setLocalTime,  \
  		":SC": self.cmd_setLocalDate,  \
  		":SG": self.cmd_dummy,  \
  		":GA": self.cmd_dummy,  \
  		":GZ": self.cmd_dummy,  \



  		":Gg": self.cmd_getSiteLongitude,  \
  		":Gt": self.cmd_getSiteLatitude,  \
  		":Gc": self.cmd_getClockFormat,  \


  		":GG": self.cmd_dummy,  \
  		":MA": self.cmd_dummy,  \
  		":Me": self.cmd_dummy,  \
  		":Mn": self.cmd_dummy,  \
  		":Ms": self.cmd_dummy,  \
  		":Mw": self.cmd_dummy,  \
  		":MS": self.cmd_slew,  \
  		":Q": self.cmd_abortMotion,  \

'''
